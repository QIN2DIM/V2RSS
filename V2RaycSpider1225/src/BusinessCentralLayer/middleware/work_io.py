__all__ = ["Middleware"]

from gevent.queue import Queue


# 工作栈
class Middleware:
    # cache of redis
    zeus = Queue()

    # Trash
    apollo = Queue()

    theseus = {}

    # 共享任务队列
    poseidon = Queue()

    hera = Queue()

    # FIXME
    #  不明原因bug 使用dict（zip（））方案生成的同样的变量，
    #  在经过同一个函数方案后输出竟然不一样
    cache_redis_queue = {"ssr": {}, "v2ray": {}}
    # cache_redis_queue = dict(zip(CRAWLER_SEQUENCE, [{}] * CRAWLER_SEQUENCE.__len__()))
