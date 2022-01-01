# -*- coding: utf-8 -*-
# Time       : 2021/12/21 23:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 天球交汇
import os.path
import random
import time
from string import printable

from cloudscraper import create_scraper
from requests.exceptions import (
    SSLError,
    HTTPError,
    ConnectionError,
    Timeout,
    RequestException
)
from selenium.common.exceptions import (
    SessionNotCreatedException,
    WebDriverException,
    TimeoutException
)
from selenium.webdriver import Chrome, ChromeOptions

from services.middleware.subscribe_io import SubscribeManager
from services.settings import (
    logger, DIR_CACHE_IMAGE, DIR_CACHE_AUDIO
)
from services.utils import (
    GeeTestAdapter, ToolBox, apis_get_email_context, apis_get_verification_code,
    activate_recaptcha, handle_audio, parse_audio, submit_recaptcha
)
from services.utils.armor.anti_email.exceptions import GetEmailTimeout,GetEmailCodeTimeout


class ArmorUtils:
    def __init__(
            self, beat_dance: int = None, action_name: str = None,

    ):
        self.beat_dance = 0 if beat_dance is None else beat_dance
        self.action_name = "ArmorUtils" if action_name is None else action_name

        # 邮箱验证上下文缓存数据
        self.context_anti_email = {}
        # 声纹验证音频转文本的输出
        self.audio_answer = ""

    def anti_email(self, api: Chrome, method="email") -> str:
        if method == "email":
            try:
                self.context_anti_email = apis_get_email_context(
                    api=api,
                    main_handle=api.current_window_handle,
                )
                return self.context_anti_email["email"]
            except TimeoutException:
                raise GetEmailTimeout
        if method == "code":
            try:
                # 切换标签页监听验证码
                email_code = apis_get_verification_code(
                    api=api,
                    link=self.context_anti_email["link"],
                    main_handle=api.current_window_handle,
                    collaborate_tab=self.context_anti_email["handle"],
                )
                return email_code
            except TimeoutException:
                raise GetEmailCodeTimeout

    def anti_slider(self, api: Chrome):
        path_bg_full = os.path.join(DIR_CACHE_IMAGE, f"full_{self.action_name}.{int(time.time())}.png")
        path_bg_notch = os.path.join(DIR_CACHE_IMAGE, f"notch_{self.action_name}.{int(time.time())}.png")

        time.sleep(1)
        try:
            ok = GeeTestAdapter(
                driver=api,
                business_name=self.action_name,
                full_img_path=path_bg_full,
                notch_img_path=path_bg_notch,
            ).run()
            return ok
        except WebDriverException:
            return False

    def anti_recaptcha(self, api):
        """
                处理 SSPanel 中的 Google reCAPTCHA v2 Checkbox 人机验证。

                使用音频声纹识别验证而非直面图像识别。

                > 无论站点本身可否直连访问，本模块的执行过程的流量必须过墙，否则音频文件的下载及转码必然报错。
                > 可能的异常有:
                 - speech_recognition.RequestError
                 - http.client.IncompleteRead

                :param api:
                :return:
                """

        """
        TODO [√]激活 reCAPTCHA 并获取音频文件下载链接
        ------------------------------------------------------
        """
        audio_url: str = activate_recaptcha(api)

        # Google reCAPTCHA 风控
        if not audio_url:
            logger.error("运行实例已被风控。\n"
                         "可能原因及相关建议如下：\n"
                         "1.目标站点可能正在遭受流量攻击，请更换测试用例；\n"
                         "2.代理IP可能已被风控，建议关闭代理运行或更换代理节点；\n"
                         "3.本机设备所在网络正在传输恶意流量，建议切换网络如切换WLAN。\n"
                         ">>> https://developers.google.com/recaptcha/docs/faq#"
                         "my-computer-or-network-may-be-sending-automated-queries")
            raise WebDriverException

        """
        TODO [√]音频转码 （MP3 --> WAV） 增加识别精度
        ------------------------------------------------------
        """
        path_audio_wav: str = handle_audio(
            audio_url=audio_url,
            dir_audio_cache=DIR_CACHE_AUDIO
        )
        # logger.success("Handle Audio - path_audio_wav=`{}`".format(path_audio_wav))

        """
        TODO [√]声纹识别 --(output)--> 文本数据
        ------------------------------------------------------
        # speech_recognition.RequestError 需要挂起代理
        # http.client.IncompleteRead 网速不佳，音频文件未下载完整就开始解析
        """
        self.audio_answer: str = parse_audio(path_audio_wav)
        # logger.success("Parse Audio - answer=`{}`".format(self.audio_answer))

        """
        TODO [√] 定位输入框并填写文本数据
        ------------------------------------------------------
        # speech_recognition.RequestError 需要挂起代理
        # http.client.IncompleteRead 网速不佳，音频文件未下载完整就开始解析
        """
        response = submit_recaptcha(api, answer=self.audio_answer)
        if not response:
            logger.error("Submit reCAPTCHA answer.")
            raise TimeoutException


