from datetime import datetime
from gevent.queue import Queue
from BusinessCentralLayer.middleware.redis_io import RedisClient
from config import *


# 工作栈
class Middleware:
    # cache of redis
    zeus = Queue()

    # Trash
    apollo = Queue()

    theseus = {}

    # work
    poseidon = Queue()


def markup_admin_element(class_: str) -> str:
    """

    @param class_: seq str
    @return:
    """
    key_name = REDIS_SECRET_KEY.format(class_)

    r = RedisClient().get_driver()

    me = [i for i in r.hgetall(key_name).items()]

    if me.__len__() >= 1:
        # 从池中获取(最新)链接(不删除)
        subs, end_life = [i for i in r.hgetall(key_name).items()].pop()
        flag = str(datetime.now(TIME_ZONE_CN)).split('.')[0]
        # 将s-e加入缓冲队列，该队列将被ddt的refresh工作流同过期链接一同删除
        # 使用缓冲队列的方案保证节拍同步，防止过热操作/失误操作贯穿Redis

        r.hset(key_name, key=subs, value=flag)
        # 既当管理员使用此权限获取链接时，刷出的链接并不会直接从池中删去
        # 而是被加入缓冲队列，当ddt发动时，refresh机制会一次性删除池中所有过期链接
        # 而apollo队列内的元素会被标记为过时信息，此时refresh将从apollo中弹出元素
        # 与池中链接进行查找比对，若找到，则一同删去
        return subs
    else:
        return ''


def step_admin_element(class_: str = None) -> None:
    """
    管理员权限--范式缓冲
    @param class_:
    @return:
    """
    from BusinessLogicLayer.cluster.__task__ import loads_task
    loads_task(class_=class_, one_step=True)
