# -*- coding: utf-8 -*-
# Time       : 2021/12/22 0:10
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import redis
from redis.exceptions import ConnectionError

from services.settings import REDIS_NODE, logger
from services.utils import ToolBox


class RedisClient:
    def __init__(
        self,
        host=REDIS_NODE["host"],
        port=REDIS_NODE["port"],
        password=REDIS_NODE["password"],
        db=REDIS_NODE["db"],
        **kwargs,
    ) -> None:
        self.db = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            db=db,
            health_check_interval=30,
            **kwargs,
        )

        # 兼容服务
        self.PREFIX_ALIAS = "v2rss:alias"

        # 特征服务
        self.PREFIX_SUBSCRIBE = "v2rayc_spider:v2ray"
        self.PREFIX_API = "sspanel:apis:"
        self.PREFIX_DETACH = "sspanel:detach"
        self.PREFIX_ENTROPY = "sspanel:entropy"
        self.PREFIX_CAPACITY = "sspanel:pool_cap"

        self.PREFIX_STREAM = "sspanel:synergy"

        self.INSTANCE = "V2RSS云彩姬"

    def ping(self) -> bool:
        try:
            return self.db.ping()
        except (ConnectionResetError, ConnectionError):
            return False

    def __len__(self):
        try:
            return self.db.hlen(self.PREFIX_SUBSCRIBE)
        except (ConnectionResetError, ConnectionError):
            logger.error(
                ToolBox.runtime_report(
                    motive="ConnectionError",
                    action_name="StreamIO",
                    message="Redis 远程主机关闭了一个现有连接，本地网络可能出现异常。",
                )
            )
            return 0
