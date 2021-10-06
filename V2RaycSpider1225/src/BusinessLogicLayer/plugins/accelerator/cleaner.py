"""
- 核心功能
    - 订阅池清洗维护
    - 识别不可用链接并剔除
"""
import base64
import warnings
from typing import List

import requests
from redis import exceptions as redis_error

from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.setting import REDIS_SECRET_KEY, CRAWLER_SEQUENCE, logger, terminal_echo
from .core import CoroutineSpeedup

WHITELIST = [
    "www.kaikaiyun.cyou"
]


class SubscribesCleaner(CoroutineSpeedup):
    """解耦清洗插件：国内IP调用很可能出现性能滑坡"""

    def __init__(self, debug=False, whitelist: list = None):
        """

        :param debug:
        :param whitelist: 白名单，包含 whitelist 特征的链接不被主动清扫
        """
        super(SubscribesCleaner, self).__init__()
        self.debug = debug
        self.keys = [REDIS_SECRET_KEY.format(s) for s in CRAWLER_SEQUENCE]
        self.rc = RedisClient().get_driver()
        self.whitelist = whitelist if whitelist else WHITELIST

    def offload_task(self):
        for key_ in self.keys:
            try:
                for sub, _ in self.rc.hgetall(key_).items():
                    self.work_q.put_nowait([sub, key_])
            except redis_error.ResponseError:
                logger.critical("Link pool is broken down.")

    def _del_subs(self, key_: str, subs: str, err_) -> None:
        try:
            # 白名单对象，拒绝清除
            if subs in self.whitelist:
                logger.info(f"<SubscribeCleaner> Mission pass cause by whitelist:{self.whitelist} | {subs}")
            else:
                self.rc.hdel(key_, subs)
                # terminal_echo(f"detach -> {subs} {err_}", 3)
                logger.debug(f"<SubscribeCleaner> detach -> {subs} {err_}")
        except redis_error.ConnectionError:
            logger.critical("<SubscribeCleaner> The local network communication is abnormal.")

    def control_driver(self, sub_info: List[str], threshold: int = 4):
        """

        :param sub_info: [subs,key_secret_class]
        :param threshold: 解耦置信阈值 小于或等于这个值的订阅将被剔除
        :return:
        """
        super(SubscribesCleaner, self).control_driver(task=sub_info)
        try:
            # 解析订阅
            node_info: dict = SubscribeParser(sub_info[0]).parse_subscribe()
            # 订阅解耦
            if node_info['nodes'].__len__() <= threshold:
                self._del_subs(sub_info[-1], sub_info[0], "decouple active removal")
            elif self.debug:
                terminal_echo(f"valid -- {node_info['subs']} -- {len(node_info['nodes'])}", 1)
        except (UnicodeDecodeError, TypeError) as e:
            # 对于已标记“解析错误”的订阅 更新其请求次数
            if self.temp_cache.get(sub_info[0]):
                self.temp_cache[sub_info[0]] += 1
            # 否则标记为“解析错误”的订阅
            else:
                terminal_echo(f"recheck -- {sub_info[0]}", 2)
                self.temp_cache[sub_info[0]] = 1
            # 若链接重试次数少于3次 重添加至任务队列尾部
            if self.temp_cache[sub_info[0]] <= 3:
                self.work_q.put_nowait(sub_info)
            # 若链接重试次数大于3次 剔除
            else:
                self._del_subs(sub_info[-1], sub_info[0], e)
        except SystemExit:
            warnings.warn("请关闭系统代理后部署订阅清洗任务")
        except Exception as e:
            logger.warning(f"{sub_info} -- {e}")
            self._del_subs(sub_info[-1], sub_info[0], e)

    def killer(self):
        if not self.debug:
            logger.success("<SubscribesCleaner> --> decouple compete.")


class SubscribeParser:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def is_subscribe(url: str):
        protocol = url.split("://", 1)[0]
        if protocol.startswith("http"):
            return True
        return False

    def parse_subscribe(self, subscribe: str = None, auto_base64=False) -> dict:
        """
        将订阅链接解析成节点数据
        :param subscribe:
        :param auto_base64:
        :return: {'subs': subscribe, "nodes": nodes}
        """

        subscribe = self.url if subscribe is None else subscribe
        # 提取有效解析内容
        subscribe = subscribe.split("&")[0]

        # 订阅类型
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53",
        }
        # 流量不通过系统代理
        proxies = {'http': None, 'https': None}
        try:
            # 拉取订阅
            session = requests.session()
            res = session.get(subscribe, headers=headers, proxies=proxies)

            # 解析订阅
            nodes_bytes = base64.decodebytes(res.content)
            nodes = [self.parse_share_link(i, auto_base64)['msg'] for i in nodes_bytes.decode("utf8").split("\n") if i]

            return {'subs': subscribe, "nodes": nodes}

        # 捕获异常输入 剔除恶意链接或脏数据
        # f'{subscribe} -- 传入的subs格式有误或不是订阅链接
        except requests.exceptions.MissingSchema:
            pass
        # 链接清洗任务不能使用代理IP操作
        except requests.exceptions.ProxyError:
            raise SystemExit
        # 1.远程主机关闭通信窗口，可能原因是 并发数过大；
        # 2.IP被封禁，可能原因是 目标站点拒绝国内IP访问；
        # 3.IP被拦截，可能原因是 目标站点拒绝代理访问；
        except requests.exceptions.ConnectionError:
            raise TypeError
        # 未知风险
        except requests.exceptions.RequestException as e:
            logger.error(f"{subscribe} -- {e}")

    def parse_share_link(self, node: str = None, auto_parse: bool = True) -> dict:
        """

        :param auto_parse: 自动进行 BASE64 解密工作
        :param node: node of share link ,like this vmess:// ssr://
        :return:
        """
        # 读取协议头以及正文信息
        node = self.url if node is None else node
        class_, body = node.split('://', 1)

        # 补全非标准格式 BASE64 编码
        body: str = body if body.endswith("==") else f"{body}=="

        if auto_parse:
            share_link: str = base64.b64decode(body).decode("utf8")
            return {"msg": share_link, "protocol": class_}
        return {"msg": body, "protocol": class_}

    def parse_out(self, auto_base64=True) -> dict:
        response = self.is_subscribe(self.url)
        return {
            "is_subscribe": response,
            "body": self.parse_subscribe(auto_base64=auto_base64) if response else self.parse_share_link()
        }
