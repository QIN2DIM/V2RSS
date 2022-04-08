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
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from services.settings import logger
from services.utils import ToolBox
from ..core import TheElderBlood


class GoldenOrder(TheElderBlood):
    COMMAND_CONTINUE = "continue"
    COMMAND_BREAK = "break"
    COMMAND_OK = "ok"

    def __init__(self, atomic: dict, silence: bool = None):
        super().__init__(atomic=atomic, silence=silence)

        # [√]平台对象参数
        self._API_GET_SUBSCRIBE = self.hyper_params.get("api", self.register_url)
        self.PATH_GET_SUBSCRIBE = "/user"
        self.PATH_INVITE = "/user/invite"
        self.aff_link = ""

        self.ABSOLUTE_INDEX = {
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
            "trigger_flooding_entity_data": {
                "name_id": "name",
                "email_id": "email",
                "passwd_id": "passwd",
                "repasswd_id": "repasswd",
            },
            "trigger_anti_email": {"send_id": "email_verify", "input_id": "email_code"},
            "trigger_submit_entity_data": {"button_id": "register-confirm"},
            "trigger_confirm_entity_data": {
                "button_xpath": "//button[contains(@class,'confirm')]"
            },
            "trigger_sign_in": {
                "email_id": "email",
                "password_id": "password",
                "login_xpath": "//button",
            },
        }
        for trigger_ in self.ABSOLUTE_INDEX.keys():
            if self.hyper_params.get(f"on_{trigger_}"):
                self.ABSOLUTE_INDEX[trigger_] = self.hyper_params[f"on_{trigger_}"]

    def flooding_entity_data(self, ctx: Chrome):
        _trigger = self.ABSOLUTE_INDEX["trigger_flooding_entity_data"]
        _name_id = _trigger.get("name_id", "name")
        _email_id = _trigger.get("email_id", "email")
        _passwd_id = _trigger.get("passwd_id", "passwd")
        _repasswd_id = _trigger.get("repasswd_id", "repasswd")

        time.sleep(0.5 + self.beat_dance)

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

    def submit_entity_data(self, ctx: Chrome):
        _button_id = self.ABSOLUTE_INDEX["trigger_submit_entity_data"]["button_id"]

        time.sleep(0.5)
        for _ in range(3):
            try:
                ctx.find_element(By.ID, _button_id).click()
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

    def confirm_entity_data(self, ctx: Chrome):
        button_xpath = self.ABSOLUTE_INDEX["trigger_confirm_entity_data"]["button_xpath"]

        time.sleep(0.5)
        for _ in range(3):
            try:
                ctx.find_element(By.XPATH, button_xpath).click()
                break
            except (
                ElementNotInteractableException,
                NoSuchElementException,
                WebDriverException,
            ):
                time.sleep(0.7 + self.beat_dance)
                continue

    def handle_machine_email(self, ctx):
        _trigger: dict = self.ABSOLUTE_INDEX["trigger_anti_email"]
        _send_id = _trigger.get("send_id", "email_verify")
        _input_id = _trigger.get("input_id", "email_code")

        # 发送邮箱验证码
        chef = ActionChains(ctx)
        chef.double_click(ctx.find_element(By.ID, _send_id))
        chef.perform()

        # 获取邮箱验证码
        email_code = self.armor.anti_email(ctx, method="code")

        # 确认邮箱验证码
        time.sleep(0.5 + self.beat_dance)
        try:
            ActionChains(ctx).send_keys(Keys.ESCAPE).perform()
        except TimeoutException:
            pass

        # 填写邮箱验证码
        ctx.find_element(By.ID, _input_id).send_keys(email_code)

    def im_not_robot(self, ctx):
        # GeeTest Slider v2/v3
        if self.anti_slider:
            ok = self.armor.anti_slider(ctx)
            if not ok:
                self._update_clock()
                ctx.refresh()
                return self.COMMAND_CONTINUE
        # Google reCAPTCHA
        if self.anti_recaptcha:
            try:
                ok = self.armor.anti_recaptcha(ctx)
                if not ok:
                    self._update_clock()
                    ctx.refresh()
                    return self.COMMAND_CONTINUE
            except TimeoutException:
                time.sleep(0.5 + self.beat_dance)
                return self.COMMAND_CONTINUE

        return self.COMMAND_OK

    def sign_in(self, ctx: Chrome):
        _trigger = self.ABSOLUTE_INDEX["trigger_sign_in"]
        _email_id = _trigger.get("email_id", "email")
        _password_id = _trigger.get("password_id", "password")
        _login_xpath = _trigger.get("login_xpath", "//button")

        time.sleep(0.3 + self.beat_dance)
        WebDriverWait(ctx, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "button")))

        ctx.find_element(By.ID, _email_id).send_keys(self.email)
        ctx.find_element(By.ID, _password_id).send_keys(self.password)
        ctx.find_element(By.XPATH, _login_xpath).click()

    def sign_up(self, ctx: Chrome):
        # 灌入实体数据
        self.username, self.password, self.email = self.generate_account(ctx)

        while True:
            # ---------------------------------------------
            # [√] 超时处理
            # ---------------------------------------------
            if self._is_timeout():
                raise TimeoutException
            # ---------------------------------------------
            # [√] 灌入基础信息
            # ---------------------------------------------
            try:
                self.flooding_entity_data(ctx)
            except (ElementNotInteractableException, WebDriverException):
                time.sleep(0.5 + self.beat_dance)
                continue
            # ---------------------------------------------
            # [√] 对抗模组
            # ---------------------------------------------
            if self.im_not_robot(ctx) == self.COMMAND_CONTINUE:
                continue
            if self.anti_email:
                self.handle_machine_email(ctx)
            # ---------------------------------------------
            # [√] 提交数据
            # ---------------------------------------------
            self.submit_entity_data(ctx)
            # ---------------------------------------------
            # [√] 确认提交数据
            # ---------------------------------------------
            self.confirm_entity_data(ctx)

            return True

    def waiting_to_load(self, ctx: Chrome):
        """
        register --> dashboard

        :param ctx:
        :return:
        """
        while ctx.current_url == self.register_url:
            time.sleep(0.5)
            if self._is_timeout():
                raise TimeoutException

        if "/auth/login" in ctx.current_url:
            self.sign_in(ctx)

        if self.PATH_GET_SUBSCRIBE not in ctx.current_url:
            ctx.get(
                ToolBox.reset_url(
                    url=self._API_GET_SUBSCRIBE, path=self.PATH_GET_SUBSCRIBE
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
        _subs_xpath = self.ABSOLUTE_INDEX["v2ray"]["xpath"]
        _subs_attr = self.ABSOLUTE_INDEX["v2ray"]["attr"]

        # 兼容性改动，仅获取通用链接
        self.subscribe_url = (
            WebDriverWait(api, 45)
            .until(EC.presence_of_element_located((By.XPATH, _subs_xpath)))
            .get_attribute(_subs_attr)
        )

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
        _aff_xpath = self.ABSOLUTE_INDEX["aff"]["xpath"]
        _aff_attr = self.ABSOLUTE_INDEX["aff"]["attr"]

        start_time = time.time()
        url_invite = ToolBox.reset_url(self.register_url, path=self.PATH_INVITE)
        api.get(url_invite)

        while True:
            try:
                time.sleep(1 + self.beat_dance)
                aff_tag = api.find_element(By.XPATH, _aff_xpath)
                self.aff_link = aff_tag.get_attribute(_aff_attr)
                return self.aff_link
            except WebDriverException:
                try:
                    # 深度兼容 material
                    alert_ = api.find_element(By.TAG_NAME, "h3").text
                    if "无法使用邀请链接" in alert_:
                        break
                except (NoSuchElementException, AttributeError):
                    pass
                if time.time() - start_time > 45:
                    break


class LionCubOfCintra(GoldenOrder):
    """
    # 「辛特拉的幼狮」希瑞
    # -----------------------------------------------------------
    # 作为尼弗迦德帝位和辛特拉王位的第一顺位继承人，希瑞的正式头衔为：
    # 尼弗迦德女皇、辛特拉女王、布鲁格公主暨索登女爵、大小史凯利格岛之继承者、
    # 阿特里和艾伯·雅拉领主。
    """


class LunarPrincessRani(GoldenOrder):
    """
    # 「月亮公主」菈妮
    # -----------------------------------------------------------
    # 菈妮，有时也被称为雪地女巫，是艾尔登法环中一个拥有四条手臂的神秘女人。
    """

    def __init__(self, atomic: dict, silence: bool = None):
        super().__init__(atomic=atomic, silence=silence)
        self.ABSOLUTE_INDEX.update(
            {
                "v2ray": {
                    "xpath": "//a[contains(@data-clipboard-text,'?sub=3')]",
                    "attr": "data-clipboard-text",
                },
                "aff": {
                    "xpath": "//button[contains(@class,'subscription')]",
                    "attr": "data-clipboard-text",
                },
                "trigger_submit_entity_data": {"button_id": "tos"},
                "trigger_confirm_entity_data": {"button_xpath": "//button[@id='reg']"},
                "trigger_sign_in": {
                    "email_id": "email",
                    "password_id": "passwd",
                    "login_xpath": "//button",
                },
            }
        )

        self.contact = self.hyper_params.get("contact", False)

    def flooding_entity_data(self, ctx: Chrome):
        super().flooding_entity_data(ctx=ctx)

        # 需要额外灌入联络方式
        if self.contact:
            # 点击联络方式
            ctx.find_element(By.ID, "imtype").click()
            # 选择联络方式
            WebDriverWait(ctx, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//ul//li//a[@class='dropdown-option']")
                )
            ).click()
            # 输入联络方式
            ctx.find_element(By.ID, "wechat").send_keys(self.username)


class StarscourgeRadahn(GoldenOrder):
    """
    #「碎星将军」拉塔恩
    # -----------------------------------------------------------
    # 拉达恩将军曾经被称为「著名的红狮」，他被猩红腐烂侵蚀，
    # 导致他吞噬了朋友和敌人的尸体，对着天空嚎叫。尽管他的状况不佳，
    # 但他仍然是一个凶猛的战士，利用他的蛮力和重力魔法来抵挡攻击者。
    # 你将有幸与星际之神对决，并让他脱离苦海。
    """

    def __init__(self, atomic: dict, silence: bool = None):
        super().__init__(atomic=atomic, silence=silence)

        self.ABSOLUTE_INDEX.update(
            {
                "v2ray": {
                    "xpath": "//button[contains(@data-clipboard-text,'?sub=3')]",
                    "attr": "data-clipboard-text",
                },
                "aff": {
                    "xpath": "//a[contains(@data-clipboard-text,'?code=')]",
                    "attr": "data-clipboard-text",
                },
                "v2ray_1": {
                    "xpath": "//button[contains(@data-clipboard-text,'?mu=2')]",
                    "attr": "data-clipboard-text",
                },
                "aff_1": {"xpath": "//input[contains(@value,'?code=')]", "attr": "value"},
                "trigger_submit_entity_data": {"button_id": "register-button"},
                "trigger_confirm_entity_data": {
                    "button_xpath": "//button[text()='转入用户中心']"
                },
            }
        )


class MohgLordOfBlood(GoldenOrder):
    """
    #「鲜血君王」蒙格
    # -----------------------------------------------------------
    # Welcome, honored guest. To the birthplace of our Dynasty!
    """

    def __init__(self, atomic: dict, silence: bool = None):
        super().__init__(atomic=atomic, silence=silence)
        self.PATH_INVITE = "/user/setting/invite"
        self.ABSOLUTE_INDEX.update(
            {
                "v2ray": {
                    "xpath": "//button[contains(@data-clipboard-text,'?sub=3')]",
                    "attr": "data-clipboard-text",
                },
                "aff": {
                    "xpath": "//button[contains(@data-clipboard-text,'?code=')]",
                    "attr": "data-clipboard-text",
                },
                "trigger_anti_email": {"send_id": "send-code"},
                "trigger_submit_entity_data": {
                    "button_id": "register_submit",
                    "input_id": "email_code",
                },
                "trigger_confirm_entity_data": {"button_xpath": "//button[text()='确定']"},
            }
        )

    def flooding_entity_data(self, ctx: Chrome):
        super().flooding_entity_data(ctx=ctx)
        if self.tos:
            ctx.find_element(By.XPATH, "//label//span").click()


class MimicTear(GoldenOrder):
    """
    #「ASHES」仿生泪滴
    # -----------------------------------------------------------
    # This spirit takes the form of the summoner to fight alongside
    # them, but its mimicry does not extend to imitating the
    # summoner's will.
    # Mimic tears are the result of an attempt by the Eternal City to
    # forge a lord.
    """
