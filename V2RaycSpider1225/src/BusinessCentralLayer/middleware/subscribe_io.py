__all__ = [
    'FlexibleDistribute',
    'pop_subs_to_admin',
    'detach',
    'set_task2url_cache',
    'select_subs_to_admin',
]

import threading
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse
from uuid import uuid4

from faker import Faker

from src.BusinessCentralLayer.setting import logger, REDIS_SECRET_KEY, CRAWLER_SEQUENCE, NGINX_SUBSCRIBE, \
    SQLITE3_CONFIG, TIME_ZONE_CN
from .flow_io import FlowTransferStation
from .redis_io import RedisClient
from ..middleware import work_io


class FlexibleDistribute:
    """数据交换 弹性分发"""

    def __init__(self, docker: list = None, beat_sync=False):
        """

        @param docker:['domain', 'subs', 'class_', 'end_life', 'res_time', 'passable',
                        'username', 'password', 'email']
        @param beat_sync:立即启动数据存储功能，当单只爬虫调试时弃用，若为集群运动，数据存储功能将由其他模块单独负责
        """
        self.work_q = work_io.Middleware
        # 若容器激活，迅速入队
        try:
            if all(docker) and isinstance(docker, list):
                self.work_q.zeus.put_nowait(
                    dict(zip(SQLITE3_CONFIG['header'].split(','), docker + [str(uuid4()), ])))
            if beat_sync:
                self.beat_sync = beat_sync
                self.start()
        except TypeError:
            pass

    @staticmethod
    @logger.catch()
    def to_sqlite3(docker: dict):
        """

        @param docker: {uuid1:{key1:value1, key2:value2, ...}, uuid2:{key1:value1, key2:value2, ...}, ...} len >= 1
        @return:
        """
        try:
            if docker.keys().__len__() >= 1:
                docker = [tuple(data.values()) for data in docker.values()]
                # logger.success(f'>> STORING -> Sqlite3')
        finally:
            FlowTransferStation(docker=docker).add()

    def to_redis(self, ):
        r = RedisClient().get_driver()
        for docker in self.work_q.cache_redis_queue.items():
            key_name = REDIS_SECRET_KEY.format(docker[0])
            if docker[-1]:
                r.hset(key_name, mapping=docker[-1])
        # logger.success(f">> PUSH -> Redis")

        for k in self.work_q.cache_redis_queue:
            self.work_q.cache_redis_queue[k] = {}
        # logger.debug(f'>> RESET <Middleware.cache_redis_queue>')

    @staticmethod
    def to_nginx(class_, subscribe) -> None:
        """
        直接调用--to show subs
        @param class_: 链接类型
        @param subscribe: 该类型链接
        @return:
        """

        with open(NGINX_SUBSCRIBE.format(class_), 'w', encoding='utf-8') as f:
            f.write(subscribe)

    def start(self):
        docker = {}

        # 任务出列 更新容器
        while not self.work_q.zeus.empty():
            item = self.work_q.zeus.get_nowait()

            # 临时拷贝
            docker.update({item['uuid PRIMARY KEY']: item})

            # 将数据压入redis缓存
            self.work_q.cache_redis_queue[f"{item['class_']}"].update({item['subs']: item['end_life']})

        # 将数据推送至redis
        self.to_redis()

        # 将数据推送至sqlite3
        # self.to_sqlite3(docker)

        # Middleware.hera.put('push')


def set_task2url_cache(task_name, register_url, subs):
    """

    @param task_name: XXCloud
    @param register_url:
    @param subs:
    @return:
    """
    from src.BusinessCentralLayer.middleware.work_io import Middleware
    docker = {
        urlparse(register_url).netloc: {
            "name": task_name,
            "type": urlparse(subs).netloc
        }
    }
    Middleware.theseus.update(docker)


def detach(subscribe: str, beat_sync=False):
    """

    @param subscribe:
    @param beat_sync: 是否立即删除， True：立即删除，False:节拍同步，随ddt删除
    @return:
    """

    # 清洗出订阅中的token
    token = urlparse(subscribe).path

    r = RedisClient().get_driver()

    # 遍历所有任务类型
    for task in CRAWLER_SEQUENCE:
        # 遍历某种类型的链接池
        for sub in r.hgetall(REDIS_SECRET_KEY.format(task)).items():
            # 匹配用户token
            if token == urlparse(sub[0]).path:
                # 若节拍同步，立即移除订阅
                if beat_sync:
                    r.hdel(REDIS_SECRET_KEY.format(task), sub[0])
                    logger.debug(f'>> Detach -> {sub[0]}')
                # 否则将订阅过期时间标记为过期，该链接将随下一波任一节点的ddt任务被删除
                else:
                    r.hset(REDIS_SECRET_KEY.format(task), sub[0], str(Faker().past_datetime()))
                break


