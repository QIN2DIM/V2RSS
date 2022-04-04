# -*- coding: utf-8 -*-
# Time       : 2021/12/22 9:04
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import json
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from cloudscraper import create_scraper
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import (
    presence_of_all_elements_located,
)
from selenium.webdriver.support.wait import WebDriverWait


class EmailCodeParser:
    @staticmethod
    def _pattern(context, mode=1):
        if mode == 1:
            return [i for i in re.split("[：，]", context) if i.isdigit()]
        elif mode == 2:
            return [i.strip() for i in context.split("\n") if i.strip().isdigit()]

    @staticmethod
    def patterns(url: str = None, email_body: str = None) -> str:

        _email_body = email_body
        if url:
            scraper = create_scraper()
            response = scraper.get(url)

            if response.status_code != 200:
                return ""

            _email_body = response.text

        soup = BeautifulSoup(_email_body, "html.parser")
        context = soup.text

        for mode in range(1, 3):
            email_code = EmailCodeParser._pattern(context, mode)
            if not email_code:
                continue
            return email_code[0]


class EmailRelay:
    def __init__(self, url: str = None):
        self.primary = "https://www.linshiyouxiang.net/" if url is None else url

        self.pending_domains = [
            "@bytetutorials.net",
            "@iffygame.com",
            "@maileven.com",
            "@smuggroup.com",
            "@chapedia.net",
            "@worldzipcodes.net",
            "@chapedia.org",
        ]
        self.mailbox_link = "https://www.linshiyouxiang.net/mailbox/{}"
        self.email_driver = "admin@rookie.it"
        self.email_id = "admin"

    def get_temp_email(self, api: Chrome, timeout: int = 45) -> str:
        start = time.time()
        while True:
            time.sleep(1)
            WebDriverWait(api, timeout).until(presence_of_all_elements_located)
            try:
                activate_email: str = api.find_element(
                    By.TAG_NAME, "input"
                ).get_attribute("data-clipboard-text")
                self.email_id = activate_email.split("@")[0]
            except NoSuchElementException:
                if "Cloudflare" in api.page_source:
                    return ""
            except AttributeError:
                if time.time() - start > timeout:
                    return ""
                api.refresh()
                time.sleep(3)
            else:
                self.email_driver = self.email_id + random.choice(self.pending_domains)
                return self.email_driver

    @staticmethod
    def check_receive(api: Chrome):
        start_time = time.time()

        while True:
            checker_tag = api.find_elements(By.XPATH, "//tbody//td[@class='text-center']")
            if checker_tag.__len__() != 1:
                return True
            if time.time() - start_time > 300:
                return False

            # 缩短邮件列表刷新时间
            time.sleep(3)
            try:
                api.find_element(By.XPATH, "//a[@data-original-title='刷新邮件列表']").click()
            except WebDriverException:
                pass

    @staticmethod
    def switch_to_mail(api: Chrome):
        while True:
            details_tag = api.find_elements(
                By.XPATH, "//tbody//td[@class='text-center']//a"
            )
            if details_tag:
                details_tag[0].click()
                if "google_" in api.current_url:
                    api.refresh()
                    time.sleep(1)
                    continue
                return True
            time.sleep(1)

    @staticmethod
    def get_number(api: Chrome):
        url = api.current_url
        email_code = EmailCodeParser.patterns(url)
        return email_code

    @staticmethod
    def get_numer_by_selenium(api: Chrome):
        pass

    def is_availability(self):
        response = requests.get(self.primary)
        if response.status_code != 200:
            return False
        return True


def apis_get_email_context(api: Chrome, main_handle) -> dict:
    """

    :param main_handle:
    :param api:
    :return:
    """

    er = EmailRelay()

    api.switch_to.new_window("tab")

    collaborate_tab = api.current_window_handle

    api.get(er.primary)

    er.get_temp_email(api)

    context = {
        "email": er.email_driver,
        "id": er.email_id,
        "link": er.mailbox_link.format(er.email_id),
        "handle": collaborate_tab,
    }

    api.switch_to.window(main_handle)

    return context


def apis_get_verification_code(
    api: Chrome, link: str, main_handle, collaborate_tab
) -> str:
    """

    :param collaborate_tab:
    :param main_handle:
    :param api:
    :param link: apis_get_email_context() 上下文键值对 link
    :return:
    """
    er = EmailRelay(link)

    api.switch_to.window(collaborate_tab)

    api.get(link)

    if er.check_receive(api):
        er.switch_to_mail(api)
        email_code = er.get_number(api)
    else:
        email_code = ""

    api.switch_to.window(main_handle)

    return email_code


class EmailRelayV2:
    def __init__(self):
        self.primary = "https://temp-mail.to/"
        self._mailbox_api = "https://temp-mail.to/a/mailbox"

        self._headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62"
        }

        self._temp_email_tab = None

    def _context_switch(self, api: Chrome, handle_obj=None):
        if handle_obj is None:
            api.switch_to.new_window("tab")
            self._temp_email_tab = api.current_window_handle
        else:
            api.switch_to.window(handle_obj)

    def _handle_token(self, api: Chrome):
        api.get(self.primary)

        WebDriverWait(
            api, 10, poll_frequency=0.5, ignored_exceptions=NoSuchElementException
        ).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='cta-refresh']//a"))
        ).click()

        WebDriverWait(
            api, 10, poll_frequency=0.5, ignored_exceptions=NoSuchElementException
        ).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@class='email-g']"))
        ).click()

        _cookie: str = "; ".join([f"{i['name']}={i['value']}" for i in api.get_cookies()])
        _token = api.get_cookie("XSRF-TOKEN")["value"].replace("%3D", "=")

        self._headers.update({"cookie": _cookie, "x-xsrf-token": _token})

    def _listen_email(self, ignore: bool = None) -> str:
        """

        :param ignore: True: 返回 Address， False: 监听来件
        :return:
        """
        scraper = create_scraper()
        response = scraper.post(self._mailbox_api, headers=self._headers)

        try:
            data: dict = response.json()
            if ignore is True:
                return data.get("address")
        except json.decoder.JSONDecodeError:
            print("data 解析失败 | status_code={}".format(response.status_code))
            return ""
        else:
            try:
                email_body = data["inbox"][-1]["body"]
            except (AttributeError, IndexError):
                return ""
            else:
                return email_body

    def is_availability(self) -> bool:
        response = requests.get(self.primary)
        if response.status_code != 200:
            return False
        return True

    def apis_get_temp_email(self, api: Chrome, handle_obj=None) -> dict:

        # 新建 TAB 作业
        self._context_switch(api, handle_obj=None)

        # 模拟登录获取身份认证信息
        self._handle_token(api)

        # 携带 TOKEN POST 获取临时邮箱账号
        address = self._listen_email(ignore=True)

        # 切换回 MAIN_TAB
        self._context_switch(api, handle_obj=handle_obj)

        context = {
            "email": address,
            "id": address.split("@")[0],
            "link": "",
            "handle": self._temp_email_tab,
        }

        return context

    def apis_get_email_code(self, timeout: int = 60) -> str:
        start = time.time()

        while True:
            # 超时
            if time.time() - start > timeout:
                return ""

            email_body = self._listen_email()

            # 空邮件
            if not email_body:
                time.sleep(3)
                continue

            # 来件
            return EmailCodeParser.patterns(email_body=email_body)
