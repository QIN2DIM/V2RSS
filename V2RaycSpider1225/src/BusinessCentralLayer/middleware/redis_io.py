__all__ = ['RedisClient', 'RedisDataDisasterTolerance']

from typing import List, Tuple

import redis

from src.BusinessCentralLayer.setting import REDIS_MASTER, REDIS_SECRET_KEY, TIME_ZONE_CN, CRAWLER_SEQUENCE, logger

REDIS_CLIENT_VERSION = redis.__version__
IS_REDIS_VERSION_2 = REDIS_CLIENT_VERSION.startswith('2.')


class RedisClient:
    def __init__(self, host=REDIS_MASTER['host'], port=REDIS_MASTER['port'], password=REDIS_MASTER['password'],
                 db=REDIS_MASTER['db'],
                 **kwargs) -> None:
        """
        init redis client
        :param host: redis host
        :param port: redis port
        :param password: redis password
        """

        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True, db=db, **kwargs, )
        self.subscribe = ''
        self.crawler_seq = CRAWLER_SEQUENCE

    def add(self, key_name=None, subscribe=None, life_cycle: str = None):
        """

        @param key_name: hash_name
        @param subscribe:
        @param life_cycle:
        @return:
        """
        try:
            self.db.hset(key_name, subscribe, life_cycle)
        finally:
            self.kill()

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
                    self.subscribe, end_life = list(target_raw.items()).pop(pop_)

                    # end_life: requests_time(采集时间点) + vip_crontab(机场会员时长(账号试用时长))

                    # 该模块最初设计时仅针对<vip_crontab = 1day>的机场采集
                    # 后续又将试用几天甚至几个月的机场加入了任务队列
                    # 但该分发逻辑并未更新 以后版本将继续沿用这套分发逻辑

                    # 若之后版本的项目支持end_life动态更新时(既加入某种技术能够实时反馈机场主对会员规则的修改)
                    # 此分发逻辑将会加入排序功能

                    # 若链接过期 -> loop next -> finally :db-del stale subscribe
                    if self.is_stale(end_life, beyond=3):
                        continue
                    return self.subscribe
                # 出现该错误视为redis队列被击穿 无任何可用的链接分发，中断循环
                except IndexError:
                    logger.critical("{}.get() IndexError".format(self.__class__.__name__))
                    return False
                # 关联解除
                finally:
                    from src.BusinessCentralLayer.middleware.subscribe_io import detach
                    detach(self.subscribe, beat_sync=True)
        finally:
            # 关闭连接
            self.kill()

    def refresh(self, key_name: str, cross_threshold: int = None) -> None:
        """
        原子级链接池刷新，一次性删去所有过期的key_name subscribe
        @param cross_threshold: 越过阈值删除订阅
        @param key_name:secret_key
        @return:
        """

        docker: dict = self.db.hgetall(key_name)
        # 管理员指令获取的链接
        if self.get_len(key_name) != 0:
            for subscribe, end_life in docker.items():
                if self.is_stale(end_life, cross_threshold):
                    logger.debug(f'del-({key_name})--{subscribe}')
                    self.db.hdel(key_name, subscribe)
            logger.success('<{}> UPDATE - {}({})'.format(self.__class__.__name__, key_name, self.get_len(key_name)))
        else:
            logger.warning('<{}> EMPTY - {}({})'.format(self.__class__.__name__, key_name, self.get_len(key_name)))

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
            now_time = datetime.fromisoformat(str(datetime.now(TIME_ZONE_CN)).split('.')[0])

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
            return '欢迎使用v2ray云彩姬'

    def get_driver(self) -> redis.StrictRedis:
        return self.db

    def update_api_status(self, api_name, date_format):
        if api_name not in ['select', 'get', 'search', 'decouple', 'reset']:
            return False
        self.db.rpush(f"v2rayc_apis:{api_name}", date_format)
        self.db.incr(f"v2rayc_apis:{api_name}_num")

    def sync_remain_subs(self, key_name) -> List[Tuple]:
        """
        载入Redis池内<key_name>类型剩余hash键
        @param key_name: secret key
        @return:
        """
        return list(self.db.hgetall(key_name).items())

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


class RedisDataDisasterTolerance(RedisClient):
    def __init__(self):
        super(RedisDataDisasterTolerance, self).__init__()

        from src.BusinessCentralLayer.setting import REDIS_SLAVER_DDT
        if not REDIS_SLAVER_DDT.get('host'):
            logger.warning('未设置数据容灾服务器，该职能将由Master执行')
            # 拷贝参数
            redis_virtual = REDIS_MASTER
            # 改动浅拷贝数据库
            redis_virtual.update({'db': redis_virtual['db'] + 1})
            logger.debug("备份重定向 --> {}".format(redis_virtual))
        else:
            redis_virtual = REDIS_SLAVER_DDT
        # 容器初始化
        self.docker = {}
        try:
            self.acm = RedisClient(host=redis_virtual['host'], port=redis_virtual['port'],
                                   password=redis_virtual['password'])
            logger.info("DDT: Master({}) -> Slaver({})".format(REDIS_MASTER['host'], redis_virtual['host']))
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
            logger.warning(f'({class_}):缓存可能被击穿或缓存为空，请系统管理员及时维护链接池！')
        except redis.exceptions.ConnectionError:
            logger.error(f"redis-slave {self.redis_virtual} 或宕机")
