# -*- coding: utf-8 -*-
# Time       : 2021/7/30 4:01
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: Adaptive acquisition framework
import csv
import json
import os
import time
from datetime import datetime

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.by import By

from BusinessCentralLayer.setting import logger, SERVER_DIR_DATABASE_CACHE
from .master import ActionMasterGeneral


class Prism(ActionMasterGeneral):
    def __init__(self, atomic: dict, silence=True, assault=True):
        super(Prism, self).__init__(silence=silence, assault=assault)

        atomic = {} if atomic is None else atomic

        self.register_url = (
            "" if atomic.get("register_url") is None else atomic.get("register_url")
        )
        self.hyper_params = (
            {} if atomic.get("hyper_params") is None else atomic.get("hyper_params")
        )
        self.action_name = (
            "PrismInstance" if atomic.get("name") is None else atomic.get("name")
        )
        self.life_cycle = (
            1 if atomic.get("life_cycle") is None else atomic.get("life_cycle")
        )
        self.anti_slider = (
            True if atomic.get("anti_slider") is None else atomic.get("anti_slider")
        )
        self.atomic = atomic

        self.xpath_page_shop = "//div[contains(@onclick,'shop')]"
        self.xpath_button_buy = "//a[contains(@onclick,'buyConfirm')]"
        self.xpath_canvas_subs = "//div[@class='card-body']"

    def run(self, api=None):
        logger.debug(self.runtime_flag(self.hyper_params))
        api = self.set_spider_option() if api is None else api
        if not api:
            return
        try:
            self.get_html_handle(api, self.register_url, 60)
            self.sign_up(api)
            # 已进入/usr界面 尽最大努力加载页面中的js元素
            self.wait(api, 40, "all")
            # 点击商城转换页面
            try:
                self.wait(api, 10, self.xpath_page_shop)
                api.find_element(By.XPATH, self.xpath_page_shop).click()
            except TimeoutException:
                logger.error(
                    f">>> TimeoutException <{self.action_name}> -- {self.register_url} -- 商城转换页面超时"
                )
            # 弹窗遮盖
            except ElementClickInterceptedException:
                time.sleep(0.5)
                api.find_element(By.XPATH, "//button").click()
                time.sleep(0.5)

                # 点击商城转换页面至/shop界面，again
                self.wait(api, 10, self.xpath_page_shop)
                api.find_element(By.XPATH, self.xpath_page_shop).click()
            # 免费计划识别 购买免费计划
            try:
                self.wait(api, 3, self.xpath_button_buy)
                api.find_element(By.XPATH, self.xpath_button_buy).click()

                # 回到主页
                time.sleep(1)
                api.get(self.register_url)

                # 获取链接
                time.sleep(1)
                self.wait(api, 40, self.xpath_canvas_subs)
                self.capture_share_link(api)
            except TimeoutException:
                return False
        finally:
            api.quit()


