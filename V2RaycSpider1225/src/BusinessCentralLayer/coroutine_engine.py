__all__ = ['vsu', 'lsu', 'PuppetCore']

from typing import List, Dict

import gevent
from gevent.queue import Queue

from src.BusinessCentralLayer.middleware.work_io import Middleware
from src.BusinessCentralLayer.setting import logger


class CoroutineEngine(object):
    """协程加速控件"""

    def __init__(self, core, power: int = None, **kwargs) -> None:
        """

        :param core: 驱动核心
        :param power: 协程功率
        :param progress_name: 进度条
        """
        # 初始化参数
        self.max_queue_size = 0
        self.power = power

        # 驱动器
        self.core = core

        # 额外参数
        self.config_path = kwargs.get("config_path")  # 配置文件
        self.docker = kwargs.get("docker")  # 业务列表
        self.progress_name = kwargs.get('progress_name')  # 进度条注释
        self.silence = kwargs.get('silence')  # selenium 静默启动
        self.work_Q = Queue()

    def load_tasks(self, tasks: list) -> None:
        if isinstance(tasks, list):
            for task in tasks:
                self.work_Q.put_nowait(task)

    def flexible_power(self):
        """
        @todo 优化弹性协程算法
        @return:
        """
        import os
        # 若未指定self.power 则使用弹性协程方案调度资源
        if not self.power:
            self.max_queue_size = self.work_Q.qsize()
            # limit = round((psutil.cpu_count() / CRAWLER_SEQUENCE.__len__()))
            limit = os.cpu_count()

            self.power = limit if self.max_queue_size >= limit else self.max_queue_size

    def launch(self, ) -> None:
        while not self.work_Q.empty():
            task = self.work_Q.get_nowait()
            self.control_driver(task)

    def control_driver(self, task) -> None:
        """
        重写此模块
        :param task:
        :return:
        """

    def progress_manager(self, total, desc='Example', leave=True, ncols=100, unit='B', unit_scale=True) -> None:
        """
        进度监测
        :return:
        """
        from tqdm import tqdm
        import time
        # iterable: 可迭代的对象, 在手动更新时不需要进行设置
        # desc: 字符串, 左边进度条描述文字
        # page_size: 总的项目数
        # leave: bool值, 迭代完成后是否保留进度条
        # file: 输出指向位置, 默认是终端, 一般不需要设置
        # ncols: 调整进度条宽度, 默认是根据环境自动调节长度, 如果设置为0, 就没有进度条, 只有输出的信息
        # unit: 描述处理项目的文字

        with tqdm(total=total, desc=desc, leave=leave, ncols=ncols,
                  unit=unit, unit_scale=unit_scale) as progress_bar:
            progress_bar.update(self.power)
            # while self.max_queue_size != Middleware.hera.qsize():
            #     progress_bar.update(Middleware.hera.qsize())
            #     time.sleep(1)
            while not self.work_Q.empty():
                now_1 = self.work_Q.qsize()
                time.sleep(0.1)
                now_2 = self.work_Q.qsize() - now_1
                progress_bar.update(abs(now_2))

    def run(self, speed_up=True, use_bar=False) -> None:
        """
        协程任务接口
        :return:
        """
        task_list = []

        if isinstance(self.docker, list):
            # 刷新任务队列
            self.load_tasks(tasks=self.docker)
        else:
            # 业务交接
            self.work_Q = self.docker

        # 弹性协程
        if not speed_up:
            self.power = 1
        else:
            self.flexible_power()
        logger.info(f'<Gevent> Flexible Power:{self.power} || Queue Capacity:{self.max_queue_size}')

        # 启动进度条
        if use_bar:
            import threading
            threading.Thread(target=self.progress_manager,
                             args=(self.max_queue_size, self.progress_name + '[{}]'.format(self.power))).start()

        for x in range(self.power):
            task = gevent.spawn(self.launch)
            task_list.append(task)
        gevent.joinall(task_list)


class V2raycSpiderSpeedUp(CoroutineEngine):
    """协程控件继承"""

    def __init__(self, core, docker: Middleware.poseidon or list = None, interface='run', power: int = None) -> None:
        super(V2raycSpiderSpeedUp, self).__init__(core=core, power=power, docker=docker,
                                                  progress_name=f'{self.__class__.__name__}')
        self.interface = interface

    def control_driver(self, task) -> None:
        exec(f'self.core.{self.interface}(task)')


class LightweightSpeedup(object):
    """轻量化的协程控件"""

    def __init__(self, work_q: Queue = Queue(), task_docker=None, power: int = None):
        self.work_q = work_q
        self.task_docker = task_docker
        self.power = power
        self.temp_cache: Dict[str:int] = {}
        self.apollo: List[List[str]] = []

    def launch(self):
        while not self.work_q.empty():
            task = self.work_q.get_nowait()
            self.control_driver(task)

    @staticmethod
    def step_wait():
        gevent.sleep(1)

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

    def killer(self):
        """

        @return:
        """

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

        for x in range(power_):
            task = gevent.spawn(self.launch)
            task_list.append(task)
        gevent.joinall(task_list)
        self.killer()

        logger.success(f'<Gevent> mission completed -- <{self.__class__.__name__}>')


class PuppetCore(object):
    @staticmethod
    def run(expr: str):
        exec(expr)


QuickDumps = type("QuickDumps", (object,), {"run": lambda expr: exec(expr)})
vsu = V2raycSpiderSpeedUp
lsu = LightweightSpeedup
