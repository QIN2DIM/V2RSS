# -*- coding: utf-8 -*-
# Time       : 2021/7/30 4:01
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: Adaptive acquisition framework
import time
from urllib.parse import urlparse

from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver import Chrome

from src.BusinessCentralLayer.setting import logger
from .master import ActionMasterGeneral


class Prism(ActionMasterGeneral):
    def __init__(self, atomic: dict, silence=True, assault=True):
        super(Prism, self).__init__(silence=silence, assault=assault)

        atomic = {} if atomic is None else atomic

        self.register_url = "" if atomic.get("register_url") is None else atomic.get("register_url")
        self.hyper_params = {} if atomic.get("hyper_params") is None else atomic.get("hyper_params")
        self.action_name = "PrismInstance" if atomic.get("name") is None else atomic.get("name")
        self.life_cycle = 1 if atomic.get("life_cycle") is None else atomic.get("life_cycle")
        self.anti_slider = True if atomic.get("anti_slider") is None else atomic.get("anti_slider")
        self.atomic = atomic

        self.xpath_page_shop = "//div[contains(@onclick,'shop')]"
        self.xpath_button_buy = "//a[contains(@onclick,'buyConfirm')]"
        self.xpath_canvas_subs = "//div[@class='card-body']"

    def run(self, api=None):
        logger.debug(
            f">> RUN <{self.action_name}> --> beat_sync[{self.beat_sync}] feature[{self.atomic.get('feature')}]")
        api = self.set_spider_option() if api is None else api
        try:
            self.get_html_handle(api, self.register_url, 60)
            self.sign_up(api)
            # 已进入/usr界面 尽最大努力加载页面中的js元素
            self.wait(api, 40, 'all')
            # 点击商城转换页面
            try:
                self.wait(api, 10, self.xpath_page_shop)
                api.find_element_by_xpath(self.xpath_page_shop).click()
            # 弹窗遮盖
            except ElementClickInterceptedException:
                time.sleep(0.5)
                api.find_element_by_xpath("//button").click()
                time.sleep(0.5)

                # 点击商城转换页面至/shop界面，again
                self.wait(api, 10, self.xpath_page_shop)
                api.find_element_by_xpath(self.xpath_page_shop).click()
            # 免费计划识别 购买免费计划
            try:
                self.wait(api, 3, self.xpath_button_buy)
                api.find_element_by_xpath(self.xpath_button_buy).click()

                # 回到主页
                time.sleep(1)
                api.get(self.register_url)

                # 获取链接
                time.sleep(1)
                self.wait(api, 40, self.xpath_canvas_subs)
                self.capture_subscribe(api)
            except TimeoutException:
                return False
        finally:
            api.quit()


class PrismV2(ActionMasterGeneral):
    def __init__(self, register_url, silence=True, assault=False):
        super(PrismV2, self).__init__(silence=silence, assault=assault)

        self.register_url = register_url
        self.action_name = "Action{}Cloud".format(urlparse(self.register_url).netloc.title().replace(".", ""))
        self.identity = ""

    def verify(self, api: Chrome):
        time.sleep(1)
        res_text = api.page_source
        if "已经有账号了" in res_text:
            if ("geetest" in res_text) and ("滑动" in res_text):
                self.identity = "crack"
            else:
                self.identity = "None"
        elif api.find_element_by_id("email_verify") or api.find_element_by_id("send-code"):
            self.identity = "email"
        elif "recaptcha" in api.find_element_by_xpath("//div//iframe").get_attribute("src"):
            self.identity = "recaptcha"
        else:
            self.identity = "unknown"

    def divide_and_rule(self):
        if self.identity == "None":
            self.anti_slider = False
        elif self.identity == "crack":
            self.anti_slider = True
        elif self.identity == "email":
            pass
        elif self.identity == "recaptcha":
            pass
        elif self.identity == "unknown":
            pass

    def run(self, api=None):
        logger.info("DO -- <{}>:beat_sync:{}".format(self.action_name, self.beat_sync))
        api = self.set_spider_option() if api is None else api
        try:
            self.get_html_handle(api, self.register_url, 60)
            self.verify(api)
            print(self.identity)
            self.divide_and_rule()
            self.sign_up(api)
        finally:
            api.quit()
