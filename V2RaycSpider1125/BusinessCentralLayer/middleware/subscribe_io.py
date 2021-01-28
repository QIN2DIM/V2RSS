__all__ = ['flexible_distribute', 'FlexibleDistribute', 'to_admin', 'detach']

import csv
import threading
from uuid import uuid4

from BusinessCentralLayer.middleware.flow_io import FlowTransferStation
from BusinessCentralLayer.middleware.redis_io import RedisClient
from BusinessCentralLayer.middleware.work_io import Middleware, step_admin_element
from config import *


class FlexibleDistribute(object):
    """数据交换 弹性分发"""

    def __init__(self, docker: list = None, at_once=False):
        """

        @param docker:['domain', 'subs', 'class_', 'end_life', 'res_time', 'passable',
                        'username', 'password', 'email']
        @param at_once:立即启动数据存储功能，当单只爬虫调试时弃用，若为集群运动，数据存储功能将有其他模块单独负责
        """
        # 若容器激活，迅速入队
        try:
            if all(docker) and isinstance(docker, list):
                Middleware.zeus.put_nowait(dict(zip(SQLITE3_CONFIG['header'].split(','), docker + [str(uuid4()), ])))
            if at_once:
                self.at_once = at_once
                self.start()
        except TypeError:
            pass

    @staticmethod
    def to_sqlite3(docker: dict):
        """

        @param docker: {uuid1:{key1:value1, key2:value2, ...}, uuid2:{key1:value1, key2:value2, ...}, ...} len >= 1
        @return:
        """
        try:
            if docker.keys().__len__() >= 1:
                docker = [tuple(data.values()) for data in docker.values()]
                # logger.success(f'>> STORING -> Sqlite3')
        except Exception as e:
            logger.exception(e)
        finally:
            FlowTransferStation(docker=docker).add()

    @staticmethod
    def to_redis():
        r = RedisClient().get_driver()
        for docker in Middleware.cache_redis_queue.items():
            key_name = REDIS_SECRET_KEY.format(docker[0])
            if docker[-1]:
                r.hset(key_name, mapping=docker[-1])
        # logger.success(f">> PUSH -> Redis")

        for k in Middleware.cache_redis_queue.keys():
            Middleware.cache_redis_queue[k] = {}
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
        while not Middleware.zeus.empty():
            item = Middleware.zeus.get_nowait()

            # 临时拷贝
            docker.update({item['uuid PRIMARY KEY']: item})

            # 将数据压入redis缓存
            Middleware.cache_redis_queue[f"{item['class_']}"].update({item['subs']: item['end_life']})

        # 将数据推送至redis
        self.to_redis()

        # 将数据推送至sqlite3
        self.to_sqlite3(docker)

        # Middleware.hera.put('push')


# TODO:该模块将被弃用 后续版本将引入多路IO模块，代码使用class封装
def flexible_distribute(subscribe, class_, end_life: str, driver_name=None):
    """

    @param subscribe:
    @param class_:
    @param end_life:
    @param driver_name:
    @return:
    """
    from datetime import datetime
    # data --> Database(Mysql)

    # data --> Database(MongoDB)

    # data --> Redis
    threading.Thread(target=RedisClient().add, args=(REDIS_SECRET_KEY.format(class_), subscribe, end_life)).start()

    # data --> csv
    with open(SERVER_PATH_DATABASE_FETCH, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 入库时间 subscribe 类型
        now_ = str(datetime.now(TIME_ZONE_CN)).split('.')[0]
        writer.writerow([f'{now_}', f"{driver_name}", f'{subscribe}', class_])

    # data --> <Nginx> if linux or <Cache>
    try:
        with open(NGINX_SUBSCRIBE.format(class_), 'w', encoding='utf-8') as f:
            f.write(subscribe)
    except FileNotFoundError as e:
        print(e)


def detach(subscribe, at_once=False):
    """

    @param subscribe:
    @param at_once: 是否立即删除， True：立即删除，False:节拍同步，随ddt删除
    @return:
    """
    from faker import Faker
    from urllib.parse import urlparse
    from config import CRAWLER_SEQUENCE

    token = urlparse(subscribe).path

    r = RedisClient().get_driver()

    for task in CRAWLER_SEQUENCE:
        for sub in r.hgetall(REDIS_SECRET_KEY.format(task)).items():
            if token == urlparse(sub[0]).path:
                if at_once:
                    r.hdel(REDIS_SECRET_KEY.format(task), sub[0])
                else:
                    r.hset(REDIS_SECRET_KEY.format(task), sub[0], str(Faker().past_datetime()))
                logger.debug(f'>> Detach -> {sub[0]}')
                break


def to_admin(class_):
    # 获取链接
    if class_ in CRAWLER_SEQUENCE:
        try:
            logger.debug("管理员模式--点取链接")

            key_name = REDIS_SECRET_KEY.format(class_)

            me = [i for i in RedisClient().get_driver().hgetall(key_name).items()]

            if me.__len__() >= 1:
                # 从池中获取(最新)链接(不删除)
                subs, end_life = me.pop()

                # 将s-e加入缓冲队列，该队列将被ddt的refresh工作流同过期链接一同删除
                # 使用缓冲队列的方案保证节拍同步，防止过热操作/失误操作贯穿Redis

                # 既当管理员使用此权限获取链接时，刷出的链接并不会直接从池中删去
                # 而是被加入缓冲队列，当ddt发动时，refresh机制会一次性删除池中所有过期链接
                # 而apollo队列内的元素会被标记为过时信息，此时refresh将从apollo中弹出元素
                # 与池中链接进行查找比对，若找到，则一同删去

                if subs:
                    # from BusinessLogicLayer.dog import subs2node
                    # node_info: dict = subs2node(os.path.join(SERVER_DIR_DATABASE_CACHE, 'subs2node.txt'), subs)
                    # cache = {'subscribe': node_info.get('subs'), 'nodeInfo': node_info.get('node')}
                    logger.success('管理员模式--链接分发成功')
                    threading.Thread(target=step_admin_element, kwargs={"class_": class_}).start()

                    # at_once =True立即刷新，False延迟刷新（节拍同步）
                    logger.info(f'>> Try to detach subs')
                    threading.Thread(target=detach, kwargs={"subscribe": subs, 'at_once': True}).start()

                    return {'msg': 'success', 'subscribe': subs, 'subsType': class_}
                else:
                    return {'msg': 'failed'}
            # else:
            #     logger.error('链接池为空，正在紧急补充链接池')
            #     threading.Thread(target=step_admin_element, kwargs={"class_": class_}).start()
            #     return to_admin(class_)
        except Exception as e:
            logger.exception(e)
            return {'msg': 'failed'}


if __name__ == '__main__':
    url = 'https://www.jssv2raytoday.xyz/link/lRpFe0B8rvamG5IL?sub=3'
    detach(url, True)
