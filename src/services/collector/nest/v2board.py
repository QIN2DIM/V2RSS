# -*- coding: utf-8 -*-
# Time       : 2021/12/28 18:57
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import time
from json.decoder import JSONDecodeError
from typing import Optional, Dict, Any

from cloudscraper.exceptions import CloudflareChallengeError
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from services.utils import ToolBox, SubscribeParser
from ..core import TheElderBlood


class TheElf(TheElderBlood):
    def __init__(self, atomic: Dict[str, Any], silence: Optional[bool] = None):
        super().__init__(atomic=atomic, silence=silence)

        self._API_GET_SUBSCRIBE = self.hyper_params.get("api", self.register_url)
        self._PATH_GET_SUBSCRIBE = "/api/v1/user/getSubscribe"
        self._PATH_PLAN_STORE = "/#/plan"

    @staticmethod
    def get_html_handle(ctx: Chrome, url: str, timeout: Optional[int] = 45):
        ctx.set_page_load_timeout(time_to_wait=timeout)
        ctx.get(url)

    def sign_up(self, ctx: Chrome):
        # 灌入实体内脏数据
        self.username, self.password, self.email = self.generate_account(ctx)

        # 加入全局超时判断的 register 生命周期轮询
        while True:
            # 超时销毁
            if self._is_timeout():
                raise TimeoutException

            # [√] 灌入基础信息
            time.sleep(0.5 + self.beat_dance)
            try:
                email_field = ctx.find_element(By.XPATH, "//input[@placeholder='邮箱']")
                password_fields = ctx.find_elements(
                    By.XPATH, "//input[@placeholder='密码']"
                )
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
                ctx.find_element(By.XPATH, "//input[@type='checkbox']").click()

            # [√] 对抗模组
            # 邮箱验证
            if self.anti_email:
                # 发送验证码
                ctx.find_elements(By.XPATH, "//button[@type='submit']")[0].click()

                # 获取验证码
                email_code = self.armor.anti_email(ctx, method="code")

                # 填写验证码
                ctx.find_element(By.XPATH, "//input[@placeholder='邮箱验证码']").send_keys(
                    email_code
                )

            # [√] 提交数据
            time.sleep(0.5)
            for _ in range(3):
                try:
                    ctx.find_elements(By.XPATH, "//button[@type='submit']")[-1].click()
                    break
                except (ElementNotInteractableException, WebDriverException):
                    ToolBox.echo(
                        msg=f"正在同步集群节拍 | "
                        f"action={self.action_name} "
                        f"hold={1.5 + self.beat_dance}s "
                        f"session_id={ctx.session_id} "
                        f"event=`register-pending`",
                        level=2,
                    )
                    time.sleep(3 + self.beat_dance)
                    continue

            # [√] 捕获隐藏的 checkbox
            # Google reCAPTCHA 人机验证
            if self.anti_recaptcha:
                WebDriverWait(
                    ctx, 10, poll_frequency=1, ignored_exceptions=NoSuchElementException
                ).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='ant-modal-body']")
                    )
                )
                self.armor.anti_recaptcha(ctx)

            return True

    def waiting_to_load(self, ctx: Chrome):
        """
        register --> dashboard

        :param ctx:
        :return:
        """
        while ctx.current_url == self.register_url:
            if self._is_timeout():
                raise TimeoutException

        ctx.get(
            ToolBox.reset_url(url=self._API_GET_SUBSCRIBE, path=self._PATH_GET_SUBSCRIBE)
        )

    def get_subscribe(self, ctx: Chrome):
        """
        获取订阅

        引入健壮工程 + 手动标注数据集，大幅度增强模型的泛化能力
        :param ctx:
        :return:
        """
        try:
            self.subscribe_url = SubscribeParser.parse_url_from_json(
                url=ToolBox.reset_url(
                    self._API_GET_SUBSCRIBE, path=self._PATH_GET_SUBSCRIBE
                ),
                api_cookie=ctx.get_cookies(),
            )
        except (CloudflareChallengeError, JSONDecodeError):
            context: str = ctx.find_element(By.XPATH, "//pre").text
            self.subscribe_url = SubscribeParser.parse_url_from_page(context)

    def buy_free_plan(self, ctx: Chrome):
        # New subtask tab.
        user_tab = ctx.current_window_handle
        ctx.switch_to.new_window("tab")

        # Jump to the `plan store` page.
        ctx.get(
            ToolBox.reset_url(url=self._API_GET_SUBSCRIBE, path=self._PATH_PLAN_STORE)
        )

        # Click `Buy Free Plan` Button.
        if self.plan_index == 0:
            WebDriverWait(ctx, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(@class,'btn-rounded')]")
                )
            ).click()

        # Place an order and jump to the payment page to terminate the cycle.
        for _ in range(3):
            time.sleep(2)
            try:
                WebDriverWait(ctx, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class,'btn-block')]")
                    )
                ).click()
            except WebDriverException:
                try:
                    time.sleep(2)
                    WebDriverWait(ctx, 3).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "//div[@class='ant-modal-body']//button[contains(@class,'primary')]",
                            )
                        )
                    ).click()
                except TimeoutException:
                    pass

            # Return to the main business tab and refresh the interface.
        ctx.switch_to.window(user_tab)
        ctx.refresh()


class LaraDorren(TheElf):
    def __init__(self, atomic: dict, silence: bool = None):
        super().__init__(atomic, silence=silence)
