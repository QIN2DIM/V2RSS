# -*- coding: utf-8 -*-
# Time       : 2021/12/22 22:04
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from typing import Optional, List, Dict, Any

from services.collector import __entropy__
from services.middleware.workers_io import EntropyHeap
from services.settings import logger, POOL_CAP
from services.utils import CoroutineSpeedup
from services.utils import ToolBox

eh = EntropyHeap()


def update() -> None:
    """更新远程队列"""
    eh.update(local_entropy=__entropy__)

    logger.success(
        ToolBox.runtime_report(
            motive="UPDATE",
            action_name="ScaffoldEntropy",
            message="update remote tasks queue.",
        )
    )


def preview(remote: Optional[bool] = False) -> None:
    """输出任务队列信息"""
    # 将要输出的摘要数据 <localQueue> or <remoteQueue>
    check_entropy = __entropy__ if not remote else eh.sync()

    # 当摘要数据非空时输出至控制台
    if check_entropy:
        for i, atomic in enumerate(check_entropy):
            print(f">>> [{i + 1}/{check_entropy.__len__()}]{atomic['name']}")
            print(f"注入地址: {atomic['register_url']}")
            print(f"渲染引擎: {atomic.get('nest', 'unknown')}")
            print(f"生命周期: {atomic.get('life_cycle', 24)}小时")
            print(f"超级参数: {atomic.get('hyper_params')}\n")

        logger.success(
            ToolBox.runtime_report(motive="PREVIEW", action_name="ScaffoldEntropy")
        )
    else:
        logger.warning(
            ToolBox.runtime_report(
                motive="PREVIEW", action_name="ScaffoldEntropy", message="empty entropy."
            )
        )


def check(power: Optional[int] = None) -> None:
    """检查任务队列心跳"""

    class EntropyChecker(CoroutineSpeedup):
        """协程助推器 加速代码片段"""

        def __init__(self, docker, utils):
            super().__init__(docker=docker)
            self.control_driver = utils

    mirror_entropy: List[Dict[str, Any]] = __entropy__

    power = mirror_entropy.__len__() if not isinstance(power, int) else abs(power)

    urls = list({atomic["register_url"] for atomic in mirror_entropy.copy()})

    sug = EntropyChecker(docker=urls, utils=ToolBox.check_html_status)
    sug.go(power=power, action_name="ScaffoldEntropy")

    logger.success(ToolBox.runtime_report(motive="CHECK", action_name="ScaffoldEntropy"))


def cap(new_capacity: int = None) -> None:
    """重设任务队列容量"""
    if not new_capacity:
        return

    new_capacity = new_capacity if isinstance(new_capacity, int) else POOL_CAP
    if new_capacity <= 2 or new_capacity >= 28:
        logger.error(
            ToolBox.runtime_report(
                motive="SET POOL CAPACITY",
                action_name="ScaffoldEntropy",
                message=f"new_capacity({new_capacity}) 设置不合理",
            )
        )
        return

    stable_capacity = eh.get_unified_cap()

    eh.set_new_cap(new_capacity)

    logger.success(
        ToolBox.runtime_report(
            motive="SET POOL CAPACITY",
            action_name="ScaffoldEntropy",
            message="更新远程队列容量",
            new_capacity=new_capacity,
            old_capacity=stable_capacity,
        )
    )
