__all__ = ["RedisClient", "RedisDataDisasterTolerance", "MessageQueue", "EntropyHeap"]

import ast
from typing import List, Tuple

import redis

from BusinessCentralLayer.setting import (
    REDIS_MASTER,
    REDIS_SECRET_KEY,
    TIME_ZONE_CN,
    CRAWLER_SEQUENCE,
    LAUNCH_INTERVAL,
    SINGLE_TASK_CAP,
    logger,
)


class RedisClient:
    def __init__(
            self,
            host=REDIS_MASTER["host"],
            port=REDIS_MASTER["port"],
            password=REDIS_MASTER["password"],
            db=REDIS_MASTER["db"],
            **kwargs,
    ) -> None:
        """
        init redis client
        :param host: redis host
        :param port: redis port
        :param password: redis password
        """

        self.db = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            db=db,
            health_check_interval=30,
            **kwargs,
        )
        self.sub_link = ""
        self.crawler_seq = CRAWLER_SEQUENCE
        self.studio = "collaborators"

    def add(self, subscribe_class=None, subscribe=None, end_time: str = None):
        """

        @param subscribe_class:
        @param subscribe:
        @param end_time:
        @return:
        """
        name_ = REDIS_SECRET_KEY.format(subscribe_class)
        self.db.hset(name_, subscribe, end_time)

    def get(self, key_name, pop_=0) -> str or bool:
        """
        分发订阅链接
        每次get请求都会强制关闭连接
        @param pop_:
        @param key_name: 任务类型，用于定位 redis hash name
        @return:
        """
        try:
            while True:
                # 一次性抽取key_name(hashName)下的所有subscribe
                target_raw: dict = self.db.hgetall(key_name)
                try:
                    # 弹出并捕获 <离当前时间> <最远一次入库>的订阅连接 既订阅链接并未按end_life排序
                    self.sub_link, end_life = list(target_raw.items()).pop(pop_)

                    # end_life: requests_time(采集时间点) + vip_crontab(机场会员时长(账号试用时长))

                    # 该模块最初设计时仅针对<vip_crontab = 1day>的机场采集
                    # 后续又将试用几天甚至几个月的机场加入了任务队列
                    # 但该分发逻辑并未更新 以后版本将继续沿用这套分发逻辑

                    # 若之后版本的项目支持end_life动态更新时(既加入某种技术能够实时反馈机场主对会员规则的修改)
                    # 此分发逻辑将会加入排序功能

                    # 若链接过期 -> loop next -> finally :db-del stale subscribe
                    if self.is_stale(end_life, beyond=3):
                        continue
                    return self.sub_link
                # 出现该错误视为redis队列被击穿 无任何可用的链接分发，中断循环
                except IndexError:
                    logger.critical(
                        "{}.get() IndexError".format(self.__class__.__name__)
                    )
                    return False
                # 关联解除
                finally:
                    from BusinessCentralLayer.middleware.subscribe_io import detach

                    detach(self.sub_link, beat_sync=True)
        finally:
            # 关闭连接
            self.kill()

    def refresh(self, key_name: str, cross_threshold: int = None) -> int:
        """
        原子级链接池刷新，一次性删去所有过期的key_name subscribe
        @param cross_threshold: 越过阈值删除订阅
        @param key_name:secret_key
        @return:
        """

        docker: dict = self.db.hgetall(key_name)
        if docker:
            for subscribe, end_life in docker.items():
                if self.is_stale(end_life, cross_threshold):
                    logger.debug(f"del-({key_name})--{subscribe}")
                    self.db.hdel(key_name, subscribe)
        return self.get_len(key_name)

    @staticmethod
    def is_stale(subs_expiration_time: str, beyond: int = None) -> bool:
        """
        判断订阅链接是否过期
        @param beyond: 链接剩余可用时间不足 beyond 小时达到可删除阈值
        @todo v_5.0.X update 若`订阅存活时间` < `阈值` 也需删除
        @param subs_expiration_time: 可转换为datetime 的 str 时间戳
        @return: True 过期或越过阈值 需删除；False链接为过期或未达阈值，无特殊需求请勿删除
        """
        from datetime import datetime, timedelta

        if isinstance(subs_expiration_time, str):
            # 订阅连接到期时间 -> datetime
            subs_end_time = datetime.fromisoformat(subs_expiration_time)

            # 上海时区 -> datetime
            now_time = datetime.fromisoformat(
                str(datetime.now(TIME_ZONE_CN)).split(".")[0]
            )

            # 时间比对 并返回是否过期的响应 -> bool
            if beyond and isinstance(beyond, int):
                return subs_end_time < (now_time + timedelta(hours=beyond))
            if beyond is None:
                return subs_end_time < now_time

    def get_len(self, key_name) -> int:
        return self.db.hlen(key_name)

    def subs_info(self, class_: str = None) -> dict:
        """

        @return: 获取各个类型订阅的剩余数量
        """
        response = {}
        if class_ is None:
            for key_ in CRAWLER_SEQUENCE:
                response.update({key_: self.get_len(REDIS_SECRET_KEY.format(key_))})
        else:
            response[class_] = self.get_len(REDIS_SECRET_KEY.format(class_))
        return response

    def kill(self) -> None:
        self.db.close()

    def test(self) -> str:
        if self.db.ping():
            return "欢迎使用V2RSS云彩姬"

    def get_driver(self) -> redis.StrictRedis:
        return self.db

    def update_api_status(self, api_name, date_format):
        if api_name not in ["select", "get", "search", "decouple", "reset"]:
            return False
        self.db.rpush(f"v2rayc_apis:{api_name}", date_format)
        self.db.incr(f"v2rayc_apis:{api_name}_num")

    def sync_remain_subs(self, key_name) -> List[Tuple]:
        """
        载入Redis池内<key_name>类型剩余hash键
        @param key_name: secret key
        @return:
        """
        _sync_response = []
        try:
            _sync_response = list(self.db.hgetall(key_name).items())
            return list(self.db.hgetall(key_name).items())
        except redis.exceptions.ResponseError:
            logger.error(f"{key_name} 队列为空")
            return _sync_response

    def sync_message_queue(self, mode: str, message: str = None):
        """
        同步消息队列，此处暂时仅用于任务队列的同步,
        @todo 数据结构预设为List，每次download获取（弹出）一个元素，
        @todo 读写分离，向 master上传，通过订阅同步到集群，slave从集群读入
        @param message: 消息队列容器
        @param mode:
        @return:
        """

        # 发布任务订阅任务
        if mode == "upload":
            if message:
                self.db.lpush("Poseidon", message)
                # logger.info(f"<RedisClient> UploadTask || message")
                return True
            logger.warning("<RedisClient> EmptyTask || 要上传的消息载体为空")
            return False

        # 同步任务队列，下载原子任务
        if mode == "download":
            if self.db.exists("Poseidon"):
                return self.db.lpop("Poseidon")
            return False

    def set_alias(self, alias: str, netloc: str):
        """
        为订阅存储别名
        :param netloc: 网址的 netloc
        :param alias: 别名
        :return:
        """
        self.db.hset("v2rss:alias", netloc, alias)


