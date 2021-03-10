# TODO :demand：用于释放/执行链接采集任务
__all__ = ['ShuntRelease', 'ForceRunRelease']

import os

from src.BusinessCentralLayer.coroutine_engine import CoroutineSpeedup
from src.BusinessCentralLayer.setting import logger


class ShuntRelease(CoroutineSpeedup):
    def __init__(self, work_queue=None, task_docker: list = None, power: int = os.cpu_count()):
        super(ShuntRelease, self).__init__(work_q=work_queue, task_docker=task_docker, power=power)

    def control_driver(self, shunt_pointer):
        try:
            shunt_pointer()
        except Exception as e:
            logger.exception(e)


class ForceRunRelease(CoroutineSpeedup):
    def __init__(self, task_docker: list = None, power: int = os.cpu_count()):
        super(ForceRunRelease, self).__init__(task_docker=task_docker, power=power)

        from src.BusinessLogicLayer.cluster.sailor import manage_task

        self.core = manage_task

    def control_driver(self, task):
        self.core(class_=task, beat_sync=True, force_run=True)


if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()
