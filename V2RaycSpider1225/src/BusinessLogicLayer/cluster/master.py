__all__ = ['ActionMasterGeneral']

import random
import time
from datetime import datetime, timedelta
from os.path import join
from string import printable
from urllib.parse import urlparse

from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import HTTPError

from src.BusinessCentralLayer.middleware.subscribe_io import FlexibleDistribute
from src.BusinessCentralLayer.setting import CHROMEDRIVER_PATH, TIME_ZONE_CN, SERVER_DIR_CACHE_BGPIC, logger
from ..plugins.armour import GeeTestAdapter
from ..plugins.armour import get_header


class BaseAction:
    """针对SSPanel-Uim机场的基准行为"""

    def __init__(self, silence=None, assault=None, beat_sync=True, debug=None,
                 action_name=None, email_class=None, life_cycle=None, anti_slider=None,
                 chromedriver_path=None):
        """
        设定登陆选项，初始化登陆器
        :param silence: chromedriver静默启动；linux 环境下必须启用
        :param assault: 目标是否有反爬虫措施；默认为True BaseAction将根据目标是否具备反爬虫措施做出不同的行为
        :param beat_sync: 节拍同步。当前业务场景下必须开启，否则采集器将工作在高位环境中
        :param debug: linux环境中部署必须关闭debug模式
        :param action_name: 任务标签
        :param email_class: register页面显示的默认邮箱；常见为 @qq.com or @gmail.com
        :param life_cycle: 会员试用时长 trail time；
        :param anti_slider: 目标站点是否具备极验（GeeTest）滑动验证
        """
        # =====================================
        # Parametric Cleaning
        # =====================================
        silence = True if silence is None else silence
        assault = True if assault is None else assault
        beat_sync = beat_sync if beat_sync else True
        debug = False if debug is None else debug
        action_name = "BaseAction" if action_name is None else action_name
        email_class = "@qq.com" if email_class is None else email_class
        life_cycle = 1 if life_cycle is None else life_cycle
        anti_slider = True if anti_slider is None else anti_slider
        chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path
        # =====================================
        # driver setting
        # =====================================
        # 初始化浏览器
        self.silence, self.assault = silence, assault
        self.chromedriver_path = chromedriver_path
        # 调试模式
        self.debug = debug
        # =====================================
        # signs_information
        # =====================================
        self.username, self.password, self.email = self.generate_account(email_class=email_class)
        self.subscribe = ''
        self.register_url = ''
        self.life_cycle = life_cycle
        self.beat_sync = beat_sync
        self.action_name = action_name
        self.anti_slider = anti_slider
        # =====================================
        # v-5.4.r 添加功能：I/O任务超时设置
        # =====================================
        # 作业开始时间点
        self.work_clock_global = time.time()
        self.work_clock_utils = self.work_clock_global
        # 处理反爬虫作业的生命周期(秒) 陷入僵局后实体将自我销毁
        self.work_clock_max_wait = 120
        # 等待注册时的容错时间
        self.timeout_retry_time = 3

    def utils_slider(self, api):
        """
        实现极验（GeeTest）滑动验证的插件接口
        :param api:
        :return:
        """
        # 生成缓存路径
        full_bg_path = join(SERVER_DIR_CACHE_BGPIC, f'fbg_{self.action_name}.{self.work_clock_utils}.png')
        bg_path = join(SERVER_DIR_CACHE_BGPIC, f'bg_{self.action_name}.{self.work_clock_utils}.png')
        try:
            # 更新作业时间
            self.work_clock_utils = time.time()
            # 调用滑块验证模块
            # 通过分流器自适应调度gt2和gt3代码
            work_success = GeeTestAdapter(
                driver=api,
                debug=self.debug,
                business_name=self.action_name,
                full_img_path=full_bg_path,
                notch_img_path=bg_path
            ).run()
            # 执行成功
            if work_success:
                return True
            return False
        # 网络不给力 刷新当前网页
        except WebDriverException:
            return False
        finally:
            # 更新作业时间
            self.work_clock_utils = time.time()

    def _is_timeout(self):
        """任务超时简易判断"""
        # True：当前任务超时 False：当前任务未超时
        if self.work_clock_utils - self.work_clock_global > self.work_clock_max_wait:
            return True
        return False

    @staticmethod
    def generate_account(email_class: str = '@qq.com') -> tuple:
        """
        账号生成器
        :param email_class: @qq.com @gmail.com ...
        :return:
        """
        # 账号信息
        username = ''.join([random.choice(printable[:printable.index('!')]) for _ in range(9)])
        password = ''.join([random.choice(printable[:printable.index(' ')]) for _ in range(15)])
        email = username + email_class

        return username, password, email

    @staticmethod
    def generate_life_cycle(trial_time: int) -> str:
        """
        计算订阅的自然销毁时间 ---> end_life = Shanghai_nowTime + trialTime
        :param trial_time: 机场VIP时长（试用时间）
        :return: subscribe失效时间
        """
        return str(datetime.now(TIME_ZONE_CN) + timedelta(days=trial_time)).split('.')[0]

    def set_spider_option(self, header=None) -> Chrome:
        """

        :param header:
        :return:
        """
        # 实例化Chrome可选参数
        options = ChromeOptions()
        # 最高权限运行
        options.add_argument('--no-sandbox')
        # 隐身模式
        options.add_argument('-incognito')
        # 无缓存加载
        options.add_argument('--disk-cache-')
        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')
        # 禁用 DevTools listening
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        # 更换头部
        if header:
            options.add_argument(f"user-agent={header}")
        else:
            options.add_argument(f'user-agent={get_header()}')
        # 静默启动
        if self.silence is True:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument("--disable-software-rasterizer")
        # 抑制自动化控制特征
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 加速模式，增加Selenium渲染效率
        if self.assault:
            chrome_pref = {"profile.default_content_settings": {"Images": 2, 'javascript': 2},
                           "profile.managed_default_content_settings": {"Images": 2}}
            options.experimental_options['prefs'] = chrome_pref
            d_c = DesiredCapabilities.CHROME
            d_c['pageLoadStrategy'] = 'none'
            _api = Chrome(
                options=options,
                executable_path=self.chromedriver_path,
                desired_capabilities=d_c
            )
        else:
            _api = Chrome(options=options, executable_path=self.chromedriver_path)
        # 进一步消除操作指令头，增加隐蔽性
        _api.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        return _api

    @staticmethod
    def get_html_handle(api: Chrome, url, wait_seconds: int = 15):
        api.set_page_load_timeout(time_to_wait=wait_seconds)
        api.get(url)

    def sign_in(self, api: Chrome, email=None, password=None):
        """登录行为"""
        email = self.email if email is None else email
        password = self.password if password is None else password
        self.wait(api, timeout=5, tag_xpath_str="//button")

        api.find_element_by_id("email").send_keys(email)
        api.find_element_by_id("password").send_keys(password)
        api.find_element_by_tag_name("button").click()
        try:
            api.find_element_by_xpath("//h2[@id='swal2-title']")
            logger.error("FAILED Incorrect account or password.")
        except NoSuchElementException:
            pass

    def sign_up(self, api: Chrome):
        """
        注册行为
        @param api:
        @return:
        """
        # 任务超时则弹出协程句柄 终止任务进行
        while True:
            # ======================================
            # 紧急制动，本次行为释放宣告失败，拉闸撤退！！
            # ======================================
            # 若任务超时 主动抛出异常
            if self._is_timeout():
                raise TimeoutException

            # ======================================
            # 填充注册数据
            # ======================================
            time.sleep(0.5)

            WebDriverWait(api, 20) \
                .until(expected_conditions.presence_of_element_located((By.ID, 'name'))) \
                .send_keys(self.username)

            api.find_element_by_id('email').send_keys(self.email)

            api.find_element_by_id('passwd').send_keys(self.password)

            api.find_element_by_id('repasswd').send_keys(self.password)

            time.sleep(1)

            # ======================================
            # 依据实体抽象特征，选择相应的解决方案
            # ======================================
            # 滑动验证 TODO 引入STAFF API 自适应识别参数
            if self.anti_slider:
                # 打开工具箱
                response = self.utils_slider(api=api)
                # 执行失败刷新页面并重试N次
                if not response:
                    self.work_clock_utils = time.time()
                    api.refresh()
                    continue

            # ======================================
            # 提交注册数据，完成注册任务
            # ======================================
            # 点击注册按键
            api.find_element_by_id('register-confirm').click()
            # 重试N轮 等待[注册成功]界面的加载
            for x in range(3):
                try:
                    time.sleep(1.5)
                    api.find_element_by_xpath("//button[contains(@class,'confirm')]").click()
                    return True
                except NoSuchElementException:
                    logger.debug(f'[{x + 1} / 3]{self.action_name}验证超时，{self.timeout_retry_time}s后重试')
                    time.sleep(self.timeout_retry_time)
                    continue

    @staticmethod
    def wait(api: Chrome, timeout: float, tag_xpath_str):
        if tag_xpath_str == 'all':
            time.sleep(1)
            WebDriverWait(api, timeout).until(expected_conditions.presence_of_all_elements_located)
        else:
            WebDriverWait(api, timeout).until(expected_conditions.presence_of_element_located((
                By.XPATH, tag_xpath_str
            )))

    def check_in(self, button_xpath_str: str):
        """
        机场账号每日签到
        该功能收益较低，加入主工作流会降低系统运行效率，仅在编写特种脚本时引用
        :param button_xpath_str:
        :return:
        """

    def load_any_subscribe(self, api: Chrome, element_xpath_str: str, href_xpath_str: str, class_: str, retry=0):
        """
        捕获订阅并送入持久化数据池
        @param api: ChromeDriverObject
        @param element_xpath_str: 用于定位链接所在的标签
        @param href_xpath_str: 用于取出目标标签的属性值，既subscribe
        @param class_: 该subscribe类型，如`ssr`/`v2ray`/`trojan`
        @param retry: 失败重试
        @todo 使用 retrying 模块替代retry参数实现的功能（引入断网重连，断言重试，行为回滚...）
        @return:
        """
        self.subscribe = WebDriverWait(api, 30).until(expected_conditions.presence_of_element_located((
            By.XPATH,
            element_xpath_str
        ))).get_attribute(href_xpath_str)

        # 若对象可捕捉则解析数据并持久化数据
        if self.subscribe:
            # 失败重试3次
            for _ in range(3):
                # ['domain', 'subs', 'class_', 'end_life', 'res_time', 'passable','username', 'password', 'email']
                try:
                    # 机场域名
                    domain = urlparse(self.register_url).netloc
                    # 采集时间
                    res_time = str(datetime.now(TIME_ZONE_CN)).split('.')[0]
                    # 链接可用，默认为true
                    passable = 'true'
                    # 信息键
                    docker = [domain, self.subscribe, class_, self.generate_life_cycle(self.life_cycle), res_time,
                              passable, self.username,
                              self.password, self.email]
                    # 根据不同的beat_sync形式持久化数据
                    FlexibleDistribute(docker=docker, beat_sync=self.beat_sync)
                    # 数据存储成功后结束循环
                    logger.success(">> GET <{}> --> [{}] {}".format(self.action_name, class_, self.subscribe))
                    # TODO ADD v5.1.0更新特性，记录机场域名-订阅域名映射缓存
                    # set_task2url_cache(task_name=self.__class__.__name__, register_url=self.register_url,
                    #                    subs=self.subscribe)
                    break
                except Exception as e:
                    logger.debug(">> FAILED <{}> --> {}:{}".format(self.action_name, class_, e))
                    time.sleep(1)
                    continue
            # 若没有成功存储，返回None
            else:
                return None
        # 否则调入健壮工程
        # TODO 判断异常原因，构建解决方案，若无可靠解决方案，确保该任务安全退出
        else:
            if retry >= 3:
                raise TimeoutException
            retry += 1
            self.load_any_subscribe(api, element_xpath_str, href_xpath_str, class_, retry)

    def run(self):
        """Please rewrite this function!"""

        # Get register url

        # Locate register tag and send keys

        # Click the submit button

        # * Shut down the sAirPort TOS pop-us

        # * Jump to the login page
        # ** Locate sign in tag and send keys
        # ** Click the sign in button

        # To the sAirPort homepage

        # Wait for page elements to load

        # Get the subscribe link of ssr/trojan/v2ray

        # Save subscribe link and refresh redis task list

        # Close Chrome driver and release memory


