"""
- 核心功能：
    - “解压”与实例化采集器管理模块
    - 加速器性能释放
"""
from src.BusinessCentralLayer.setting import logger, DEFAULT_POWER
from .core import CoroutineSpeedup


class ShuntRelease(CoroutineSpeedup):
    """accelerator性能释放关口"""

    def __init__(self, work_queue=None, task_docker: list = None, power: int = DEFAULT_POWER):
        super(ShuntRelease, self).__init__(work_q=work_queue, task_docker=task_docker, power=power)

    def control_driver(self, shunt_pointer):
        try:
            shunt_pointer()
        except Exception as e:
            logger.exception(e)


class ForceRunRelease(CoroutineSpeedup):
    """collector管理器实例化关口"""

    def __init__(self, task_docker: list = None, power: int = DEFAULT_POWER):
        super(ForceRunRelease, self).__init__(task_docker=task_docker, power=power)

        from src.BusinessLogicLayer.cluster.sailor import manage_task

        self.core = manage_task

    def control_driver(self, task):
        self.core(class_=task, beat_sync=True, force_run=True)
