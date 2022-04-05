import urllib.request

from bs4 import BeautifulSoup
from cloudscraper import create_scraper
from cloudscraper.exceptions import CloudflareChallengeError
from loguru import logger
from requests import Response
from requests.exceptions import SSLError, HTTPError, Timeout, ProxyError, ConnectionError

from .booster import CoroutineSpeedup, Queue


class SSPanelHostsClassifier(CoroutineSpeedup):
    def __init__(self, docker: list = None, debug=True):
        """

        :param docker:
        :param debug:
        """
        super().__init__(docker=docker)
        self.local_proxy = urllib.request.getproxies()
        logger.debug("本机代理状态 PROXY={}".format(self.local_proxy))

        self.done = Queue()
        self.headers = {"accept-language": "zh-CN"}

        self.context = {
            # 直连链接
            "url": "",
            # 样本标签
            "label": "",
            # 样本别名
            "alias": "",
        }

        self.debug = debug

    def _fall_status(self, status_code: int, url: str):
        """
         规则：判断状态异常

        :param status_code:
        :param url:
        :return:
        """
        if status_code > 400 or status_code == 302:
            logger.error(
                self.report(
                    message="请求异常",
                    context={"url": url, "label": f"请求异常(ERROR:{status_code})"},
                    url=url,
                )
            )
            return False
        return True

    def _fall_register_closed(self, soup: BeautifulSoup, url: str):
        """
        规则：判断关闭注册接口或结构非范式的站点

        :param soup:
        :param url:
        :return:
        """
        if "closed" in soup.text or not soup.find(id="passwd"):
            logger.warning(
                self.report(
                    message="拒绝注册", context={"url": url, "label": "拒绝注册"}, url=url
                )
            )
            return False
        return True

    def _fall_register_limit_by_email(self, soup: BeautifulSoup, url: str):
        """
        规则：判断限定注册邮箱域名的站点

        :param soup:
        :param url:
        :return:
        """
        if soup.find("select") and soup.find(id="email_verify"):
            logger.info(
                self.report(
                    message="限制注册", context={"url": url, "label": "限制注册(邮箱)"}, url=url
                )
            )
            return False
        return True

    def _fall_register_limit_by_code(self, response: Response, url: str):
        """
        规则：判断需要邀请码注册的站点

        :return:
        """
        if (
            "Please fill in invitation code" in response.text
            or "请填写邀请码" in response.text
            or "邀请码（必填）" in response.text
            or "邀请码(必填)" in response.text
        ):
            logger.info(
                self.report(
                    message="限制注册", context={"url": url, "label": "限制注册(邀请)"}, url=url
                )
            )
            return False
        return True

    def _fine_node(self, response: Response, soup: BeautifulSoup, url: str):
        """
        标注正常站点

        :param response:
        :param soup:
        :param url:
        :return:
        """
        labels_ = []
        if "grecaptcha.get" in response.text:
            labels_.append("Google reCAPTCHA")
        if soup.find(id="email_verify"):
            labels_.append("Email Validation")
        if "geetest" in response.text:
            labels_.append("GeeTest Validation")
        if not labels_:
            labels_.append("Normal")

        _preview_log = self.report(
            message="实例正常", context={"url": url, "label": ";".join(labels_)}, url=url
        )
        if self.debug:
            logger.success(_preview_log)
        return True

    def _fall_danger(self, url: str):
        if not url.startswith("https://"):
            logger.warning(
                self.report(
                    message="危险通信", context={"url": url, "label": "危险通信(HTTP)"}, url=url
                )
            )
            return False
        return True

    def report(self, message: str, context: dict = None, **flags) -> str:
        """
        格式化运行日志，缓存上下文摘要信息

        :param message:
        :param context:
        :param flags:
        :return:
        """

        # 缓存上下文数据流
        if isinstance(context, dict):
            if context.get("url") and context.get("label"):
                self.done.put_nowait(context)

        # 格式化运行日志
        _content = f"{message} - [{self.progress()}] "
        if flags:
            _content += " ".join([f"{i[0]}={i[1]}" for i in flags.items()])
        return _content

    def handle_html(self, url: str, allow_redirects: bool = False):
        """

        :param allow_redirects:
        :param url:
        :return:
        """
        scraper = create_scraper()
        response = scraper.get(
            url, timeout=60, allow_redirects=allow_redirects, headers=self.headers
        )
        status_code = response.status_code
        soup = BeautifulSoup(response.text, "html.parser")
        return response, status_code, soup

    @logger.catch()
    def control_driver(self, url: str):
        # 剔除 http 直连站点
        if not self._fall_danger(url):
            return False
        try:
            response, status_code, soup = self.handle_html(url)

            # 状态异常的站点
            if not self._fall_status(status_code, url):
                return False

            # 关闭注册接口或结构非范式的站点
            if not self._fall_register_closed(soup, url):
                return False

            # 需要邀请码注册的站点
            if not self._fall_register_limit_by_code(response, url):
                return False

            # 限定注册邮箱域名的站点
            if not self._fall_register_limit_by_email(soup, url):
                return False

            # 标注正常站点
            return self._fine_node(response, soup, url)

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