def pop_subs_to_admin(class_: str):
    """

    @param class_:
    @return:
    """
    logger.debug("<SuperAdmin> -- 获取订阅")
    from src.BusinessLogicLayer.cluster.sailor import manage_task

    try:
        # 获取该类型订阅剩余链接
        remain_subs: list = RedisClient().sync_remain_subs(REDIS_SECRET_KEY.format(class_))
        while True:
            # 若无可用链接则返回错误信息
            if remain_subs.__len__() == 0:
                logger.error(f'<SuperAdmin> --  无可用<{class_}>订阅')
                return {'msg': 'failed', 'info': f"无可用<{class_}>订阅"}
            # 从池中获取(最新加入的)订阅s-e
            subs, end_life = remain_subs.pop()

            # 将s-e加入缓冲队列，该队列将被ddt的refresh工作流同过期链接一同删除
            # 使用缓冲队列的方案保证节拍同步，防止过热操作/失误操作贯穿Redis

            # 既当管理员通过此接口获取链接时，被返回的链接不会直接从池中删去
            # 而是触发缓冲机制，既将该链接标记后加入apollo缓冲队列
            # apollo队列内的元素都是欲删除缓存，当ddt发动后会一次性情况当前所有的缓存

            # 对订阅进行质量粗检
            # if subs2node(subs=subs, cache_path=False, timeout=2)['node'].__len__() <= 3:
            #     logger.debug(f"<check> BadLink -- {subs}")
            #     continue

            # 使用节拍同步线程锁发起连接池回滚指令,仅生成/同步一枚原子任务
            threading.Thread(target=manage_task, kwargs={"class_": class_, "only_sync": True}).start()
            logger.success('管理员模式--链接分发成功')

            # 立即执行链接解耦，将同一账号的所有订阅移除
            # beat_sync =True立即刷新，False延迟刷新（节拍同步）
            threading.Thread(target=detach, kwargs={"subscribe": subs, 'beat_sync': True}).start()

            return {'msg': 'success', 'subscribe': subs, 'subsType': class_}
    except Exception as e:
        logger.exception(e)
        return {'msg': 'failed', 'info': str(e)}


def select_subs_to_admin(select_netloc: str = None, _debug=False) -> dict:
    # 池内所有类型订阅
    remain_subs = []
    # 订阅池状态映射表
    mapping_subs_status = {}
    # 链接-类型映射表
    mapping_subs_type = {}
    rc = RedisClient()
    # 清洗数据
    for filed in CRAWLER_SEQUENCE:
        # 提取池内对应类型的所有订阅链接
        filed_subs: list = RedisClient().sync_remain_subs(REDIS_SECRET_KEY.format(filed))
        # 更新汇总队列
        remain_subs += filed_subs
        # 提取subs netloc映射区间
        urls = [urlparse(i[0]).netloc for i in filed_subs]
        # 更新映射表
        mapping_subs_status.update({filed: dict(Counter(urls))})
        mapping_subs_type.update(zip([i[0] for i in filed_subs], [filed, ] * len(filed_subs)))
    # 初始化状态下，返回订阅池状态
    if not select_netloc:
        rc.update_api_status(api_name="search", date_format=str(datetime.now(TIME_ZONE_CN)))
        return {'msg': 'success', 'info': mapping_subs_status}
    for tag in remain_subs:
        # 提取信息键
        subscribe, end_life = tag[0], tag[-1]
        # 存在对应netloc的链接并可存活至少beyond小时
        if select_netloc in urlparse(subscribe).netloc and not RedisClient().is_stale(end_life, beyond=6):
            logger.debug("<SubscribeIO> -- GET SUBSCRIPTION")
            rc.update_api_status(api_name="get", date_format=str(datetime.now(TIME_ZONE_CN)))
            try:
                return {
                    'msg': "success",
                    'debug': _debug,
                    'info': {
                        "subscribe": subscribe,
                        "endLife": end_life,
                        'subsType': mapping_subs_type[subscribe],
                        "netloc": select_netloc
                    }
                }
            finally:
                if not _debug:
                    threading.Thread(target=detach, kwargs={"subscribe": subscribe, 'beat_sync': True}).start()
            # 无库存或误码
    return {'msg': "failed", "netloc": select_netloc, "info": "指令错误或不存在该类型订阅", "status": mapping_subs_status}
