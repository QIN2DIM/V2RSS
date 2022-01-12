# -*- coding: utf-8 -*-
# Time       : 2021/12/22 16:15
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import ast
from datetime import timedelta, datetime
from typing import List

from redis.exceptions import ConnectionError, ResponseError

from services.middleware.stream_io import RedisClient
from services.settings import TIME_ZONE_CN


class EntropyHeap(RedisClient):
    def __init__(self):
        super(EntropyHeap, self).__init__()

    def update(self, local_entropy: List[dict]):
        self.db.lpush(self.PREFIX_ENTROPY, str(local_entropy))

    def sync(self) -> List[dict]:
        try:
            response = self.db.lrange(self.PREFIX_ENTROPY, 0, 1)
            if response:
                remote_entropy = ast.literal_eval(self.db.lrange(self.PREFIX_ENTROPY, 0, 1)[0])
                return remote_entropy
            return []
        except ConnectionError:
            return []

    def is_empty(self) -> bool:
        return not bool(self.db.llen(self.PREFIX_ENTROPY))


class MessageQueue(RedisClient):
    def __init__(self):
        super(MessageQueue, self).__init__()

        self.group = "tasks_group"
        self.consumer = "hexo"
        self.max_queue_size = 5600

        self.SYNERGY_PROTOCOL = "SYNERGY"

        self.automated()

    def is_exists_group(self, group_name: str) -> bool:
        try:
            groups = self.db.xinfo_groups(self.PREFIX_STREAM)
            for group in groups:
                if group.get("name", "") == group_name:
                    return True
            return False
        except ResponseError:
            return False

    def automated(self):
        if not self.is_exists_group(self.group):
            self.db.xgroup_create(self.PREFIX_STREAM, self.group, id="0", mkstream=True)

    def ack(self, message_id: str):
        self.db.xack(self.PREFIX_STREAM, self.group, message_id)

    def broadcast_synergy_context(self, context: dict):
        context = str(context) if isinstance(context, dict) else context
        synergy_context = {self.SYNERGY_PROTOCOL: context}
        self.db.xadd(self.PREFIX_STREAM, synergy_context, maxlen=self.max_queue_size, approximate=True)

    def listen(self, count: int = None, block: int = None):
        """

        :return:
        """

        while True:
            try:
                task_queue = self.db.xreadgroup(
                    self.group, self.consumer, {self.PREFIX_STREAM: ">"}, count=count, block=block
                )
            except ConnectionError:
                yield None
            else:
                if task_queue:
                    _, message = task_queue[0]
                    yield message


class AccessControl(RedisClient):
    def __init__(self, token: str = None):
        super(AccessControl, self).__init__()
        self.PREFIX_ACCESS_USER = "v2rss:access:user"
        self.PREFIX_ACCESS_LIMIT = "v2rss:access:limit"

        if token:
            self.init_tracer(token)

    def init_tracer(self, token: str):
        self.PREFIX_ACCESS_USER += f":{token}"
        self.PREFIX_ACCESS_LIMIT += f":{token}"

        # 自动注册
        self._register()

    def _register(self):
        self.db.setnx(self.PREFIX_ACCESS_USER, 0)

    def update(self):
        self.db.setnx(self.PREFIX_ACCESS_LIMIT, 0)
        self.db.incr(self.PREFIX_ACCESS_LIMIT)
        self.db.incr(self.PREFIX_ACCESS_USER)

    def _capture_access_trace(self):
        _lifecycle = 10
        self.db.setex(
            name=self.PREFIX_ACCESS_LIMIT,
            time=timedelta(seconds=_lifecycle),
            value=str(datetime.now(TIME_ZONE_CN) + timedelta(seconds=_lifecycle))
        )

    def is_user(self) -> bool:
        return bool(self.db.exists(self.PREFIX_ACCESS_USER))

    def is_repeat(self) -> bool:
        return bool(self.db.exists(self.PREFIX_ACCESS_LIMIT))
