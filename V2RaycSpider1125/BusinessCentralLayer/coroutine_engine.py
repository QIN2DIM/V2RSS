# FIXME:
#  若您为项目开发者 请不要在生产环境中启用进度条功能 <- 未知bug


__all__ = ['V2rayCloudSpiderSpeedUp', 'PuppetCore']

import gevent
from gevent.queue import Queue


class CoroutineEngine(object):
    """协程加速控件"""

    def __init__(self, core, power: int = 8, **kwargs) -> None:
        """

        :param core: 驱动核心
        :param power: 协程功率
        :param progress_name: 进度条
        """
        # 初始化参数
        self.max_queue_size = 0
        self.power = power
        self.work_Q = Queue()

        # 驱动器
        self.core = core

        # 额外参数
        self.config_path = kwargs.get("config_path")  # 配置文件
        self.user_cluster = kwargs.get("user_cluster")  # 业务列表
        self.progress_name = kwargs.get('progress_name')  # 进度条注释
        self.silence = kwargs.get('silence')  # selenium 静默启动

    def load_tasks(self, tasks=None) -> None:
        if isinstance(tasks, list):
            for task in tasks:
                self.work_Q.put_nowait(task)
        elif not tasks:
            pass

        self.max_queue_size = self.work_Q.qsize()
        # 弹性协程
        self.power = 72 if self.max_queue_size >= 72 else self.max_queue_size

    def launch(self, ) -> None:
        while not self.work_Q.empty():
            task = self.work_Q.get_nowait()
            self.control_driver(task)

    # 移交外部控制权
    def control_driver(self, task) -> None:
        """
        重写此模块
        :param task:
        :return:
        """

    # 进度条
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
            while not self.work_Q.empty():
                now_1 = self.work_Q.qsize()
                time.sleep(0.1)
                now_2 = self.work_Q.qsize() - now_1
                progress_bar.update(abs(now_2))

    # 入口
    def run(self, speed_up=True, use_bar=False) -> None:
        """
        协程任务接口
        :return:
        """
        task_list = []

        # 刷新任务队列
        self.load_tasks(tasks=self.user_cluster)

        # 启动进度条
        if use_bar:
            import threading
            threading.Thread(target=self.progress_manager,
                             args=(self.max_queue_size, self.progress_name + '[{}]'.format(self.power))).start()

        # 弹性协程
        if not speed_up:
            self.power = 1

        for x in range(self.power):
            task = gevent.spawn(self.launch)
            task_list.append(task)
        gevent.joinall(task_list)


class V2rayCloudSpiderSpeedUp(CoroutineEngine):
    """协程控件继承"""

    def __init__(self, core, user_cluster=None, interface='run', power: int = None) -> None:
        super(V2rayCloudSpiderSpeedUp, self).__init__(core=core, power=power, user_cluster=user_cluster,
                                                      progress_name=f'{self.__class__.__name__}')
        self.interface = interface

    def control_driver(self, task) -> None:
        exec(f'self.core.{self.interface}(task)')


class PuppetCore(object):
    @staticmethod
    def run(expr: str):
        exec(expr)


QuickDumps = type("QuickDumps", (object,), {"run": lambda expr: exec(expr)})
