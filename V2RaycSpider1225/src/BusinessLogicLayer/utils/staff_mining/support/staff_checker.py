import os
import time
import warnings
from urllib.parse import urlparse

import gevent
import requests
from bs4 import BeautifulSoup
from gevent.queue import Queue

from ..common.exceptions import NoSuchElementException
from ..support.staff_collector import StaffCollector


class StaffChecker:
    def __init__(self, task_docker, work_q: Queue = None, output_dir: str = None, power: int = 16, debug: bool = False,
                 work_name: str = 'classify_urls'):
        # 任务容器：queue
        self.work_q = work_q if work_q else Queue()
        # 任务容器：迭代器
        self.task_docker = task_docker
        # 协程数
        self.power = power
        # 是否打印日志信息
        self.debug_logger = debug
        # 任务队列满载时刻长度
        self.max_queue_size = 0
        # 业务名
        self.work_name = work_name
        # 急救箱，用于搭配self._doctor模块实现任务重载/抢救
        self._first_aid_kit = {}
        # 运行模式
        self.debug = debug
        # 初始化生产路径
        _classifier_dir = output_dir if output_dir else os.path.dirname(__file__)
        self._path_cls_verity_email = os.path.join(_classifier_dir, "verity_email.txt")
        self._path_cls_verity_sms = os.path.join(_classifier_dir, "verity_sms.txt")
        self._path_cls_others = os.path.join(_classifier_dir, "other_arch.txt")
        self._path_cls_staff_arch_slider = os.path.join(_classifier_dir, "staff_arch_slider.txt")
        self._path_cls_staff_arch_general = os.path.join(_classifier_dir, "staff_arch_general.txt")
        self._path_cls_staff_arch_inc = os.path.join(_classifier_dir, "staff_arch_inc.txt")
        # 用于进一步清洗reCAPTCHA的缓存容器
        self.queue_staff_arch_pending = []

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def classify_urls(self, url: str):
        """

        :param url:
        :return:
        """
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                 " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67"}
        proxies = {"http": None, "https": None}
        # 剔除不安全站点
        if not url.startswith("https"):
            return True
        try:
            # res = requests.get(url, headers=headers, timeout=20)
            res = requests.get(url, headers=headers, timeout=20, proxies=proxies)
            soup = BeautifulSoup(res.text, 'html.parser')

            # ====================================================
            # Function: filter_live_urls
            # ====================================================
            # 剔除异常站点
            if res.status_code != 200:
                return True
            # ====================================================
            # Function: filter_std_urls
            # ====================================================
            # 剔除拒绝注册的源
            if not soup.find_all("input"):
                return True
            # ====================================================
            # Function: classify_urls
            # ====================================================
            # classify: 包含EMAIL邮箱验证模块的源
            if soup.find_all("button", id='email_verify') or soup.find_all("button", id="send-code"):
                with open(self._path_cls_verity_email, 'a', encoding="utf8") as f:
                    f.write(f"{url}\n")
            # classify: 包含SMS短信验证模块的源 [???]
            elif soup.find_all("button", id="send_sms_code"):
                with open(self._path_cls_verity_sms, 'a', encoding="utf8") as f:
                    f.write(f"{url}\n")
            # classify: STAFF原生架构
            elif "已经有账号了" in res.text:
                # classify: 包含geetest-slider滑动验证
                if ("geetest" in res.text) and ("滑动" in res.text):
                    with open(self._path_cls_staff_arch_slider, 'a', encoding="utf8") as f:
                        f.write(f"{url}\n")
                # classify: 无验证的STAFF ARCH
                else:
                    self.queue_staff_arch_pending.append(url)
                    if "邀请码" in res.text:
                        with open(self._path_cls_staff_arch_inc, 'a', encoding="utf8") as f:
                            f.write(f"{url}\n")
                    else:
                        with open(self._path_cls_staff_arch_general, 'a', encoding="utf8") as f:
                            f.write(f"{url}\n")
            # classify: 基于其他解决方案的源
            else:
                self.queue_staff_arch_pending.append(url)
                with open(self._path_cls_others, 'a', encoding="utf8") as f:
                    f.write(f"{url}\n")
        except requests.exceptions.RequestException:
            self._doctor(url)
        # except Exception as e:
        #     warnings.warn(f"<StaffChecker> ||{self.work_name}||{e} -> {url}")

    def go(self):
        """
        主函数
        :return:
        """
        # 任务重载
        self._offload_task()
        # 空载协程队列
        pending_queue = []
        # 配置弹性采集功率
        power_ = self.power
        if self.max_queue_size != 0:
            power_ = self.max_queue_size if power_ > self.max_queue_size else power_
        # 任务启动
        for _ in range(power_):
            task = gevent.spawn(self.launcher)
            pending_queue.append(task)
        gevent.joinall(pending_queue)

    def launcher(self):
        while not self.work_q.empty():
            url = self.work_q.get_nowait()
            self.classify_urls(url)
            print(f"loop[{self.max_queue_size - self.work_q.qsize()}/{self.max_queue_size}] --> {url}")

    # --------------------------------------------------
    # Private API
    # --------------------------------------------------

    def _offload_task(self):
        """

        @return:
        """
        if self.task_docker:
            for task in self.task_docker:
                self.work_q.put_nowait(task)
        self.max_queue_size = self.work_q.qsize()

    def _doctor(self, url):
        """
        模拟失败重试过程，一定程度上解决 因并发数过大引发的带宽拥堵HTTPPool握手异常
        - 默认重试1次
        :param url: 需要重试的链接
        :return:
        """
        if self.debug:
            # 若不在包中则初始化添加
            # 若在包中 且未达边界重试标准 则+1
            # 若在包中 且已达边界重试标准 则踢出队列
            if self._first_aid_kit.get(url):
                warnings.warn(f"<StaffChecker> ||{self.work_name}||Detach -> {url}")
            else:
                self._first_aid_kit[url] = True
                self.work_q.put_nowait(url)
        else:
            pass


