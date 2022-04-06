# -*- coding: utf-8 -*-
# Time       : 2021/12/28 18:57
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import time
from typing import Optional

from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    ElementNotInteractableException,
    ElementNotVisibleException,
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from services.collector.exceptions import GetPageTimeoutException
from services.settings import logger
from services.utils import ToolBox
from ..core import TheElderBlood


class TheWitcher(TheElderBlood):
    def __init__(self, atomic: dict, silence: bool = None):
        super().__init__(atomic=atomic, silence=silence)

        # [√]平台对象参数
        self._API_GET_SUBSCRIBE = self.hyper_params.get("api", self.register_url)
        self._PATH_GET_SUBSCRIBE = "/user"
        self._PATH_INVITE = "/user/invite"
        self.aff_link = ""

        self._ABSOLUTE_INDEX = {
            "v2ray": {
                "xpath": "//div[@class='buttons']//a[contains(@class,'v2ray')]",
                "attr": "data-clipboard-text",
            },
            "ssr": {
                "xpath": """//a[@onclick="importSublink('ssr')"]/..//a[contains(@class,'copy')]""",
                "attr": "data-clipboard-text",
            },
            "aff": {
                "xpath": "//div[@class='hero-inner']//a",
                "attr": "data-clipboard-text",
            },
            "normal": {"xpath": "", "attr": ""},
        }
        for trigger_ in self._ABSOLUTE_INDEX.keys():
            if self.hyper_params.get(f"on_{trigger_}"):
                self._ABSOLUTE_INDEX[trigger_] = self.hyper_params[f"on_{trigger_}"]

    @staticmethod
    def get_html_handle(ctx: Chrome, url: str, timeout: Optional[int] = 45):
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

    def sign_in(self, ctx: Chrome):
        wait = WebDriverWait(
            ctx,
            10,
            poll_frequency=1,
            ignored_exceptions=[ElementNotVisibleException, NoSuchElementException],
        )
        wait.until(EC.element_to_be_clickable((By.TAG_NAME, "button")))

        ctx.find_element(By.ID, "email").send_keys(self.email)
        ctx.find_element(By.ID, "password").send_keys(self.password)
        ctx.find_element(By.TAG_NAME, "button").click()

    def sign_up(self, ctx: Chrome):
        # 灌入实体内脏数据
        self.username, self.password, self.email = self.generate_account(ctx)

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
                username_field = ctx.find_element(By.ID, "name")
                email_field = ctx.find_element(By.ID, "email")
                password_fields = [
                    ctx.find_element(By.ID, "passwd"),
                    ctx.find_element(By.ID, "repasswd"),
                ]
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
                chef = ActionChains(ctx)
                chef.double_click(ctx.find_element(By.ID, "email_verify"))
                chef.perform()

                # 确认发送邮箱验证码
                time.sleep(0.5 + self.beat_dance)
                WebDriverWait(
                    ctx, 35, poll_frequency=1, ignored_exceptions=NoSuchElementException
                ).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@class='swal2-confirm swal2-styled']")
                    )
                ).click()

                # 获取邮箱验证码
                email_code = self.armor.anti_email(ctx, method="code")

                # 填写邮箱验证码
                ctx.find_element(By.ID, "email_code").send_keys(email_code)
            # GeeTest 滑动验证 v2/v3
            if self.anti_slider:
                ok = self.armor.anti_slider(ctx)
                if not ok:
                    self._update_clock()
                    ctx.refresh()
                    continue
            # Google reCAPTCHA 人机验证
            if self.anti_recaptcha:
                try:
                    ok = self.armor.anti_recaptcha(ctx)
                    if not ok:
                        self._update_clock()
                        ctx.refresh()
                        continue
                except TimeoutException:
                    time.sleep(0.5 + self.beat_dance)
                    continue

            # [√] 提交数据
            time.sleep(0.5)
            for _ in range(3):
                try:
                    ctx.find_element(By.ID, "register-confirm").click()
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
            # 确认提交数据
            time.sleep(0.5)
            for _ in range(3):
                try:
                    ctx.find_element(
                        By.XPATH, "//button[contains(@class,'confirm')]"
                    ).click()
                    break
                except (
                    ElementNotInteractableException,
                    NoSuchElementException,
                    WebDriverException,
                ):
                    time.sleep(0.5 + self.beat_dance)
                    continue

            return True

    def waiting_to_load(self, ctx: Chrome):
        """
        register --> dashboard

        :param ctx:
        :return:
        """

        while ctx.current_url == self.register_url:
            time.sleep(0.1)
            if self._is_timeout():
                raise TimeoutException

        if "/auth/login" in ctx.current_url:
            self.sign_in(ctx)

        if self._PATH_GET_SUBSCRIBE not in ctx.current_url:
            ctx.get(
                ToolBox.reset_url(
                    url=self._API_GET_SUBSCRIBE, path=self._PATH_GET_SUBSCRIBE
                )
            )

    def buy_free_plan(self, ctx):
        xpath_page_shop = "//div[contains(@onclick,'shop')]"
        xpath_button_buy = "//a[contains(@onclick,'buyConfirm')]"

        try:
            # 点击商城转换页面
            time.sleep(1 + self.beat_dance)
            WebDriverWait(ctx, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_page_shop))
            ).click()
        except (ElementNotInteractableException, ElementClickInterceptedException):
            # 解决弹窗遮挡
            time.sleep(0.5 + self.beat_dance)
            ctx.find_element(By.XPATH, "//button").click()

            # 再次尝试跳转
            time.sleep(0.5 + self.beat_dance)
            WebDriverWait(ctx, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_page_shop))
            ).click()

        # 识别免费计划并购买
        time.sleep(1 + self.beat_dance)
        buy_free_plan = WebDriverWait(ctx, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_button_buy))
        )
        try:
            buy_free_plan.click()
        except WebDriverException:
            pass

        # 回到主页
        ctx.get(self.register_url)

    def get_subscribe(self, api: Chrome):
        """
        获取订阅

        引入健壮工程 + 手动标注数据集，大幅度增强模型的泛化能力
        :param api:
        :return:
        """
        # 兼容性改动，仅获取通用链接
        tag = WebDriverWait(
            api, 45, poll_frequency=0.5, ignored_exceptions=NoSuchElementException
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, self._ABSOLUTE_INDEX["v2ray"]["xpath"])
            )
        )
        self.subscribe_url = tag.get_attribute(self._ABSOLUTE_INDEX["v2ray"]["attr"])

        if self.subscribe_url == "":
            logger.error(
                ToolBox.runtime_report(
                    action_name=self.action_name,
                    motive="MISS",
                    message="订阅丢失",
                    email=self.email,
                    password=self.password,
                    register_url=self.register_url,
                )
            )

    def get_aff_link(self, api: Chrome) -> str:
        start_time = time.time()
        aff = self._ABSOLUTE_INDEX["aff"]
        url = ToolBox.reset_url(self.register_url, path=self._PATH_INVITE)
        api.get(url)
        while True:
            try:
                time.sleep(1 + self.beat_dance)
                self.aff_link = api.find_element(By.XPATH, aff["xpath"]).get_attribute(
                    aff["attr"]
                )
                return self.aff_link
            except WebDriverException:
                if time.time() - start_time > 45:
                    break


class LionCubOfCintra(TheWitcher):
    def __init__(self, atomic: dict, silence: bool = None):
        """
        # - 辛特拉的幼狮 -
        # -----------------------------------------------------------
        # 作为尼弗迦德帝位和辛特拉王位的第一顺位继承人，希瑞的正式头衔为：
        # 尼弗迦德女皇、辛特拉女王、布鲁格公主暨索登女爵、大小史凯利格岛之继承者、
        # 阿特里和艾伯·雅拉领主。

        :param atomic:
        :param silence:
        """
        super().__init__(atomic, silence=silence)