class RedisDataDisasterTolerance(RedisClient):
    def __init__(self):
        super(RedisDataDisasterTolerance, self).__init__()

        from BusinessCentralLayer.setting import REDIS_SLAVER_DDT

        if not REDIS_SLAVER_DDT.get("host"):
            logger.warning("未设置数据容灾服务器，该职能将由Master执行")
            # 拷贝参数
            redis_virtual = REDIS_MASTER
            # 改动浅拷贝数据库
            redis_virtual.update({"db": redis_virtual["db"] + 1})
            logger.debug("备份重定向 --> {}".format(redis_virtual))
        else:
            redis_virtual = REDIS_SLAVER_DDT
        # 容器初始化
        self.docker = {}
        try:
            self.acm = RedisClient(
                host=redis_virtual["host"],
                port=redis_virtual["port"],
                password=redis_virtual["password"],
            )
            logger.info(
                "DDT: Master({}) -> Slaver({})".format(
                    REDIS_MASTER["host"], redis_virtual["host"]
                )
            )
        except redis.exceptions.ConnectionError as e:
            logger.exception(e)
        finally:
            self.redis_virtual = redis_virtual

    def run(self, class_: str) -> None:
        """
        Data disaster tolerance or one class_
        @param class_: subscribe type  `ssr` or `v2ray` or `trojan` ...
        @return:
        """

        key_name = REDIS_SECRET_KEY.format(class_)
        self.refresh(key_name, cross_threshold=6)

        # 数据拷贝  ... -> self
        for subscribe, end_life in self.db.hgetall(key_name).items():
            self.docker.update({subscribe: end_life})
            # logger.info("{} {}".format(key_name, subscribe))

        # 映射迁移  acm <- ...
        try:
            self.acm.get_driver().hset(key_name, mapping=self.docker)
        except redis.exceptions.DataError:
            logger.warning(f"({class_}):缓存可能被击穿或缓存为空，请系统管理员及时维护链接池！")
        except redis.exceptions.ConnectionError:
            logger.error(f"redis-slave {self.redis_virtual} 或宕机")