class ActionMasterGeneral(BaseAction):

    def __init__(self, register_url: str = None,
                 silence: bool = True, assault: bool = False, beat_sync: bool = True,
                 email: str = None, life_cycle: int = None, anti_slider: bool = False,
                 hyper_params: dict = None, action_name: str = None, debug: bool = False,
                 chromedriver_path=CHROMEDRIVER_PATH):
        """

        @param register_url: 机场注册网址，STAFF原生register接口
        @param silence: 静默启动；为True时静默访问<linux 必须启用>
        @param anti_slider: 目标是否有反爬虫措施；默认为True BaseAction将根据目标是否具备反爬虫措施做出不同的行为
        @param email: register页面显示的默认邮箱；常见为 @qq.com or @gmail.com
        @param life_cycle: 会员试用时长 trail time；
        @param hyper_params: 模型超级参数
        """
        super(ActionMasterGeneral, self).__init__(silence=silence, assault=assault, beat_sync=beat_sync,
                                                  email_class=email, life_cycle=life_cycle, anti_slider=anti_slider,
                                                  debug=debug, chromedriver_path=chromedriver_path)
        # 任务标记
        self.action_name = "ActionMasterGeneral" if action_name is None else action_name
        # 机场注册网址
        self.register_url = register_url
        # 定义模型超级参数
        self.hyper_params = {
            'v2ray': True,
            'ssr': True,
            'trojan': False,
            # Shadowrocket
            'rocket': False,
            # Quantumult
            'qtl': False,
            # Kitsunebi
            'kit': False,
            # usr_email True: 需要自己输入邮箱后缀(默认为qq)
            # usr_email False: 邮箱后缀为选择形式只需填写主段
            'usr_email': False,
        }
        # 更新模型超参数
        if hyper_params:
            self.hyper_params.update(hyper_params)
        # 只需填写主段则邮箱名=用户名
        if not self.hyper_params['usr_email']:
            self.email = self.username

    def capture_subscribe(self, api):
        if self.hyper_params['v2ray']:
            self.load_any_subscribe(
                api,
                "//div[@class='buttons']//a[contains(@class,'v2ray')]",
                'data-clipboard-text',
                'v2ray'
            )
        elif self.hyper_params['ssr']:
            self.load_any_subscribe(
                api,
                """//a[@onclick="importSublink('ssr')"]/..//a[contains(@class,'copy')]""",
                'data-clipboard-text',
                'ssr'
            )
        # elif self.hyper_params['trojan']: ...
        # elif self.hyper_params['kit']: ...
        # elif self.hyper_params['qtl']: ...

    def run(self, api=None):
        logger.debug(f">> RUN <{self.action_name}> --> beat_sync[{self.beat_sync}] feature[General]")
        # 获取任务设置
        api = self.set_spider_option() if api is None else api
        # 执行核心业务逻辑
        try:
            # 设置弹性计时器，当目标站点未能在规定时间内渲染到预期范围时自主销毁实体
            # 防止云彩姬误陷“战局”被站长过肩摔
            self.get_html_handle(api=api, url=self.register_url, wait_seconds=45)
            # 注册账号
            self.sign_up(api)
            # 进入站点并等待核心元素渲染完成
            self.wait(api, 40, "//div[@class='card-body']")
            # 根据原子类型订阅的优先顺序 依次捕获
            self.capture_subscribe(api)
        except TimeoutException:
            logger.error(f'>>> TimeoutException <{self.action_name}> -- {self.register_url}')
        except WebDriverException as e:
            logger.error(f">>> WebDriverException <{self.action_name}> -- {e}")
        except (HTTPError, ConnectionRefusedError, ConnectionResetError):
            pass
        except Exception as e:
            logger.warning(f">>> Exception <{self.action_name}> -- {e}")
        finally:
            api.quit()


