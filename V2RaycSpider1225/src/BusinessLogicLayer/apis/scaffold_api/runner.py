# -*- coding: utf-8 -*-
# Time       : 2021/12/20 12:37
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import sys

from BusinessCentralLayer.middleware.redis_io import EntropyHeap
from BusinessLogicLayer.cluster.slavers.actions import __entropy__
from BusinessLogicLayer.plugins.accelerator import booster


def spawn(
        silence: bool = True,
        power: int = 4,
        join: bool = False,
        remote: bool = False
):
    """

    :param silence:
    :param power:
    :param join:
    :param remote:
    :return:
    """
    # 读取（远程 / 本地）执行队列
    eh = EntropyHeap()
    pending_docker = eh.sync() if remote is True else __entropy__
    docker = (
        pending_docker
        if join
        else [i for i in __entropy__ if not i["hyper_params"].get("co-invite")]
    )

    # Power 调优最佳实践
    if power is None:
        if os.cpu_count() <= 4:
            power = min(docker.__len__(), os.cpu_count())
        else:
            power = 3

    # 静默/显示启动参数调整
    silence = True if "linux" in sys.platform else bool(silence)

    # 生产运行实例
    booster(
        docker=docker,
        silence=silence,
        power=power,
        assault=True,
    )
