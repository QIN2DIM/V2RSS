"""
核心功能：单步调试actions-entropy任务
"""
import warnings

from BusinessLogicLayer.cluster.cook import ActionShunt
from .core import CoroutineSpeedup


class SpawnBooster(CoroutineSpeedup):
    def __init__(self, docker: dict or list, silence: bool = False, assault=False):
        """
        :param docker: 需要测试的抽象步态字典，针对__entropy__实体测试使用
        :param silence: 是否静默启动
        :param assault:
        """
        super(SpawnBooster, self).__init__()

        # 当仅测试1枚实例时设置self.power=1既单例启动，否则将self.power置为None
        # 当self.power = None时，实际的采集功率将由弹性协程接口自动计算
        self.power = 1 if isinstance(docker, dict) else None

        # 将单例视为容量为1的sequence
        # 允许sequence中出现重复的任务
        self.docker = (
            docker
            if isinstance(docker, list)
            else [
                docker,
            ]
        )
        self.jobs = []

        # 其他SpawnBooster参数
        self.debug_logger = False
        self.run = self.interface

        # silence：driver静默启动设置
        self.silence = silence
        # assault：driver加速渲染设置
        self.assault = assault

    def offload_task(self):
        # 将运行实体加入任务队列
        for atomic in self.docker:
            entity_ = ActionShunt.generate_entity(
                atomic=atomic,
                silence=self.silence,
                assault=self.assault
            )
            self.work_q.put_nowait(entity_)
            self.jobs.append(entity_)

    def control_driver(self, task):
        """
        # 将高度抽象（压缩）的行为（Function）解压执行
        # 考虑到本例仅在人机调试时使用，故不采用任何exception捕获方案，期望错误弹出
        :param task:
        :return:
        """
        task()


def booster(docker: dict or list, silence: bool, power: int = 1, assault=False):
    """

    :param docker:
    :param silence:
    :param power:
    :param assault:
    :return:
    """

    # 对单个实体进行power次测试，当power>=2时使用gevent完成任务
    if isinstance(docker, dict):
        # 对该实体发起一次行为测试
        if power == 1:
            ActionShunt.generate_entity(
                atomic=docker, silence=silence, assault=assault
            )()
        # 对该实体发起power次并发的行为测试[使用gevent]
        elif power > 1:
            if power > 16:
                return warnings.warn(
                    "The power of BoosterEngine has exceeded performance expectations."
                    "Please make it less than 16."
                )
            SpawnBooster(
                docker=[docker, ] * power,
                silence=silence,
                assault=assault,
            ).run(power)

    # 将送测实体灌入协程引擎，每个标注实体执行一次
    elif isinstance(docker, list):
        SpawnBooster(
            docker=docker,
            silence=silence,
            assault=assault
        ).run(power)
    return True
