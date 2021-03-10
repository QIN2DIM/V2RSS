# TODO :demand：用于释放/执行链接采集任务
__all__ = ['ShuntRelease']

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


if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()
