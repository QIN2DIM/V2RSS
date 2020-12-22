from gevent.queue import Queue
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

    hera = Queue()
    # FIXME
    #  不明原因bug 使用dict（zip（））方案生成的同样的变量，
    #  在经过同一个函数方案后输出竟然不一样
    cache_redis_queue = {'ssr': {}, 'v2ray': {}}
    # cache_redis_queue = dict(zip(CRAWLER_SEQUENCE, [{}] * CRAWLER_SEQUENCE.__len__()))


def step_admin_element(class_: str = None) -> None:
    """
    管理员权限--范式缓冲
    @param class_:
    @return:
    """
    from BusinessLogicLayer.cluster.__task__ import loads_task
    loads_task(class_=class_, one_step=True)
