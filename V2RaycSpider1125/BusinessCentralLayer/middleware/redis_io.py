__all__ = ['RedisClient', 'RedisDataDisasterTolerance']

import redis
from config import REDIS_MASTER, REDIS_SECRET_KEY, TIME_ZONE_CN, CRAWLER_SEQUENCE, logger

REDIS_CLIENT_VERSION = redis.__version__
IS_REDIS_VERSION_2 = REDIS_CLIENT_VERSION.startswith('2.')


class RedisClient(object):
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

    def add(self, key_name, subscribe, life_cycle: str):
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

    def get(self, key_name) -> str or bool:
        """
        分发订阅链接
        每次get请求都会强制关闭连接
        @param key_name: 任务类型，用于定位 redis hash name
        @return:
        """
        try:
            while True:
                # 一次性抽取key_name(hashName)下的所有subscribe
                target_raw: dict = self.db.hgetall(key_name)
                try:
                    # 弹出并捕获 <离当前时间> <最远一次入库>的订阅连接 既订阅链接并未按end_life排序
                    self.subscribe, end_life = list(target_raw.items()).pop(0)

                    # end_life: requests_time(采集时间点) + vip_crontab(机场会员时长(账号试用时长))

                    # 该模块最初设计时仅针对<vip_crontab = 1day>的机场采集
                    # 后续又将试用几天甚至几个月的机场加入了任务队列
                    # 但该分发逻辑并未更新 以后版本将继续沿用这套分发逻辑

                    # 若之后版本的项目支持end_life动态更新时(既加入某种技术能够实时反馈机场主对会员规则的修改)
                    # 此分发逻辑将会加入排序功能
                    # TODO 当前版本使用<可视-选择-获取>的方案给予使用者挑选链接的权限

                    # 若链接过期 -> loop next -> finally :db-del stale subscribe
                    if self.is_stale(end_life):
                        continue
                    # 若链接可用 -> break off -> 分发 -> finally :db-del subscribe
                    else:
                        return self.subscribe
                # 出现该错误视为redis队列被击穿 无任何可用的链接分发，中断循环
                except IndexError:
                    logger.critical("{}.get() IndexError".format(self.__class__.__name__))
                    return False
                # 烫手:见光死
                finally:
                    self.db.hdel(key_name, self.subscribe)
        finally:
            # 关闭连接
            self.kill()

    def refresh(self, key_name: str) -> None:
        """
        原子级链接池刷新，一次性删去所有过期的key_name subscribe
        @param key_name:secret_key
        @return:
        """
        if self.db.hlen(key_name) != 0:
            for subscribe, end_life in self.db.hgetall(key_name).items():
                if self.is_stale(end_life):
                    logger.debug(f'del-({key_name})--{subscribe}')
                    self.db.hdel(key_name, subscribe)
            logger.success('{}:UPDATE - {}({})'.format(self.__class__.__name__, key_name, self.__len__(key_name)))
        else:
            logger.warning('{}:EMPTY - {}({})'.format(self.__class__.__name__, key_name, self.__len__(key_name)))

    @staticmethod
    def is_stale(item) -> bool:
        """
        判断订阅链接是否过期
        @param item: 可转换为datetime 的 str 时间戳
        @return:
        """
        from datetime import datetime

        if isinstance(item, str):
            # 订阅连接到期时间 -> datetime
            check_item = datetime.fromisoformat(item)

            # 上海时区 -> datetime
            check_now = datetime.fromisoformat(str(datetime.now(TIME_ZONE_CN)).split('.')[0])

            # 时间比对 并返回是否过期的响应 -> bool
            return False if check_item >= check_now else True

    def __len__(self, key_name) -> int:
        return self.db.hlen(key_name)

    def kill(self) -> None:
        self.db.close()

    def test(self) -> str:
        if self.db.ping():
            return '欢迎使用v2ray云彩姬'

    def get_driver(self) -> redis.StrictRedis:
        return self.db


class RedisDataDisasterTolerance(RedisClient):
    def __init__(self):
        super(RedisDataDisasterTolerance, self).__init__()

        from config import REDIS_SLAVER_DDT
        if not REDIS_SLAVER_DDT.get('host'):
            logger.warning(f'未设置数据容灾服务器，该职能将由{self.__class__.__name__}执行')
            REDIS_SLAVER_DDT = REDIS_MASTER
            REDIS_SLAVER_DDT.update({'db': REDIS_SLAVER_DDT['db'] + 1})
            logger.debug("备份重定向 --> {}".format(REDIS_SLAVER_DDT))

        self.docker = {}
        try:
            self.acm = RedisClient(host=REDIS_SLAVER_DDT['host'], port=REDIS_SLAVER_DDT['port'],
                                   password=REDIS_SLAVER_DDT['password'])
            logger.info("DDT: Master({}) -> Slaver({})".format(REDIS_MASTER['host'], REDIS_SLAVER_DDT['host']))
        except redis.exceptions.ConnectionError as e:
            logger.exception(e)

    def run(self, class_: str) -> None:
        """
        Data disaster tolerance or one class_
        @param class_: subscribe type  `ssr` or `v2ray` or `trojan` ...
        @return:
        """
        key_name = REDIS_SECRET_KEY.format(class_)
        self.refresh(key_name)

        # 数据拷贝  ... -> self
        for subscribe, end_life in self.db.hgetall(key_name).items():
            self.docker.update({subscribe: end_life})
            # logger.info("{} {}".format(key_name, subscribe))

        # 映射迁移  acm <- ...
        try:
            self.acm.get_driver().hset(key_name, mapping=self.docker)
        except Exception as e:
            logger.exception(e)
