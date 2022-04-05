# -*- coding: utf-8 -*-
# Time       : 2021/12/22 9:07
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import time
from collections import Counter
from typing import Dict, List, Optional
from urllib.parse import urlparse

from redis.exceptions import RedisError

from services.middleware.stream_io import RedisClient
from services.settings import logger
from services.utils import ToolBox


class SubscribeManager(RedisClient):
    """缓存订阅的CRUD"""

    def set_alias(self, alias: str, netloc: str):
        """
        设置订阅别名

        :param netloc: 网址的 netloc/domain
        :param alias: 别名，暂定 ActionName
        :return:
        """
        self.db.hset(name=self.PREFIX_ALIAS, key=netloc, value=alias)

    def get_alias(self, netloc: str) -> str:
        """
        获取订阅别名

        :param netloc: 网址的 netloc/domain
        :return:
        """
        alias = self.db.hgetall(name=self.PREFIX_ALIAS)
        return alias.get(netloc, "") if alias else ""

    def get_pool_status(self) -> Dict[str, int]:
        """
        获取缓存中的活跃订阅状态

        :return: {"ActionAlias":Active number}
        """
        return dict(
            Counter(
                [
                    self.db.hgetall(self.PREFIX_ALIAS)[urlparse(url).netloc]
                    for url in self.sync()
                ]
            )
        )

    def add(self, subscribe: str, end_date: str, retry_times: Optional[int] = 60):
        """
        添加订阅

        :param retry_times:
        :param end_date:
        :param subscribe:
        :return:
        """

        # Cache a ``subscribe_url`` that bind the available time.
        for _ in range(retry_times):
            try:
                self.db.hset(self.PREFIX_SUBSCRIBE, subscribe, end_date)
                break
            except RedisError as e:
                logger.error(e)
                time.sleep(0.3)

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
        except RedisError:
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

    def sync(self) -> Optional[List[str]]:
        url2life_cycle: dict = self.db.hgetall(self.PREFIX_SUBSCRIBE)
        if url2life_cycle:
            urls = list(url2life_cycle.keys())
            return urls
        return []
