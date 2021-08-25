# -*- coding: utf-8 -*-
# Time       : 2021/7/25 13:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

import json
import os
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from selenium.webdriver import Chrome

from src.BusinessCentralLayer.setting import logger, SERVER_DIR_DATABASE, TIME_ZONE_CN
from src.BusinessLogicLayer.cluster.master import ActionMasterGeneral


class SSPanelParser(ActionMasterGeneral):
    def __init__(self, url, silence=False, assault=True, anti_slider=True):
        super(SSPanelParser, self).__init__(url, silence, assault, anti_slider=anti_slider, )

        self.obj_parser = {}
        self.cache_db_name = "parser_cache"
        self.cache_db_path = self.create_cache_db(database_dir=SERVER_DIR_DATABASE)

    def create_cache_db(self, database_dir=None):
        database_dir = "database" if database_dir is None else database_dir

        if not os.path.exists(database_dir):
            os.mkdir(database_dir)

        cache_db = os.path.join(database_dir, self.cache_db_name)
        if not os.path.exists(cache_db):
            os.mkdir(cache_db)
        return cache_db

    def capture_cache(self, signs, flow):
        output_path = os.path.join(self.cache_db_path, signs)
        with open(output_path, 'w', encoding="utf8") as f:
            f.write(flow)

    def parse(self, **kwargs):
        """
        :return:
        """
        api: Chrome = kwargs.get("api")
        self.obj_parser.update({"parse_url": self.register_url})
        # ----------------------------------------
        # 解析可用流量和可用时长
        # 优先调用，等待流体动画加载完成[耗时任务]
        # 以保证后续解析无需等待
        # ----------------------------------------
        fluid = set()
        fluid_density = []
        i = 0
        while True:
            try:
                i += 1
                card_body = api.find_elements_by_xpath("//div[@class='card-body']")[:2]
                card_body = [tag.text.strip() for tag in card_body]
                fluid.update(card_body)
                fluid_density.append(len(fluid))
                # 流体释放
                if len(fluid_density) < 10 or len(fluid) < 3:
                    continue
                # 流体相对均衡
                if max(fluid_density[:10]) == min(fluid_density[:10]):
                    self.obj_parser.update({"time": card_body[0], "flow": card_body[-1]})
                    break
            except StaleElementReferenceException:
                pass
        # 存储cookie
        with open("123.json", "w", encoding="utf8") as f:
            f.write(json.dumps(api.get_cookies()))
        # 读取cookie
        # cookie_json = " ".join([f"{i['name']}={i['value']};" for i in json.loads(f.read())])
        # ----------------------------------------
        # 解析站点名称
        # ----------------------------------------
        try:
            parse_name = api.find_element_by_xpath("//aside//div[@class='sidebar-brand']").text.strip()
            self.obj_parser.update({"parse_name": parse_name})
        except WebDriverException:
            logger.error(f"<SSPanelParserError> Site name resolution failed -- {self.register_url}")
        # ----------------------------------------
        # 解析站点公告
        # ----------------------------------------
        reference_links = {}
        try:
            card_body = api.find_elements_by_xpath("//div[@class='card-body']")[4]
            self.obj_parser.update({"desc": card_body.text.strip()})

            related_href = card_body.find_elements_by_tag_name("a")
            for tag in related_href:
                href = tag.get_attribute("href")
                if href:
                    href = href.strip()
                    if "https" not in href:
                        href = f"{self.register_url}{href}"
                    href_desc = tag.text.strip() if tag.text else href
                    reference_links.update({href: href_desc})
            self.obj_parser.update({"reference_links": reference_links})
        except WebDriverException:
            logger.error(f"<SSPanelParserError> Site announcement parsing error -- {self.register_url}")

        # ----------------------------------------
        # 解析[链接导入]
        # ----------------------------------------
        subscribes = {}
        support = []
        try:
            # 清洗订阅链接
            soup = BeautifulSoup(api.page_source, 'html.parser')
            for i in soup.find_all("a"):
                if i.get("data-clipboard-text"):
                    subscribes.update({i.get("data-clipboard-text"): i.text.strip()})
            # 识别支持的订阅类型
            buttons = api.find_elements_by_xpath("//div[@class='card'][2]//a")
            for tag in buttons:
                support_ = tag.get_attribute("class")
                if support_:
                    support_ = [i for i in [i for i in support_.split() if i.startswith("btn-")] if
                                i not in ['btn-icon', 'btn-primary', 'btn-lg', 'btn-round', 'btn-progress']]
                    if len(support_) == 1:
                        class_name = support_[0].replace("btn-", "")
                        support.append(class_name)
            # 残差补全
            for tag in subscribes.values():
                if "surge" in tag.lower():
                    support.append("surge")
                if "ssr" in tag.lower():
                    support.append("ssr")
            self.obj_parser.update({"subscribes": subscribes, "support": list(set(support))})
        except WebDriverException:
            logger.error(f"<SSPanelParserError> Site subscription resolution failed -- {self.register_url}")

        self.obj_parser.update(
            {
                "email": self.email,
                "password": self.password,
                "recently_login": datetime.now(tz=TIME_ZONE_CN)
            }
        )

        return self.obj_parser

    def parse_by_login(self, **kwargs) -> dict:
        return self.seep('login', self.parse, **kwargs)

    def parse_by_register(self, **kwargs):
        return self.seep('register', self.parse, **kwargs)

    def refresh_cookie(self, **kwargs):

        def get_cookie():
            cookies = kwargs.get("api")
            return json.dumps(cookies.get_cookies()) if cookies else {}

        return self.seep('login', get_cookie, **kwargs)

    def seep(self, method, business, **kwargs):
        # 获取任务设置
        api = self.set_spider_option()
        # 执行核心业务逻辑
        try:
            self.get_html_handle(api=api, url=self.register_url, wait_seconds=45)
            if method == 'login':
                self.sign_in(api, **kwargs)
            elif method == 'register':
                self.sign_up(api)
            self.wait(api, 40, "//div[@class='card-body']")
            kwargs.setdefault("api", api)
            return business(**kwargs)
        finally:
            api.quit()
