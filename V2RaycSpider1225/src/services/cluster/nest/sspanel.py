# -*- coding: utf-8 -*-
# Time       : 2021/12/28 18:57
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import time

from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    ElementNotInteractableException,
    NoSuchElementException
)
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import MaxRetryError

from services.cluster.exceptions import GetPageTimeoutException
from services.middleware.subscribe_io import SubscribeManager
from services.middleware.workers_io import MessageQueue
from services.settings import (
    logger
)
from services.utils import (
    ToolBox
)
from services.utils.armor.anti_email.exceptions import (
    GetEmailCodeTimeout, GetEmailTimeout
)
from ..core import TheElderBlood


class TheWitcher(TheElderBlood):
    def __init__(self, atomic: dict, chromedriver_path: str = None, silence: bool = None, ):
        super(TheWitcher, self).__init__(atomic=atomic, chromedriver_path=chromedriver_path, silence=silence)

        """
        TODO [√]平台对象参数
        ---------------------
        """
        self._API_GET_SUBSCRIBE = self.hyper_params.get("api", self.register_url)
        self._PATH_GET_SUBSCRIBE = "/user"
        self._PATH_INVITE = "/user/invite"
        self.aff_link = ""

        self._ABSOLUTE_INDEX = {
            "v2ray": {
                "xpath": "//div[@class='buttons']//a[contains(@class,'v2ray')]",
                "attr": "data-clipboard-text"
            },
            "ssr": {
                "xpath": """//a[@onclick="importSublink('ssr')"]/..//a[contains(@class,'copy')]""",
                "attr": "data-clipboard-text"
            },
            "aff": {
                "xpath": "//div[@class='hero-inner']//a",
                "attr": "data-clipboard-text"
            },
            "normal": {
                "xpath": "",
                "attr": ""
            }
        }

    @staticmethod
    def get_html_handle(api: Chrome, url, timeout: float = 45):
        start_time = time.time()
        while True:
            try:
                api.get(url)
                break
            except (TimeoutException, WebDriverException):
                if time.time() - start_time < timeout:
                    api.refresh()
                    continue
                raise GetPageTimeoutException

    def sign_up(self, api: Chrome):
        # 灌入实体内脏数据
        self.username, self.password, self.email = self.generate_account(api)

        # 加入全局超时判断的 register 生命周期轮询
        while True:
            # 超时销毁
            if self._is_timeout():
                raise TimeoutException

            """
            [√]灌入基础信息
            ---------------------
            """
            time.sleep(0.5 + self.beat_dance)
            try:
                username_field = api.find_element(By.ID, "name")
                email_field = api.find_element(By.ID, "email")
                password_fields = [api.find_element(By.ID, "passwd"), api.find_element(By.ID, "repasswd")]
                email_field.clear()
                email_field.send_keys(self.email)
                username_field.clear()
                username_field.send_keys(self.username)
                for element in password_fields:
                    element.clear()
                    element.send_keys(self.password)
            except (ElementNotInteractableException, WebDriverException):
                time.sleep(0.5 + self.beat_dance)
                continue

            """
            [√]对抗模组
            ---------------------
            """
            # 邮箱验证
            if self.anti_email:
                # 发送邮箱验证码
                chef = ActionChains(api)
                chef.double_click(api.find_element(By.ID, "email_verify"))
                chef.perform()

                # 确认发送邮箱验证码
                time.sleep(0.5 + self.beat_dance)
                WebDriverWait(api, 35).until(EC.element_to_be_clickable((
                    By.XPATH, "//button[@class='swal2-confirm swal2-styled']"
                ))).click()

                # 获取邮箱验证码
                email_code = self.armor.anti_email(api, method="code")

                # 填写邮箱验证码
                api.find_element(By.ID, "email_code").send_keys(email_code)

            # GeeTest 滑动验证 v2/v3
            if self.anti_slider:
                ok = self.armor.anti_slider(api)
                if not ok:
                    self._update_clock()
                    api.refresh()
                    continue
            # Google reCAPTCHA 人机验证
            if self.anti_recaptcha:
                try:
                    self.armor.anti_recaptcha(api)
                    # 回到 main-frame 否则后续DOM操作无法生效
                    api.switch_to.default_content()
                except TimeoutException:
                    time.sleep(0.5 + self.beat_dance)
                    continue
                # Google reCAPTCHA 风控
                except WebDriverException:
                    raise WebDriverException

            """
            [√]提交数据
            ---------------------
            """
            time.sleep(0.5)
            for _ in range(3):
                try:
                    api.find_element(By.ID, "register-confirm").click()
                    break
                except (ElementNotInteractableException, WebDriverException):
                    ToolBox.echo(
                        msg=f"正在同步集群节拍 | "
                            f"action={self.action_name} "
                            f"hold={1.5 + self.beat_dance}s "
                            f"session_id={api.session_id} "
                            f"event=`register-pending`",
                        level=2
                    )
                    time.sleep(3 + self.beat_dance)
                    continue
            # 确认提交数据
            time.sleep(0.5)
            for _ in range(3):
                try:
                    api.find_element(By.XPATH, "//button[contains(@class,'confirm')]").click()
                    break
                except (ElementNotInteractableException, NoSuchElementException, WebDriverException):
                    time.sleep(0.5 + self.beat_dance)
                    continue

            return True

    def waiting_to_load(self, api):
        """
        register --> dashboard

        :param api:
        :return:
        """
        url = ToolBox.reset_url(url=self._API_GET_SUBSCRIBE, path=self._PATH_GET_SUBSCRIBE)

        time.sleep(0.5)
        for _ in range(45):
            if self._is_timeout():
                raise TimeoutException
            if api.current_url == self.register_url:
                time.sleep(1)
                self.get_html_handle(api, url)
            else:
                break
            time.sleep(0.3)

    def buy_free_plan(self, api, force_draw: int = 2):
        xpath_page_shop = "//div[contains(@onclick,'shop')]"
        xpath_button_buy = "//a[contains(@onclick,'buyConfirm')]"

        try:
            # 点击商城转换页面
            time.sleep(1 + self.beat_dance)
            WebDriverWait(api, 10).until(EC.presence_of_element_located((
                By.XPATH, xpath_page_shop
            ))).click()
        except ElementNotInteractableException:
            # 解决弹窗遮挡
            time.sleep(0.5 + self.beat_dance)
            api.find_element(By.XPATH, "//button").click()

            # 再次尝试跳转
            time.sleep(0.5 + self.beat_dance)
            WebDriverWait(api, 10).until(EC.element_to_be_clickable((
                By.XPATH, xpath_page_shop
            ))).click()

        # 识别免费计划并购买
        time.sleep(1 + self.beat_dance)
        buy_free_plan = WebDriverWait(api, 10).until(EC.presence_of_element_located((
            By.XPATH, xpath_button_buy
        )))
        for _ in range(force_draw):
            try:
                buy_free_plan.click()
            except WebDriverException:
                pass

        # 回到主页
        api.get(self.register_url)

    def get_subscribe(self, api: Chrome):
        """
        获取订阅

        引入健壮工程 + 手动标注数据集，大幅度增强模型的泛化能力
        :param api:
        :return:
        """
        # 兼容性改动，仅获取通用链接
        method_ = self._ABSOLUTE_INDEX["v2ray"]
        for _ in range(30):
            try:
                self.subscribe_url = api.find_element(By.XPATH, method_["xpath"]).get_attribute(method_["attr"])
                break
            except NoSuchElementException:
                time.sleep(1)

        if self.subscribe_url != "":
            logger.debug(ToolBox.runtime_report(
                action_name=self.action_name,
                motive="GET",
                subscribe_url=self.subscribe_url
            ))
        else:
            logger.error(ToolBox.runtime_report(
                action_name=self.action_name,
                motive="MISS",
                message="订阅丢失",
                email=self.email,
                password=self.password,
                register_url=self.register_url
            ))

    def get_aff_link(self, api: Chrome) -> str:
        start_time = time.time()
        aff = self._ABSOLUTE_INDEX["aff"]
        url = ToolBox.reset_url(self.register_url, path=self._PATH_INVITE)
        api.get(url)
        while True:
            try:
                time.sleep(1 + self.beat_dance)
                self.aff_link = api.find_element(By.XPATH, aff["xpath"]).get_attribute(aff["attr"])
                return self.aff_link
            except WebDriverException:
                if time.time() - start_time > 45:
                    break

    def activate(self, api, synergy: bool = False, sm: SubscribeManager = None):
        """

        :param sm:
        :param api:
        :param synergy:
        :return:
        """
        logger.debug(ToolBox.runtime_report(
            action_name=self.action_name,
            motive="RUN" if not synergy else "SYNERGY",
            params={hp[0]: hp[-1] for hp in self.hyper_params.items() if hp[-1]}
        ))

        self.get_html_handle(api=api, url=self.register_url)
        self.sign_up(api)

        if not synergy:
            self.waiting_to_load(api)
            if self.prism:
                self.buy_free_plan(api)
            self.get_subscribe(api)
            self.cache_subscribe(sm)
        else:
            logger.success(ToolBox.runtime_report(
                action_name=self.action_name,
                motive="DETACH",
                message="Mission Completed!"
            ))


