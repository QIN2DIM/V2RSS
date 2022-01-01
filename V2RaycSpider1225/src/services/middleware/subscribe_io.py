# -*- coding: utf-8 -*-
# Time       : 2021/12/22 9:07
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from collections import Counter
from typing import Dict, List
from urllib.parse import urlparse

from redis.exceptions import ConnectionError, RedisError

from services.middleware.stream_io import RedisClient
from services.settings import logger
from services.utils import ToolBox


class SubscribeManager(RedisClient):
    """缓存订阅的CRUD"""

    def __init__(self):
        super(SubscribeManager, self).__init__()

    def set_alias(self, alias: str, netloc: str):
        """
        获取订阅别名

        :param netloc: 网址的 netloc/domain
        :param alias: 别名，暂定 ActionName
        :return:
        """
        self.db.hset(self.PREFIX_ALIAS, netloc, alias)

    def get_alias(self, netloc: str) -> str:
        """
        获取订阅别名

        :param netloc: 网址的 netloc/domain
        :return:
        """
        alias = self.db.hgetall(self.PREFIX_ALIAS)
        return alias.get(netloc, "") if alias else ""

    def get_pool_status(self) -> Dict[str, int]:
        """
        获取缓存中的活跃订阅状态

        :return: {"ActionAlias":Active number}
        """
        return dict(Counter([self.db.hgetall(self.PREFIX_ALIAS)[urlparse(url).netloc] for url in self.sync()]))

    def add(self, subscribe: str, life_cycle: int, threshold: int = 0):
        """
        添加订阅

        :param threshold: 视为将原定的结束时间提前 x 小时。
        :param subscribe:
        :param life_cycle:
        :return:
        """
        # Calculate ``life_cycle`` of the ``subscribe_url``.
        life_cycle -= threshold
        end_date = ToolBox.date_format_life_cycle(life_cycle)

        # Cache a ``subscribe_url`` that bind the available time.
        for _ in range(3):
            try:
                self.db.hset(self.PREFIX_SUBSCRIBE, subscribe, end_date)
                break
            except (ConnectionError, RedisError) as e:
                logger.error(e)

    def detach(self, subscribe: str, transfer: bool = True, motive: str = None):
        """
        移除订阅

        :param motive:
        :param subscribe:
        :param transfer: 规定系统移除置 False，系统分发置为 True
            - True：拷贝被删除的订阅
            - False：仅删除
        :return:
        """

        motive = "detach" if motive is None else motive
        motive = "del" if transfer is False else motive

        # Delete subscribe
        self.db.hdel(self.PREFIX_SUBSCRIBE, subscribe)

        # Transfer subscribe
        if transfer is True:
            date_now = ToolBox.date_format_now()
            self.db.hset(self.PREFIX_DETACH, subscribe, date_now)

        logger.debug(f"{motive}-(subscribe)-({subscribe})")

    def refresh(self) -> int:
        """
        连接池刷新，去除过期订阅

        :return: 返回更新后的剩余订阅数
        """
        try:
            docker: dict = self.db.hgetall(self.PREFIX_SUBSCRIBE)
            if docker:
                for subscribe, end_date in docker.items():
                    if ToolBox.is_stale_date(end_date):
                        self.detach(subscribe, transfer=False, motive="refresh")
        except (ConnectionResetError, ConnectionError):
            pass
        return self.__len__()

    def update_api_status(self, api_name) -> bool:
        """
        更新 API 函数调用情况

        :param api_name:
        :return:
        """
        if api_name not in ["select", "get", "search", "decouple", "reset"]:
            return False

        date_now = ToolBox.date_format_now()
        self.db.rpush(f"{self.PREFIX_API}{api_name}", date_now)
        self.db.incr(f"{self.PREFIX_API}{api_name}_num")
        return True

    def sync(self) -> List[str]:
        url2life_cycle: dict = self.db.hgetall(self.PREFIX_SUBSCRIBE)
        if url2life_cycle:
            urls = list(url2life_cycle.keys())
            return urls
        return []
