__all__ = ['CoroutineSpeedup']

from typing import List, Dict

import gevent
from gevent.queue import Queue

from src.BusinessCentralLayer.setting import logger


class CoroutineSpeedup(object):
    """轻量化的协程控件"""

    def __init__(self, work_q: Queue = Queue(), task_docker=None, power: int = None):
        self.work_q = work_q
        self.task_docker = task_docker
        self.power = power

        self.max_queue_size = 0

        self.temp_cache: Dict[str:int] = {}
        self.apollo: List[List[str]] = []

    def launch(self):
        while not self.work_q.empty():
            task = self.work_q.get_nowait()
            self.control_driver(task)

    def control_driver(self, task):
        """
        rewrite this method
        @param task:
        @return:
        """

    def offload_task(self):
        """

        @return:
        """
        if not self.work_q and self.task_docker:
            for task in self.task_docker:
                self.work_q.put_nowait(task)
            self.max_queue_size = self.work_q.qsize()

    def killer(self):
        """

        @return:
        """
        pass

    def interface(self, power: int = 8) -> None:
        """

        @param power: 协程功率
        @return:
        """

        # 任务重载
        self.offload_task()

        # 任务启动
        task_list = []
        power_ = self.power if self.power else power

        if self.max_queue_size != 0:
            power_ = self.max_queue_size if power_ > self.max_queue_size else power_

        for x in range(power_):
            task = gevent.spawn(self.launch)
            task_list.append(task)
        gevent.joinall(task_list)

        self.killer()

        logger.success(f'<Gevent> mission completed -- <{self.__class__.__name__}>')
