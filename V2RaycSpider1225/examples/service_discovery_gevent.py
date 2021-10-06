from gevent import monkey

monkey.patch_all()
import os
import random
from datetime import datetime
import time
import gevent
from gevent.queue import Queue
from src.BusinessCentralLayer.setting import logger, SERVER_DIR_DATABASE_CACHE
from src.BusinessLogicLayer.cluster.prism import ServiceDiscovery

runtime_queue = Queue()
SERVICE_TYPE = "v2ray"
RUNTIME_POWER = 4


def preload(get_sample: bool = True):
    """
    If the parameter `register_url` is none, the sample is loaded.
    :param get_sample:
    :return:
    """
    with open('staff_arch_general.txt', 'r', encoding='utf8') as f:
        urls = [i for i in f.read().split('\n') if i]
    if get_sample:
        return random.choice(urls)
    return urls


def get_default_heap() -> str:
    output_path_csv = f"runtime_report_{str(datetime.now()).split(' ')[0]}_{str(time.time()).split('.')[0]}.csv"
    return os.path.join(SERVER_DIR_DATABASE_CACHE, output_path_csv)


def action(register_url: str = None, share_type="v2ray", output_path_csv=None):
    """

    :param output_path_csv:
    :param share_type:
    :param register_url: 无验证 provider
    :return:
    """
    # If the parameter `register_url` is none, the sample is loaded.
    register_url = preload() if register_url is None else register_url
    # 报告存储路径
    output_path_csv = get_default_heap() if output_path_csv is None else output_path_csv
    try:
        machine = ServiceDiscovery(register_url, silence=True, output_path_csv=output_path_csv)
        # 解析运行报告
        runtime_report = machine.get_runtime_report(share_type)
        # 缓存运行报告
        cache_path = machine.save_runtime_report(list(runtime_report.values()))
        return cache_path
    # Service refused! The sample site has security holes.register_url={}".format(register_url)
    except TypeError:
        pass


def middleware():
    while not runtime_queue.empty():
        url = runtime_queue.get_nowait()
        action(url, SERVICE_TYPE, DEFAULT_HEAP)


def demo_with_gevent(auto_start=True):
    # Get demo sites.
    data_set = preload(get_sample=False)

    # Tasks Offload.
    for url in data_set:
        runtime_queue.put_nowait(url)

    # Tasks Overload.
    task_container = []
    for x in range(RUNTIME_POWER):
        task = gevent.spawn(middleware)
        task_container.append(task)
    gevent.joinall(task_container)

    # Open report file.
    if auto_start:
        os.startfile(DEFAULT_HEAP)
    logger.info(f"<ServiceDiscovery> 任务结束，相关数据已缓存至-->{DEFAULT_HEAP}")


if __name__ == '__main__':
    DEFAULT_HEAP = get_default_heap()
    demo_with_gevent()
