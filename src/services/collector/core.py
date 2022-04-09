# -*- coding: utf-8 -*-
# Time       : 2021/12/21 23:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 天球交汇
import os.path
import random
import sys
import time
from string import printable
from typing import Optional

from cloudscraper import create_scraper
from requests.exceptions import (
    SSLError,
    HTTPError,
    ConnectionError,
    Timeout,
    RequestException,
)
from selenium.common.exceptions import WebDriverException, TimeoutException,InvalidSessionIdException
from selenium.webdriver import Chrome, ChromeOptions
from urllib3.exceptions import MaxRetryError
from webdriver_manager.chrome import ChromeDriverManager

from services.middleware.subscribe_io import SubscribeManager
from services.middleware.workers_io import MessageQueue
from services.settings import logger, DIR_CACHE_IMAGE, DIR_CACHE_AUDIO
from services.utils import (
    GeeTestAdapter,
    ToolBox,
    apis_get_email_context,
    apis_get_verification_code,
    activate_recaptcha,
    handle_audio,
    parse_audio,
    submit_recaptcha,
    EmailRelayV2,
    EmailRelay,
    correct_answer,
)
from services.utils.armor.anti_email.exceptions import (
    GetEmailTimeout,
    GetEmailCodeTimeout,
)
from services.utils.armor.anti_recaptcha.exceptions import (
    RiskControlSystemArmor,
    AntiBreakOffWarning,
)
from .exceptions import GetPageTimeoutException


class ArmorUtils:
    def __init__(self, beat_dance: int = None, action_name: str = None):
        self.beat_dance = 0 if beat_dance is None else beat_dance
        self.action_name = "ArmorUtils" if action_name is None else action_name

        # 邮箱验证上下文缓存数据
        self.context_anti_email = {}
        # 声纹验证音频转文本的输出
        self.audio_answer = ""

        # 服务注册
        self.register_util = {
            "anti_email": "",
            "anti_slider": None,
            "anti_recaptcha": None,
        }
        self.er_v1 = EmailRelay()
        self.er_v2 = EmailRelayV2()

    def anti_email(self, ctx: Chrome, method: str) -> str:
        """
        临时邮箱注册解决方案

        :param ctx:
        :param method:
        :return:
        """

        def v1():
            if method == "email":
                try:
                    self.context_anti_email = apis_get_email_context(
                        api=ctx, main_handle=ctx.current_window_handle
                    )
                    return self.context_anti_email["email"]
                except TimeoutException:
                    raise GetEmailTimeout
            if method == "code":
                try:
                    # 切换标签页监听验证码
                    email_code = apis_get_verification_code(
                        api=ctx,
                        link=self.context_anti_email["link"],
                        main_handle=ctx.current_window_handle,
                        collaborate_tab=self.context_anti_email["handle"],
                    )
                    return email_code
                except TimeoutException:
                    raise GetEmailCodeTimeout

        def v2():
            if method == "email":
                self.context_anti_email = self.er_v2.apis_get_temp_email(
                    api=ctx, handle_obj=ctx.current_window_handle
                )
                return self.context_anti_email["email"]
            if method == "code":
                email_code = self.er_v2.apis_get_email_code()
                return email_code

        if method not in ["email", "code"]:
            raise ValueError

        util_mapping = {"v1": v1, "v2": v2}

        if not self.register_util["anti_email"]:
            if self.er_v2.is_availability():
                self.register_util["anti_email"] = "v2"
            elif self.er_v1.is_availability():
                self.register_util["anti_email"] = "v1"

        solution = self.register_util["anti_email"]
        return util_mapping[solution]()

    def is_available(self, **pending) -> dict:
        if pending.get("anti_email") is True:
            return {
                "result": self.er_v2.is_availability() or self.er_v1.is_availability(),
                "util": "anti_email",
            }
        if pending.get("anti_slider") is True:
            return {"result": True, "util": "anti_slider"}
        if pending.get("anti_recaptcha") is True:
            return {"result": True, "util": "anti_recaptcha"}
        return {"result": True, "util": "normal"}

    def anti_slider(self, api: Chrome):
        path_bg_full = os.path.join(
            DIR_CACHE_IMAGE, f"full_{self.action_name}.{int(time.time())}.png"
        )
        path_bg_notch = os.path.join(
            DIR_CACHE_IMAGE, f"notch_{self.action_name}.{int(time.time())}.png"
        )

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

    def anti_recaptcha(self, api: Chrome):
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
        try:
            audio_url: str = activate_recaptcha(api)
        except AntiBreakOffWarning:
            return True

        # Google reCAPTCHA 风控
        if not audio_url:
            raise RiskControlSystemArmor("陷入无法逃逸的风控上下文")

        """
        TODO [√]音频转码 （MP3 --> WAV） 增加识别精度
        ------------------------------------------------------
        """
        path_audio_wav: str = handle_audio(
            audio_url=audio_url, dir_audio_cache=DIR_CACHE_AUDIO
        )
        logger.success("Handle Audio - path_audio_wav=`{}`".format(path_audio_wav))

        """
        TODO [√]声纹识别 --(output)--> 文本数据
        ------------------------------------------------------
        # speech_recognition.RequestError 需要挂起代理
        # http.client.IncompleteRead 网速不佳，音频文件未下载完整就开始解析
        """
        self.audio_answer: str = parse_audio(path_audio_wav)
        logger.success("Parse Audio - answer=`{}`".format(self.audio_answer))

        """
        TODO [√]定位输入框并填写文本数据
        ------------------------------------------------------
        # speech_recognition.RequestError 需要挂起代理
        # http.client.IncompleteRead 网速不佳，音频文件未下载完整就开始解析
        """
        response = submit_recaptcha(api, answer=self.audio_answer)
        if not response:
            logger.error("Submit reCAPTCHA answer.")
            raise TimeoutException

        # 回到 main-frame 否则后续DOM操作无法生效
        api.switch_to.default_content()

        if not correct_answer(api):
            return False
        return True