class MessageQueue(RedisClient):
    def __init__(self, group_: str = None):
        super(MessageQueue, self).__init__()
        # 消息流：广播待处理消息的运行时上下文摘要信息
        self.stream_ = "v2rss:tasks"
        # # 信息流：广播已处理的消息ID（全局共享）
        # self.stream_offload_name = "offload_queue"
        # 统一消费组名称，分布式接入点使用统一的消费组 pending-ids 同步工作进度
        self.group_ = "tasks_group" if group_ is None else group_
        # 统一消费者头id，可考虑使用消费者回收机制，确保分布式并发安全
        self.consumer_ = "hexo"
        # 截断 6 小时理论吞吐量的冗余数据
        self.max_queue_size = max(
            int((6 * 3600 / LAUNCH_INTERVAL["collector"]) * 100), SINGLE_TASK_CAP
        )
        # 任务同步的批次大小
        self.count = 1
        # 任务同步的阻塞时间，默认 2s
        self.block = 2 * 1000

        # 自动初始化
        self._automated()

    def _is_exists_group(self, group_name: str) -> bool:
        """

        :param group_name:
        :return:
        """
        try:
            groups = self.db.xinfo_groups(self.stream_)
            for group in groups:
                if group.get("name", "") == group_name:
                    return True
            return False
        except redis.exceptions.ResponseError:
            return False

    def _automated(self):
        """
        自动初始化 消费者组 以及 消息流。
        使用 MKSTREAM 参数，当创建组时，组依赖的流不存在，则会自动创建流。此时流的长度为0。
        :return:
        """
        if not self._is_exists_group(self.group_):
            self.db.xgroup_create(self.stream_, self.group_, id="0", mkstream=True)

    def __len__(self):
        return self.db.xlen(self.stream_)

    def remove_bad_code(self, type_: str, hook_: str):
        self.db.hdel(REDIS_SECRET_KEY.format(type_), hook_)

    def broadcast_pending_task(self, fields: dict):
        """
        广播消息上下文
        :param fields: 消息键值对
        :return:
        """
        try:
            self.db.xadd(self.stream_, fields, maxlen=self.max_queue_size, approximate=True)
            return True
        except redis.exceptions.ConnectionError:
            return False

    def offload_task(self, message_id: str):
        self.db.xack(self.stream_, self.group_, message_id)

    def _focus_task(self, count: int = None, block: int = None):
        """

        :param count: 一次可同步的最大任务数。

        当 未读任务数远大于 count 时，此参数生效。
        当 未读任务数远小于 count 或为 0 时，count 数值上等于未读任务数。无可读任务时函数返回空列表。

        换句话说，在 block 阻塞时间内, 一旦消息流出现变更，xreadgroup 一次性读取 count 个（ '>' 变更数据）消息并返回；
        而不是在 block 阻塞时间内尝试等待收集到 count 数量的任务再返回。

        意味着 当 block != 0 时，实际阻塞时间 <= block

        :param block: 阻塞（毫秒），默认 2s。
        :return:
        """
        return self.db.xreadgroup(
            self.group_, self.consumer_, {self.stream_: ">"}, count=count, block=block
        )

    def handle_task(self, count: int = 1, block: int = 2 * 1000) -> list:
        """

        :param count:
        :param block:
        :return: [['tasks', [('1635474291784-0', {'pending': '待处理队列'}), ... ]]]
        """
        task_queue = self._focus_task(count, block)
        if task_queue:
            _, message = task_queue[0]
            return message

    def get_pending_tasks(self) -> dict:
        """

        :return: {
            'pending': 5,
            'min': '1635471488028-0',
            'max': '1635471640628-0',
            'consumers': [{'name': 'hexo', 'pending': 5}]
        }
        """
        return self.db.xpending(self.stream_, self.group_)

    def listen(self, count: int = None, block: int = None):
        """

        :return:
        """
        count = self.count if count is None else count
        block = self.block if block is None else block

        while True:
            yield self.handle_task(count=count, block=block)


class EntropyHeap(RedisClient):
    def __init__(self):
        super(EntropyHeap, self).__init__(db=0)
        self.entropy_name = "v2rss:entropy"

    def update(self, new_entropy: List[dict]):
        self.db.lpush(self.entropy_name, str(new_entropy))

    def sync(self) -> List[dict]:
        response = self.db.lrange(self.entropy_name, 0, 1)
        if response:
            return ast.literal_eval(self.db.lrange(self.entropy_name, 0, 1)[0])

    def is_empty(self):
        return not bool(self.db.llen(self.entropy_name))
