# -*- coding: utf-8 -*-
# Time       : 2021/12/14 21:20
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import random
import time

# from undetected_chromedriver.v2 import Chrome, ChromeOptions
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait


class EmailRelay:
    def __init__(self, url: str = "https://www.linshiyouxiang.net/",
                 chromedriver_path: str = "chromedriver", silence: bool = True):
        self.register_url = url
        self.chromedriver_path = chromedriver_path

        self.silence = silence
        self.pending_domains = ["@bytetutorials.net", "@iffygame.com", "@maileven.com",
                                "@smuggroup.com", "@chapedia.net", "@worldzipcodes.net",
                                "@chapedia.org"]
        self.mailbox_link = "https://www.linshiyouxiang.net/mailbox/{}"
        self.email_driver = "admin@rookie.it"
        self.email_id = "admin"

    def set_spider_option(self) -> Chrome:
        options = ChromeOptions()

        # 静默启动
        if self.silence is True:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")

        api = Chrome(options=options, executable_path=self.chromedriver_path)
        return api

    @staticmethod
    def get_html_handle(api: Chrome, url, wait_seconds: int = 15):
        api.set_page_load_timeout(time_to_wait=wait_seconds)
        api.get(url)

    def get_temp_email(self, api: Chrome, timeout: int = 10):
        time.sleep(1)
        if self.silence:
            api.save_screenshot("haha.png")

        activate_email: str = WebDriverWait(api, timeout).until(presence_of_element_located((
            By.TAG_NAME, "input"
        ))).get_attribute("data-clipboard-text")

        self.email_id = activate_email.split("@")[0]

        self.email_driver = self.email_id + random.choice(self.pending_domains)
        return self.email_driver

    @staticmethod
    def check_receive(api: Chrome):
        while True:
            checker_tag: str = api.find_elements(By.XPATH, "//tbody//td[@class='text-center']")
            if checker_tag.__len__() != 1:
                return True
            time.sleep(2)

    @staticmethod
    def switch_to_mail(api: Chrome):
        while True:
            details_tag = api.find_elements(By.XPATH, "//tbody//td[@class='text-center']//a")
            if details_tag:
                details_tag[0].click()
                return True
            time.sleep(1)

    @staticmethod
    def get_number(api: Chrome):
        while True:
            content_box = api.find_elements(By.XPATH, "//td[@valign='top']//span")
            if content_box:
                for i in content_box:
                    pending_str: str = i.text
                    if pending_str.isdigit():
                        return pending_str
            time.sleep(1)


def apis_get_verification_code(link: str, chromedriver_path: str = None, driver=None, silence=True) -> str:
    """

    :param driver:
    :param chromedriver_path:
    :param silence:
    :param link: apis_get_email_context() 上下文键值对 link
    :return:
    """
    chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path
    er = EmailRelay(
        url=link,
        chromedriver_path=chromedriver_path,
        silence=silence
    )
    api = er.set_spider_option() if driver is None else driver

    try:
        er.get_html_handle(api, er.register_url)
        er.check_receive(api)
        er.switch_to_mail(api)
        verification_code = er.get_number(api)

        return verification_code
    finally:
        api.quit()


def apis_get_email_context(chromedriver_path: str = None, silence: bool = True) -> dict:
    """

    :param chromedriver_path:
    :param silence:
    :return:
    """
    chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path

    er = EmailRelay(
        chromedriver_path=chromedriver_path,
        silence=silence
    )
    api = er.set_spider_option()

    try:
        er.get_html_handle(api, er.register_url)
        er.get_temp_email(api)
        context = {
            "email": er.email_driver,
            "id": er.email_id,
            "link": er.mailbox_link.format(er.email_id),
        }
        return context
    finally:
        api.quit()