class ServiceDiscovery(ActionMasterGeneral):
    def __init__(
        self,
        register_url,
        subs_type: str = None,
        silence=True,
        output_path_csv: str = None,
    ):
        """

        :param register_url: 注册链接
        :param subs_type: 订阅类型 可选项：v2ray,ssr,ss,...
        :param silence:
        :param output_path_csv: 在并发作业时指定，能够将相互独立的运行实例的持久化数据指向同一个数据文件
        """
        super(ServiceDiscovery, self).__init__(
            silence=silence, assault=True, endurance=False
        )

        # 注册链接
        self.register_url = register_url
        # 任务别名
        self.action_name = "ServiceDiscovery"
        # self.action_name = "Action{}Cloud".format(urlparse(self.register_url).netloc.title().replace(".", ""))
        # 订阅类型 可选项：v2ray,ssr,ss,...
        self.subs_type = "v2ray" if subs_type is None else subs_type

        # =====================================================
        # Setting of Runtime Report
        # =====================================================
        self.report_title = [
            "provider",
            "subType",
            "passable",
            "enDay",
            "enFlow",
            "nodeNum",
            "context",
        ]

        # Stitch the cache path of the runtime report.
        if output_path_csv is None:
            output_path_csv = f"runtime_report_{str(datetime.now()).split(' ')[0]}_{str(time.time()).split('.')[0]}.csv"
            self.output_path_csv = os.path.join(
                SERVER_DIR_DATABASE_CACHE, output_path_csv
            )
        else:
            self.output_path_csv = output_path_csv
        self._create_cache_heap(self.output_path_csv)

    def _create_cache_heap(self, output_path_csv):
        if not os.path.exists(output_path_csv):
            with open(output_path_csv, "w", encoding="utf8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.report_title)

    @logger.catch()
    def get_share_link(self, api=None):
        logger.info(
            "<ServiceDiscovery> silence={} assault={} endurance={} url={}".format(
                self.silence,
                self.assault,
                self.endurance,
                self.register_url,
            )
        )

        # 获取 ChromeDriver 操作句柄
        api = self.set_spider_option() if api is None else api
        if not api:
            return

        try:
            self.get_html_handle(api, self.register_url, 60)
            # 重构特征词典
            self.rebuild_user(api)
            self.sign_up(api)
            self.wait(api, 40, "//div[@class='card-body']")
            # 目标不开放对应类型订阅
            if not self.rebuild_policy(api, self.subs_type):
                return self.subscribe
            self.capture_share_link(api)
            return self.subscribe
        except RuntimeError as e:
            logger.error(
                "<ServiceDiscovery> The task strategy does not match, "
                f"and there is a mismatched task in the workflow.{e}"
                f"jobId=<{self.action_name}> subType={self.subs_type} url={self.register_url} "
            )
        except TimeoutException:
            logger.error(f"<ServiceDiscovery> TimeoutException url={self.register_url}")
        except UnexpectedAlertPresentException as e:
            logger.error(f"<ServiceDiscovery> {e.alert_text} url={self.register_url}")
        finally:
            api.quit()

    def get_runtime_report(self, share_type="v2ray") -> dict:
        """

        :param share_type:
        :return:
        """
        from ..plugins.accelerator import SubscribeParser

        # Context details about the sample site.
        details = {
            "provider": self.register_url,
            "subType": share_type,
            "passable": "no",
            "enDay": "nil",
            "enFlow": "nil",
            "nodeNum": "0",
            "context": "nil",
        }

        # Obtain the subscribed link with the type `share_type` from the sample site.
        if not self.get_share_link():
            return details
        details["provider"] = self.subscribe

        # Parse subscribed link.
        result = SubscribeParser(self.subscribe).parse_subscribe(auto_base64=True)

        # Convert data type: strField --> Dict
        nodes = [dict(json.loads(node)) for node in reversed(result.get("nodes"))]

        # Get the number of available nodes.
        node_num = nodes.__len__() - 2 if nodes.__len__() - 2 >= 0 else 0
        details["nodeNum"] = str(node_num)
        details["passable"] = "no" if node_num <= 1 else "yes"

        # if details['passable'] == "yes":
        if nodes:
            try:
                details["context"] = str(nodes[:-2]) if nodes[:-2] else "nil"
                details["enDay"] = [
                    i.get("remark") for i in nodes if "时间" in i.get("remark")
                ][0]
                details["enFlow"] = [
                    i.get("remark") for i in nodes if "流量" in i.get("remark")
                ][0]
            except IndexError:
                pass
        return details

    def save_runtime_report(self, reports: list):
        """

        :param reports:
        :return:
        """
        # The variable `reports` must be a nested list. Like this Reports[report1, report2, ...]
        if isinstance(reports[0], str):
            reports = [
                reports,
            ]
        # 写模式设定，如果运行模式是在并发作业中存储，则为 "a"，否则为 "w"，也即完成任务后一次性读取缓存
        with open(self.output_path_csv, "a", encoding="utf8", newline="") as f:
            # 捕获运行缓存
            writer = csv.writer(f)
            for r in reports:
                writer.writerow(r)
        # 返回缓存路径
        return self.output_path_csv