class IdentifyRecaptcha(StaffChecker):
    def __init__(
            self, task_docker,
            chromedriver_path: str = None,
            output_path: str = None,
            power: int = 8,
            silence: bool = True
    ):
        super(IdentifyRecaptcha, self).__init__(task_docker=task_docker, power=power, debug=False,
                                                work_name="is_reCAPTCHA")

        # Initialize the Selenium operation handle parameters.
        self._chromedriver_path = chromedriver_path
        self._silence = silence

        # Initialize decision parameters.
        self._is_recaptcha_dict = {}
        self._retry_num = 2
        self._output_path = output_path if output_path else "./staff_arch_recaptcha.txt"
        self.power = 8 if power >= 8 else power

    def is_recaptcha(self, url):
        """
       Determine whether the target site contains reCAPTCHA man-machine verification

       Under normal circumstances, a staff site will only contain one man-machine verification scheme.

       For example, if "slider verification" appears on the target site,
       the human-machine verification of "puzzle click" will not be used.

       :param url:
       :return:
       """
        # Get Selenium operation handle.
        api = StaffCollector(
            cache_path="",
            chromedriver_path=self._chromedriver_path,
            silence=self._silence
        ).set_spider_options()
        # Start the test process.
        try:
            api.get(url)
            # Wait for it to load and set a reasonable number of retries.
            for _ in range(self._retry_num):
                try:
                    time.sleep(1)
                    is_recaptcha = "recaptcha" in api.find_element_by_xpath("//div//iframe").get_attribute("src")
                    self._is_recaptcha_dict.update({url: is_recaptcha})
                    with open(self._output_path, 'a', encoding='utf8') as f:
                        f.write(f"{url}\n")
                    break
                except NoSuchElementException:
                    time.sleep(1)
                    continue
            else:
                self._is_recaptcha_dict.update({url: False})
        finally:
            api.quit()

    def launcher(self):
        while not self.work_q.empty():
            url = self.work_q.get_nowait()
            self.is_recaptcha(url)
            print(f"loop -->{url}")


class StaffEntropyGenerator(StaffChecker):
    def __init__(
            self, task_docker,
            chromedriver_path: str = None,
            output_path: str = None,
            power: int = 8,
            silence: bool = True
    ):
        super(StaffEntropyGenerator, self).__init__(task_docker=task_docker, power=power, debug=False,
                                                    work_name="generate_entropy")

        self._output_path = output_path
        # Initialize the Selenium operation handle parameters.
        self._silence = silence
        self._chromedriver_path = chromedriver_path

    def generate_entropy(self, url):
        """

        :param url:
        :return:
        """
        # Entropy template
        _mould = {
            'name': urlparse(url).netloc.replace(".", "").title(),
            'register_url': url,
            'life_cycle': 1,
            'anti_slider': True,
            'hyper_params': {'ssr': True, "v2ray": False, 'usr_email': False},
            'email': '@gmail.com'
        }
        # Get Selenium operation handle
        api = StaffCollector(
            cache_path="",
            chromedriver_path=self._chromedriver_path,
            silence=self._silence
        ).set_spider_options()
        # Start the test process
        api.get(url)

    def launcher(self):
        while not self.work_q.empty():
            url = self.work_q.get_nowait()
            self.generate_entropy(url)
