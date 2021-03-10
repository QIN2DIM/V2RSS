# TODO :demand：测试机场是否符合staff标准（use gevent）
__all__ = ['GhostFiller']

from src.BusinessCentralLayer.coroutine_engine import CoroutineSpeedup


class GhostFiller(CoroutineSpeedup):
    def __init__(self, docker, silence: bool = False, power: int = 1):
        """

        @param docker: 需要测试或快速填充的机场实例
        @param silence: 是否静默启动
        @param power: 发起次数,采用协程策略，既一次性并发count个任务
        @return:
        """
        super(GhostFiller, self).__init__()

        # 参数初始化
        self.power = power
        self.docker = docker
        self.silence = silence
        self.docker_behavior = "self.docker(self.silence).run()"

        # 为并发任务打入协程加速补丁
        if power > 1:
            exec("from gevent import monkey\nmonkey.patch_all(ssl=False)")

        # 自启任务
        self.interface()

    def offload_task(self):
        for _ in range(self.power):
            self.work_q.put_nowait(self.docker_behavior)

    def control_driver(self, docker_behavior: str):
        exec(docker_behavior)
