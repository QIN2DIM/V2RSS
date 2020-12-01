__all__ = ['flexible_distribute', 'FlexibleDistribute', 'to_admin']

import csv
import os
import threading

from BusinessCentralLayer.middleware.work_io import *
from BusinessLogicLayer.dog import subs2node


@logger.catch()
class FlexibleDistribute(object):
    """数据交换 弹性分发"""

    def __init__(self, docker: tuple = None) -> None:
        """

        @param docker: (class_, {subscribe: end_life})
        """
        # 若容器激活，迅速入队
        if all(docker):
            Middleware.zeus.put_nowait(docker)

            self.key_name = REDIS_SECRET_KEY.format(docker[0])

    def to_mysql(self) -> None:
        ...

    def to_mongo(self) -> None:
        ...

    @staticmethod
    def to_redis() -> None:
        """

        @return:
        """
        # 初始化容器
        docker = dict(zip(CRAWLER_SEQUENCE, [{}] * 2))

        # 任务出列 更新容器
        while not Middleware.zeus.empty():
            alice = Middleware.zeus.get_nowait()
            docker[alice[0]].update((alice[-1]))

        # 刷新Redis
        bob = RedisClient(db=4).get_driver()
        for xps in docker.items():
            bob.hset(name=xps[0], mapping=xps[-1])

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


# TODO:该模块将被弃用 后续版本将引入多路IO模块，代码使用class封装
def flexible_distribute(subscribe, class_, life_cycle: str, driver_name=None):
    """

    @param subscribe:
    @param class_:
    @param life_cycle:
    @param driver_name:
    @return:
    """

    # data --> Database(Mysql)

    # data --> Database(MongoDB)

    # data --> Redis
    threading.Thread(target=RedisClient().add, args=(REDIS_SECRET_KEY.format(class_), subscribe, life_cycle)).start()

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


def to_admin(class_):
    response = {'msg': 'failed'}
    # 获取链接
    if class_ in CRAWLER_SEQUENCE:
        try:
            logger.debug("管理员模式--点取链接")
            subs = markup_admin_element(class_)
            if subs:
                node_info: dict = subs2node(os.path.join(SERVER_DIR_DATABASE_CACHE, 'subs2node.txt'), subs)
                logger.success('管理员模式--链接分发成功')
                response.update(
                    {'msg': 'success', 'subscribe': node_info.get('subs'), 'nodeInfo': node_info.get('node'),
                     'subsType': class_})

                logger.info('管理员模式--尝试补充链接池')
                threading.Thread(target=step_admin_element, kwargs={"class_": class_}).start()
                logger.success('管理员模式--补充成功')
        except Exception as e:
            logger.exception(e)
        finally:
            return response
