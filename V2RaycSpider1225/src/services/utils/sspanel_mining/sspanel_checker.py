# -*- coding: utf-8 -*-
# Time       : 2021/12/18 14:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

from urllib.parse import urlparse

from cloudscraper.exceptions import CloudflareChallengeError
from loguru import logger
from requests.exceptions import Timeout, ConnectionError, SSLError, HTTPError, ProxyError

from .sspanel_classifier import SSPanelHostsClassifier


class SSPanelStaffChecker(SSPanelHostsClassifier):
    def __init__(self, docker: list = None):
        super().__init__(docker=docker)

        self.path_register = "/auth/register"
        self.path_tos = "/tos"
        self.path_staff = "/staff"

        self.rookies = []

    def _fall_staff_page(self, url: str):
        staff_url = url + self.path_staff

        response, status_code, soup = self.handle_html(staff_url)
        logger.info(self.report(message="心跳检测", url=staff_url, status_code=status_code))

    def _fall_tos_page(self, url: str):
        url += self.path_tos

    def _fall_staff_footer(self, url: str):
        register_url = url + self.path_register

        context = {}

        response, status_code, soup = self.handle_html(register_url, allow_redirects=True)

        copyright_ = soup.find("div", class_="simple-footer")
        try:
            copyright_text = copyright_.text.strip()
            context.update({"url": register_url, "copyright": copyright_text, "ok": True})
        except AttributeError:
            pass
        if "sspanel" in response.text.lower():
            pass

        # 转发上下文评价数据
        if context.get("ok"):
            logger.success(
                self.report(
                    message="实例正常", url=context["url"], copyright=context["copyright"]
                )
            )
        else:
            logger.error(self.report(message="脚注异常", url=context["url"]))

    def _fall_rookie(self, url: str):
        response, status_code, soup = self.handle_html(url)
        context = {
            "url": url,
            "rookie": True
            if ("占位符" in soup.text or "。素质三连" in soup.text or "CXK" in soup.text)
            else False,
        }

        if context["rookie"]:
            logger.error(self.report(message="新手司机", url=url, rookie=context["rookie"]))
            self.rookies.append(context)
        else:
            logger.success(
                self.report(
                    message="走心好评",
                    url=url,
                    rookie=context["rookie"],
                    status_code=status_code,
                )
            )

    def preload(self):
        """
        数据增强

        在docker中拷贝一份子页链接用于广度访问
        :return:
        """
        _docker = []
        for url in self.docker:
            _parse_obj = urlparse(url)
            _url = f"{_parse_obj.scheme}://{_parse_obj.netloc}"
            _docker.append(_url)
        self.docker = _docker

    def control_driver(self, url: str):
        """

        :param url:
        :return:
        """
        try:
            self._fall_rookie(url)

        # 站点被动行为，流量无法过墙
        except ConnectionError:
            logger.error(self.report("流量阻断", url=url))
            return False
        # 站点主动行为，拒绝国内IP访问
        except (SSLError, HTTPError, ProxyError):
            logger.error(self.report("代理异常", url=url))
            return False
        # 未授权站点
        except ValueError:
            logger.critical(
                self.report(
                    message="危险通信", context={"url": url, "label": "未授权站点"}, url=url
                )
            )
            return False
        # <CloudflareDefense>被迫中断且无法跳过
        except CloudflareChallengeError:
            logger.debug(
                self.report(
                    message="检测失败",
                    context={"url": url, "label": "CloudflareDefenseV2"},
                    url=url,
                    error="<CloudflareDefense>被迫中断且无法跳过",
                )
            )
            return False
        # 站点负载紊乱或主要服务器已瘫痪
        except Timeout:
            logger.error(self.report("响应超时", url=url))
            return False

    def killer(self):
        logger.info(
            f"rookie_pre={round(len(self.rookies) * 100 / self.max_queue_size, 2)}%"
        )