class TheElderBlood:
    def __init__(self, atomic: dict, silence: bool = None):
        # [√] 驱动参数
        self.silence = True if silence is None else silence

        # ----------------------------------
        # [√] Atomic原子实例
        # ----------------------------------
        # hyper_params    |原子实例超级参数
        # beat_dance      |集群节拍超级参数
        # ----------------------------------
        self.atomic: dict = atomic

        # ----------------------------------
        # 默认参数
        # ----------------------------------
        self.register_url = self.atomic["register_url"]
        self.action_name = self.atomic.get("name", "BaseAction")
        self.life_cycle = self.atomic.get("life_cycle", 24)
        self.email_domain = self.atomic.get("email_domain", "@gmail.com")
        self.username, self.password, self.email = "", "", ""

        # ----------------------------------
        # 超级参数
        # ----------------------------------
        self.hyper_params = {
            # 注册阶段
            "usr_email": False,
            "synergy": False,
            "tos": False,
            # 对抗阶段
            "skip": False,
            "anti_email": False,
            "anti_recaptcha": False,
            "anti_slider": False,
            "anti_cloudflare": False,
            # 延拓阶段
            "prism": False,
            "aff": 0,
            "plan_index": 0,
            # 缓存阶段
            "threshold": 3,
        }
        self.hyper_params.update(self.atomic.get("hyper_params", {}))
        self.beat_dance = self.hyper_params.get("beat_dance", 0)
        self.tos = bool(self.hyper_params["tos"])
        self.usr_email = bool(self.hyper_params["usr_email"])
        self.aff = self.hyper_params.get("aff", 0)
        self.synergy = bool(self.hyper_params.get("synergy"))
        self.plan_index = int(self.hyper_params["plan_index"])
        self.prism = bool(self.hyper_params["prism"])
        self.skip_checker = bool(self.hyper_params["skip"])
        self.anti_email = bool(self.hyper_params["anti_email"])
        self.anti_recaptcha = bool(self.hyper_params["anti_recaptcha"])
        self.anti_slider = bool(self.hyper_params["anti_slider"])
        self.anti_cloudflare = bool(self.hyper_params["anti_cloudflare"])
        self.threshold = self.hyper_params["threshold"]
        self.end_date = "2048-01-01 00:00"

        self.context_anti_email = {}

        # ----------------------------------
        # [√] 平台对象参数
        # ----------------------------------
        self.subscribe_url = ""

        # ----------------------------------
        # [√] 驱动超级参数
        # ----------------------------------
        # 任务超时后实体自我销毁
        self.work_clock_global = time.time()
        self.work_clock_utils = self.work_clock_global
        # 最大容灾阈值 单位秒
        self.work_clock_max_wait = 230 if self.anti_email else 120

        # ----------------------------------
        # [√] 模组依赖
        # ----------------------------------
        self.armor = ArmorUtils(beat_dance=self.beat_dance)

    def _is_timeout(self):
        if self.work_clock_utils - self.work_clock_global > self.work_clock_max_wait:
            return True
        return False

    def _update_clock(self):
        self.work_clock_utils = time.time()

    def set_chrome_options(self):
        options = ChromeOptions()

        # 无头启动禁用GPU渲染
        if self.silence is True or "linux" in sys.platform:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")

        # 滑块验证需要加载图片
        if not self.anti_slider:
            options.add_argument("blink-settings=imagesEnabled=false")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--lang=zh")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-javascript")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        return Chrome(ChromeDriverManager(log_level=0).install(), options=options)

    def generate_account(self, ctx: Chrome):
        """生成临时账号"""
        username = "".join(
            [random.choice(printable[: printable.index("!")]) for _ in range(9)]
        )
        password = "".join(
            [random.choice(printable[: printable.index(" ")]) for _ in range(15)]
        )

        # 不需要临时邮箱接码注册
        if not self.anti_email:
            # 已存在默认的邮箱域名
            # 将 username 作为 email_prefix
            if not self.usr_email:
                email = username
            # 需要键入自定义邮箱邮箱域名
            # 使用已定义的 email_domain 作为 email_suffix 补全
            else:
                email = username + self.email_domain
        # 调用外部服务申请可以接码的临时邮箱
        else:
            email = self.armor.anti_email(ctx, method="email")

        return username, password, email

    def sign_in(self, ctx: Chrome):
        """登录账号"""

    def sign_up(self, ctx: Chrome):
        """注册账号"""
        raise NotImplementedError

    def waiting_to_load(self, ctx: Chrome):
        """register --> dashboard 等待页面跳转"""
        raise NotImplementedError

    def buy_free_plan(self, ctx: Chrome):
        """购买免费套餐"""
        raise NotImplementedError

    def get_aff_link(self, api: Chrome) -> str:
        """获取邀请链接"""

    def check_in(self):
        """账号签到"""

    @staticmethod
    def get_html_handle(ctx: Chrome, url: str, timeout: Optional[int] = 45):
        """
        复杂化页面访问过程

        :param ctx:
        :param url:
        :param timeout:
        :return:
        """
        start_time = time.time()
        while True:
            try:
                ctx.get(url)
                break
            except (TimeoutException, WebDriverException):
                if time.time() - start_time < timeout:
                    ctx.refresh()
                    continue
                raise GetPageTimeoutException

    def check_heartbeat(self, debug: bool = False):
        """检测实例的健康状态"""
        _report = self.armor.is_available(
            anti_email=self.anti_email,
            anti_slider=self.anti_slider,
            anti_recaptcha=self.anti_recaptcha,
        )

        if not _report["result"]:
            logger.critical(
                ToolBox.runtime_report(
                    motive="BLOCK",
                    action_name=self.action_name,
                    message="实例构建失败，原因为实例依赖的基础设施不可用。",
                    util=_report["util"],
                )
            )
            return
        url = self.register_url
        scraper = create_scraper()
        try:
            response = scraper.get(url, timeout=5)
        except (SSLError, HTTPError):
            if debug:
                logger.warning(
                    ToolBox.runtime_report(
                        motive="BLOCK",
                        action_name=self.action_name,
                        message="Need to use a proxy to access the site.",
                        url=url,
                    )
                )
            return True
        except (ConnectionError, Timeout, RequestException) as e:
            logger.warning(
                ToolBox.runtime_report(
                    motive="BLOCK", action_name=self.action_name, url=url, error=e
                )
            )
            return False
        else:
            if response.status_code > 400:
                if self.skip_checker and response.status_code == 403:
                    logger.warning(
                        ToolBox.runtime_report(
                            motive="FORCE-RUN",
                            action_name=self.action_name,
                            message="The instance may deploy an implicit traffic defense component.",
                        )
                    )
                    return True
                logger.error(
                    ToolBox.runtime_report(
                        motive="BLOCK",
                        action_name=self.action_name,
                        message="InstanceStatusException",
                        status_code=response.status_code,
                        url=url,
                    )
                )
                return False
            return True

    def get_subscribe(self, api: Chrome):
        """获取订阅链接"""
        raise NotImplementedError

    def cache_subscribe(self, sm: Optional[SubscribeManager] = None):
        """存储订阅链接"""
        if self.subscribe_url == "":
            return

        sm = SubscribeManager() if sm is None else sm

        # Calculate ``life_cycle`` of the ``subscribe_url``.
        self.life_cycle -= self.threshold
        self.end_date = ToolBox.date_format_life_cycle(self.life_cycle)

        # 缓存订阅链接
        sm.add(subscribe=self.subscribe_url, end_date=self.end_date)

        # 更新别名映射
        sm.set_alias(
            alias=self.action_name,
            netloc=ToolBox.reset_url(url=self.subscribe_url, get_domain=True),
        )

        logger.success(
            ToolBox.runtime_report(
                action_name=self.action_name,
                motive="STORE",
                subscribe_url=self.subscribe_url,
            )
        )

    # =====================================================
    # 超级参数融合模式
    # =====================================================
    def activate(
        self,
        ctx: Chrome,
        synergy: Optional[bool] = False,
        sm: Optional[SubscribeManager] = None,
    ):
        """
        整合 实例生产注册，订阅获取，订阅存储，协同任务广播的流程

        :param sm:
        :param ctx:
        :param synergy:
        :return:
        """
        logger.debug(
            ToolBox.runtime_report(
                action_name=self.action_name,
                motive="RUN" if not synergy else "SYNERGY",
                params={hp[0]: hp[-1] for hp in self.hyper_params.items() if hp[-1]},
            )
        )

        self.get_html_handle(ctx=ctx, url=self.register_url)
        self.sign_up(ctx)

        if not synergy:
            self.waiting_to_load(ctx)
            if self.prism:
                self.buy_free_plan(ctx)
            self.get_subscribe(ctx)
            self.cache_subscribe(sm)
        else:
            logger.success(
                ToolBox.runtime_report(
                    action_name=self.action_name,
                    motive="DETACH",
                    message="Mission Completed!",
                )
            )

    def fight(self, ctx: Chrome, mq: Optional[MessageQueue] = None):
        """广播协同任务的上下文信息"""
        aff = 0 if self.aff < 1 or self.aff > 10 else self.aff
        if aff == 0:
            return True

        aff_link = self.get_aff_link(ctx)
        if not aff_link:
            return

        mq = MessageQueue() if mq is None else mq

        atomic = self.atomic
        atomic["register_url"] = aff_link
        atomic["synergy"] = True
        atomic["hyper_params"]["endpoint"] = self.end_date
        atomic["hyper_params"]["aff"] = 0
        context = {
            "atomic": atomic,
            "hostname": ToolBox.reset_url(self.register_url, get_domain=True),
        }
        for _ in range(aff):
            mq.broadcast_synergy_context(context)

    def assault(
        self,
        ctx: Chrome = None,
        synergy: Optional[bool] = None,
        force: Optional[bool] = False,
        **kwargs,
    ):
        """
        activate() 的外层包装，用于丰富实例运行前后的工作。
        包含实例心跳检测，实例生产，运行时的顶级异常捕获以及运行后的安全释放

        :param ctx:
        :param synergy:
        :param force:
        :param kwargs:
        :return:
        """
        # 心跳检测
        if not force:
            if not self.check_heartbeat():
                return

        # 获取驱动器
        ctx = self.set_chrome_options() if ctx is None else ctx
        if not ctx:
            return

        # 执行驱动
        try:
            self.activate(ctx, synergy=synergy, sm=kwargs.get("sm"))
            if not synergy:
                self.fight(ctx)

        except GetPageTimeoutException:
            logger.error(
                ToolBox.runtime_report(
                    motive="QUIT", action_name=self.action_name, message="初始页面渲染超时"
                )
            )
        except GetEmailTimeout:
            logger.error(
                ToolBox.runtime_report(
                    motive="QUIT", action_name=self.action_name, message="获取邮箱账号超时"
                )
            )
        except GetEmailCodeTimeout:
            logger.error(
                ToolBox.runtime_report(
                    motive="QUIT", action_name=self.action_name, message="获取邮箱验证码超时"
                )
            )
        except RiskControlSystemArmor as e:
            logger.error(
                ToolBox.runtime_report(
                    motive="QUIT", action_name=self.action_name, error=e.msg
                )
            )
            logger.info(
                "运行实例已被风控。\n"
                "可能原因及相关建议如下：\n"
                "1.目标站点可能正在遭受流量攻击，请更换测试用例；\n"
                "2.代理IP可能已被风控，建议关闭代理或更换代理节点；\n"
                "3.本机设备所在网络正在传输恶意流量，建议切换WLAN。\n"
                "4.浏览器自动化特征被精准识别，建议开启无定向驱动模式规避检测。\n"
                ">>> https://developers.google.com/recaptcha/docs/faq#"
                "my-computer-or-network-may-be-sending-automated-queries"
            )
        except InvalidSessionIdException:
            pass
        except WebDriverException as e:
            logger.exception(e)
        finally:
            # MaxRetryError
            # --------------
            # 场景：多个句柄争抢驱动权限 且有行为在驱动退出后发生。也即调用了已回收的类的方法。
            # 在 deploy 模式下，调度器可以在外部中断失活实例，此时再进行 api.quit() 则会引起一系列的 urllib3 异常
            try:
                ctx.quit()
            except MaxRetryError:
                pass