class AdaptiveCapture(BaseAction):
    def __init__(self, url, chromedriver_path):
        super(AdaptiveCapture, self).__init__()
        self.register_url = url
        self.chromedriver_path = chromedriver_path

    @staticmethod
    def url_clearing(unknown_hosts: str) -> str:
        if not isinstance(unknown_hosts, str):
            raise TypeError
        url = unknown_hosts.strip()
        if url.endswith("/auth/register") and url.startswith("https://"):
            return url
        if url.endswith("/auth/register") and not url.startswith("https://"):
            return f"https://{url}"
        if not url.endswith("auth/register") and url.startswith("https://"):
            return f"{url}/auth/register"
        if not (url.endswith("auth/register") and url.startswith("https://")):
            return f"https://{url}/auth/register"

    @staticmethod
    def handle_html(url, cache_source_page=False):
        import requests
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                 " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67"}
        res = requests.get(url, headers=headers, timeout=5)
        if cache_source_page:
            with open("cache_source_code.txt", 'w', encoding="utf8") as f:
                f.write(res.text)
        if res.status_code == 200:
            return res
        res.raise_for_status()

    def get_type_of_anti_tool(self, url) -> dict:
        from bs4 import BeautifulSoup

        report = {"url": url, "is_sspanel": None, "type": None}
        response = self.handle_html(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        if not soup.find_all('input'):
            report.update({"type": "refuse to register"})
        elif soup.find_all("button", id='emil_verify') or soup.find_all("button", id="send-code"):
            report.update({"type": "email"})
        elif "已经有账号了" in response.text:
            if ("geetest" in response.text) and ("滑动" in response.text):
                report.update({"type": "geetest-crack"})
            else:
                report.update({"type": "normal"})
        else:
            report.update({"type": "unknown"})

        return report

    def identity_register_elements_by_request(self, url):
        """

        :param url:
        :return:
        """
        # from bs4 import BeautifulSoup
        # elements = {"username": "", "email": "", "password": "", "re-password": "", "button": ""}
        # response = self.handle_html(url)

    def run(self, silence=None, assault=None):
        self.silence = True if silence is None else silence
        self.assault = True if assault is None else assault
        # 书写自适应流程

        # Input：unknown type url
        #  01.Input register --> return register
        #  02.Input host  --> return https://host/auth/register
        #  03.Input other --> return False
        self.register_url = self.url_clearing(self.register_url)

        # Input: register
        #  01.识别反爬虫方案
        #       - geetest crack v3
        #       - geetest crack v2
        #       - google reCAPTCHA
        #       - email
        #       - not exist
        #       - unknown
        report = self.get_type_of_anti_tool(self.register_url)
        anti_type = report['type']

        #  02.识别注册机
        #       - [elementId]email
        #       - [elementId]password
        #       - [elementId]username
        #       - [elementId]button
        if not report['is_sspanel']:
            self.identity_register_elements_by_request(self.register_url)
        #  03.更新参数
        if anti_type == 'crack':
            self.anti_slider = True
        else:
            self.anti_slider = False
        self.email = self.username
        #  04.生成注册机
        api = self.set_spider_option()
        #  05.执行注册机
        try:
            self.get_html_handle(api, self.register_url, 25)
            self.sign_up(api)
            input()
        finally:
            api.quit()
        #  06.执行解析器
        #  07.缓存数据
        #       - email,password,parser-response,job-time,work-time,cookies
        #       - subscribe: desc mapping
        # Output: cache data
