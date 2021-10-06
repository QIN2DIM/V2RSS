# feat  service-discovery-general
# - [×] base on gevent
# - [√] 订阅链接不存储
# - [√] 订阅链接解析
# - [√] 任务1：是否可用（基于类型的判断）
# - [√] 任务2：可用时长，可用流量（不自动签到）
# - [√] 任务3：实体存储，生成统计报表
#   - Format
#       provider        subType     passable        enDay       enFlow      nodeNum     context
#       https://        v2ray       yes/no          1day/nil    2G/nil      8/0         ...

import os
import random
import shlex

from src.BusinessCentralLayer.setting import logger
from src.BusinessLogicLayer.cluster.prism import ServiceDiscovery


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


def demo(register_url: str = preload(), silence=True, share_type="v2ray", start_cache: bool = False):
    """

    :param start_cache:
    :param share_type:
    :param silence:
    :param register_url: 无验证 provider
    :return:
    """
    try:
        machine = ServiceDiscovery(register_url, silence=silence)
        # 解析运行报告
        runtime_report = machine.get_runtime_report(share_type)
        # 缓存运行报告
        cache_path = machine.save_runtime_report(list(runtime_report.values()))
        # 自动打开文件
        if start_cache:
            os.startfile(shlex.quote(cache_path))
    except TypeError:
        logger.warning("服务拒绝！此站点存在安全漏洞。")
    finally:
        logger.info("demo 执行完毕")


if __name__ == '__main__':
    demo(silence=True, start_cache=True)