class LionCubOfCintra(TheWitcher):
    def __init__(self, atomic: dict, chromedriver_path: str = None, silence: bool = None):
        """
        # - 辛特拉的幼狮 -
        # -----------------------------------------------------------
        # 作为尼弗迦德帝位和辛特拉王位的第一顺位继承人，希瑞的正式头衔为：
        # 尼弗迦德女皇、辛特拉女王、布鲁格公主暨索登女爵、大小史凯利格岛之继承者、
        # 阿特里和艾伯·雅拉领主。

        :param atomic:
        :param chromedriver_path:
        :param silence:
        """
        super(LionCubOfCintra, self).__init__(atomic, chromedriver_path=chromedriver_path, silence=silence)

    def fight(self, api, mq: MessageQueue = None):
        aff = 0 if self.aff < 1 or self.aff > 10 else self.aff
        if aff == 0:
            return True

        aff_link = self.get_aff_link(api)
        if not aff_link:
            return

        mq = MessageQueue() if mq is None else mq

        atomic = self.atomic
        atomic.update({"register_url": aff_link, "synergy": True})
        context = {
            "atomic": atomic,
            "hostname": ToolBox.reset_url(self.register_url, get_domain=True),
        }
        for _ in range(aff):
            mq.broadcast_synergy_context(context)

    def assault(self, api=None, synergy: bool = None, force: bool = False, **kwargs):

        # 心跳检测
        if not force:
            if not self.check_heartbeat():
                return

        # 获取驱动器
        api = self.set_chrome_options() if api is None else api
        if not api:
            return

        # 执行驱动
        try:
            self.activate(api, synergy=synergy, sm=kwargs.get("sm"))
            if not synergy:
                self.fight(api)

        except GetPageTimeoutException:
            logger.error(ToolBox.runtime_report(
                motive="QUIT",
                action_name=self.action_name,
                message="初始页面渲染超时"
            ))
        except GetEmailTimeout:
            logger.error(ToolBox.runtime_report(
                motive="QUIT",
                action_name=self.action_name,
                message="获取邮箱账号超时"
            ))
        except GetEmailCodeTimeout:
            logger.error(ToolBox.runtime_report(
                motive="QUIT",
                action_name=self.action_name,
                message="获取邮箱验证码超时"
            ))
        except WebDriverException as e:
            logger.exception(e)
        finally:
            # MaxRetryError
            # --------------
            # 场景：多个句柄争抢驱动权限 且有行为在驱动退出后发生。也即调用了已回收的类的方法。
            # 在 deploy 模式下，调度器可以在外部中断失活实例，此时再进行 api.quit() 则会引起一系列的 urllib3 异常
            try:
                api.quit()
            except MaxRetryError:
                pass
