# -*- coding: utf-8 -*-
# Time       : 2021/12/28 18:57
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import time
from json.decoder import JSONDecodeError

from cloudscraper.exceptions import CloudflareChallengeError
from selenium.common.exceptions import (
    TimeoutException,
    ElementNotInteractableException
)
from selenium.common.exceptions import (
    WebDriverException
)
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from urllib3.exceptions import MaxRetryError

from services.middleware.subscribe_io import SubscribeManager
from services.settings import logger
from services.utils import (
    ToolBox, SubscribeParser
)
from services.utils.armor.anti_email.exceptions import (
    GetEmailCodeTimeout, GetEmailTimeout
)
from ..core import TheElderBlood


class TheElf(TheElderBlood):
    def __init__(self, atomic: dict, chromedriver_path: str = None, silence: bool = None):
        super(TheElf, self).__init__(atomic=atomic, chromedriver_path=chromedriver_path, silence=silence)

        self._API_GET_SUBSCRIBE = self.hyper_params.get("api", self.register_url)
        self._PATH_GET_SUBSCRIBE = "/api/v1/user/getSubscribe"

    @staticmethod
    def get_html_handle(api, url, wait_seconds: int = 15):
        api.set_page_load_timeout(time_to_wait=wait_seconds)
        api.get(url)

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
                email_field = api.find_element(By.XPATH, "//input[@placeholder='邮箱']")
                password_fields = api.find_elements(By.XPATH, "//input[@placeholder='密码']")
                email_field.clear()
                email_field.send_keys(self.email)
                for element in password_fields:
                    element.clear()
                    element.send_keys(self.password)
            except (ElementNotInteractableException, WebDriverException):
                time.sleep(0.5 + self.beat_dance)
                continue

            # 确认服务条款
            if self.tos:
                api.find_element(By.XPATH, "//input[@type='checkbox']").click()

            """
            [√]对抗模组
            ---------------------
            """
            # 邮箱验证
            if self.anti_email:
                # 发送验证码
                api.find_elements(By.XPATH, "//button[@type='submit']")[0].click()

                # 获取验证码
                email_code = self.armor.anti_email(api, method="code")

                # 填写验证码
                api.find_element(By.XPATH, "//input[@placeholder='邮箱验证码']").send_keys(email_code)

            # Google reCAPTCHA 人机验证
            if self.anti_recaptcha:
                raise ImportWarning

            """
            [√]提交数据
            ---------------------
            """
            time.sleep(0.5)
            for _ in range(3):
                try:
                    api.find_elements(By.XPATH, "//button[@type='submit']")[-1].click()
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
            api.get(url)
            if self._is_timeout():
                raise TimeoutException
            if api.current_url != self.register_url:
                break
            time.sleep(0.2)

    def get_subscribe(self, api: Chrome):
        """
        获取订阅

        引入健壮工程 + 手动标注数据集，大幅度增强模型的泛化能力
        :param api:
        :return:
        """
        try:
            self.subscribe_url = SubscribeParser.parse_url_from_json(
                url=ToolBox.reset_url(self._API_GET_SUBSCRIBE, path=self._PATH_GET_SUBSCRIBE),
                api_cookie=api.get_cookies()
            )
        except (CloudflareChallengeError, JSONDecodeError):
            context: str = api.find_element(By.XPATH, "//pre").text
            self.subscribe_url = SubscribeParser.parse_url_from_page(context)

    def activate(self, api=None, synergy: bool = False, sm: SubscribeManager = None):
        """

        :param sm:
        :param api:
        :param synergy:
        :return:
        """
        logger.debug(ToolBox.runtime_report(
            action_name=self.action_name,
            motive="RUN",
            params=self.hyper_params
        ))

        self.get_html_handle(api=api, url=self.register_url, wait_seconds=45 + self.beat_dance)
        self.sign_up(api)

        if not synergy:
            self.waiting_to_load(api)
            self.get_subscribe(api)

            # 由于 v2board 使用的是 token 通用订阅，不需要区分模板通道
            self.cache_subscribe(sm)


class LaraDorren(TheElf):
    def __init__(self, atomic: dict, chromedriver_path: str = None, silence: bool = None):
        super(LaraDorren, self).__init__(atomic, chromedriver_path=chromedriver_path, silence=silence)

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
