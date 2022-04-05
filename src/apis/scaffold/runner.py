# -*- coding: utf-8 -*-
# Time       : 2021/12/22 22:03
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import sys
from typing import Optional, Union, Dict, List, Any

from services.collector import __entropy__
from services.collector import devil_king_armed
from services.collector.exceptions import UnknownNestTypeException
from services.middleware.subscribe_io import SubscribeManager
from services.middleware.workers_io import EntropyHeap
from services.settings import logger
from services.utils import ToolBox
from services.utils.accelerator.core import CoroutineSpeedup


class SpawnBooster(CoroutineSpeedup):
    def __init__(self, docker, **kwargs):
        super().__init__(docker=docker)

        self.silence = kwargs.get("silence", True)

    def overload(self):
        for atomic in self.docker:
            try:
                cirilla = devil_king_armed(
                    atomic=atomic, silence=self.silence, mirror=True
                )
            except UnknownNestTypeException:
                logger.warning(
                    ToolBox.runtime_report(
                        motive="REJECT",
                        action_name="SpawnBooster",
                        message="Unknown ``nest`` type, must belong to [sspanel v2board]",
                        error_input=atomic.get("nest", "unknown"),
                    )
                )
            else:
                self.worker.put_nowait(cirilla)

        self.max_queue_size = self.worker.qsize()

    def control_driver(self, cirilla, *args, **kwargs):
        cirilla(sm=kwargs.get("sm"))


def booster(
    docker: Union[Dict[str, Any], List[Dict[str, Any]]], silence: bool, power: int = 1
):
    """
    上古之血催化剂

    :param docker:
    :param silence:
    :param power:
    :return:
    """

    sm = SubscribeManager()

    logger.success(
        ToolBox.runtime_report(
            motive="SPAWN",
            action_name="SpawnBooster",
            message="The Elder Blood is about to be activated!",
        )
    )

    # 单例的镜像生产
    if isinstance(docker, dict):
        if power == 1:
            devil_king_armed(atomic=docker, silence=silence, mirror=True)(sm=sm)
        elif power >= 5:
            return logger.warning(
                f"The power({power}) of BoosterEngine has exceeded performance expectations."
                "Please make it less than power(5)."
            )
        else:
            SpawnBooster(docker=[docker] * power, silence=silence).go(sm=sm)
    # 灌入 entropy 生产队列
    elif isinstance(docker, list):
        SpawnBooster(docker=docker, silence=silence).go(sm=sm)


def spawn(
    silence: Optional[bool] = True,
    power: Optional[int] = 4,
    join: Optional[bool] = False,
    remote: Optional[bool] = False,
    safe: Optional[bool] = False,
):
    # 读取（远程 / 本地）执行队列
    eh = EntropyHeap()
    pending_entropy = eh.sync() if remote is True else __entropy__

    # 过滤需要对抗的实例
    if safe:
        for atomic in reversed(pending_entropy):
            for params in atomic["hyper_params"]:
                if "anti_" in params:
                    pending_entropy.remove(atomic)

    # 加入协同实例
    elif join:
        pending_entropy = [
            atomic
            for atomic in pending_entropy
            if not atomic["hyper_params"].get("synergy")
        ]

    # Power 调优最佳实践
    if not isinstance(power, int):
        if os.cpu_count() <= 4:
            power = min(pending_entropy.__len__(), os.cpu_count())
        else:
            power = 3
    else:
        power = abs(power)

    # 静默/显示启动参数调整
    silence = True if "linux" in sys.platform else bool(silence)

    # 生产运行实例
    booster(docker=pending_entropy, power=power, silence=silence)