class TheElderBlood:

    def __init__(
            self,
            atomic: dict,
            chromedriver_path: str = None,
            silence: bool = None,
    ):
        """

        :param atomic:
        :param chromedriver_path:
        :param silence:
        """
        """
        TODO [√]驱动参数
        ---------------------
        """
        self.chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path
        self.silence = True if silence is None else silence

        """
        TODO [√]Atomic原子实例
        ---------------------
        hyper_params    |原子实例超级参数
        beat_dance      |集群节拍超级参数
        """
        self.atomic: dict = atomic

        # 默认参数
        self.register_url = self.atomic["register_url"]
        self.action_name = self.atomic.get("name", "BaseAction")
        self.life_cycle = self.atomic.get("life_cycle", 24)
        self.email_domain = self.atomic.get("email_domain", "@gmail.com")
        self.username, self.password, self.email = "", "", ""

        # 超级参数
        self.hyper_params = {
            # 注册阶段
            "usr_email": False,
            "synergy": False,
            "tos": False,
            # 对抗阶段
            "anti_email": False,
            "anti_recaptcha": False,
            "anti_slider": False,
            "anti_cloudflare": False,
            # 延拓阶段
            "prism": False,
            "aff": 0,
            # 缓存阶段
            "threshold": 3,
        }
        self.hyper_params.update(self.atomic.get("hyper_params", {}))
        self.beat_dance = self.hyper_params.get("beat_dance", 0)
        self.tos = bool(self.hyper_params["tos"])
        self.usr_email = bool(self.hyper_params["usr_email"])
        self.aff = self.hyper_params.get("aff", 0)
        self.synergy = bool(self.hyper_params.get("synergy"))
        self.prism = bool(self.hyper_params["prism"])
        self.anti_email = bool(self.hyper_params["anti_email"])
        self.anti_recaptcha = bool(self.hyper_params["anti_recaptcha"])
        self.anti_slider = bool(self.hyper_params["anti_slider"])
        self.anti_cloudflare = bool(self.hyper_params["anti_cloudflare"])
        self.threshold = self.hyper_params["threshold"]

        self.context_anti_email = {}
        """
        TODO [√]平台对象参数
        ---------------------
        """
        self.subscribe_url = ""

        """
        TODO [√]驱动超级参数
        ---------------------
        """
        # 任务超时后实体自我销毁
        self.work_clock_global = time.time()
        self.work_clock_utils = self.work_clock_global
        # 最大容灾阈值 单位秒
        self.work_clock_max_wait = 230 if self.anti_email else 120

        """
        TODO [√]模组依赖
        ---------------------
        """
        self.armor = ArmorUtils(beat_dance=self.beat_dance)

    def _is_timeout(self):
        if self.work_clock_utils - self.work_clock_global > self.work_clock_max_wait:
            return True
        return False

    def _update_clock(self):
        self.work_clock_utils = time.time()

    def waiting_to_load(self, api):
        """
        register --> dashboard

        :param api:
        :return:
        """
        raise ImportError

    def set_chrome_options(self):
        options = ChromeOptions()
        options.add_argument("user-agent='{}'".format(ToolBox.fake_user_agent()))

        # 无头启动禁用GPU渲染
        if self.silence is True:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")

        # 滑块验证需要加载图片
        if not self.anti_slider:
            options.add_argument("blink-settings=imagesEnabled=false")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--no-sandbox')
        options.add_argument("--lang=zh-CN")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-javascript')
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        try:
            return Chrome(options=options, executable_path=self.chromedriver_path)
        except SessionNotCreatedException as e:
            logger.critical(
                f"<{self.action_name}> 任務核心無法啓動：ChromeDriver 與 Chrome 版本不匹配。 "
                f"請審核您的 Chrome 版本號并於 http://npm.taobao.org/mirrors/chromedriver/ 拉取對應的驅動鏡像"
                f"-- {e}"
            )
        except (PermissionError, WebDriverException):
            logger.critical("The `chromedriver` executable may have wrong permissions.")

    def generate_account(self, api):
        username = "".join(
            [random.choice(printable[: printable.index("!")]) for _ in range(9)]
        )
        password = "".join(
            [random.choice(printable[: printable.index(" ")]) for _ in range(15)]
        )

        if not self.anti_email:
            if not self.usr_email:
                email = username
            else:
                email = username + self.email_domain
        else:
            email = self.armor.anti_email(api, method="email")
        return username, password, email

    def sign_in(self):
        pass

    def sign_up(self, api: Chrome):
        """

        :param api:
        :return:
        """
        raise ImportError

    def buy_free_plan(self, api, force_draw: int = 2):
        """

        :param api:
        :param force_draw:
        :return:
        """
        raise ImportError

    def get_aff_link(self, api: Chrome) -> str:
        """

        :param api:
        :return:
        """
        raise ImportError

    def check_in(self):
        pass

    @staticmethod
    def get_html_handle(api: Chrome, url, timeout: float = 45):
        """

        :param api:
        :param url:
        :param timeout:
        :return:
        """
        raise ImportError

    def check_heartbeat(self, debug: bool = False):
        ToolBox.runtime_report(self.action_name, motive="CHECK")

        url = self.register_url
        scraper = create_scraper()
        try:
            response = scraper.get(url, timeout=5)
        except (SSLError, HTTPError):
            if debug:
                logger.warning(f">> Block <{self.action_name}> Need to use a proxy to access the site "
                               f"url={url}")
            return True
        except ConnectionError as e:
            logger.warning(f">> Block <{self.action_name}> ConnectionError "
                           f"url={url} error={e}")
            return False
        except Timeout as e:
            logger.warning(f">> Block <{self.action_name}> ResponseTimeout "
                           f"url={url} error={e}")
            return False
        except RequestException as e:
            logger.warning(f">> Block <{self.action_name}> RequestException "
                           f"url={url} error={e}")
            return False
        else:
            if response.status_code > 400:
                logger.error(f">> Block <{self.action_name}> InstanceStatusException "
                             f"status_code={response.status_code} url={url}")
                return False
            return True

    def get_subscribe(self, api: Chrome):
        """
        获取订阅

        引入健壮工程 + 手动标注数据集，大幅度增强模型的泛化能力
        :param api:
        :return:
        """
        raise ImportError

    def cache_subscribe(self, sm: SubscribeManager = None):
        if self.subscribe_url == "":
            return

        sm = SubscribeManager() if sm is None else sm

        # 缓存订阅链接
        sm.add(
            subscribe=self.subscribe_url,
            life_cycle=self.life_cycle,
            threshold=self.threshold
        )

        # 更新别名映射
        sm.set_alias(
            alias=self.action_name,
            netloc=ToolBox.reset_url(
                url=self.subscribe_url,
                get_domain=True
            )
        )

        logger.success(ToolBox.runtime_report(
            action_name=self.action_name,
            motive="STORE",
            subscribe_url=self.subscribe_url
        ))
