"""
核心功能：单步调试actions-entropy任务
"""

from src.BusinessLogicLayer.cluster.cook import ActionShunt
from src.BusinessLogicLayer.cluster.prism import Prism
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
        self.docker = docker if isinstance(docker, list) else [docker, ]
        self.jobs = []

        # 其他SpawnBooster参数
        self.debug_logger = False
        self.run = self.interface

        # silence：driver静默启动设置
        self.silence = silence
        # assault：driver加速渲染设置
        self.assault = assault

    def offload_task(self):
        # 根据步态特征获取实例化任务
        for mirror_image in self.docker:
            # entity: ActionMaster 的行为抽象，此处为原子化操作，实体数仅为1
            if mirror_image.get("feature") == 'prism':
                entity_ = Prism(atomic=mirror_image, silence=self.silence, assault=self.assault).run
            else:
                entity_ = ActionShunt.generate_entity(atomic=mirror_image, silence=self.silence, assault=self.assault)
            # 将运行实体加入任务队列
            self.work_q.put_nowait(entity_)
            self.jobs.append(entity_)

    def control_driver(self, entity_):
        # 将高度抽象（压缩）的行为（Function）解压执行
        # 考虑到本例仅在人机调试时使用，故不采用任何exception捕获方案，期望错误弹出
        entity_()


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
            ActionShunt.generate_entity(atomic=docker, silence=silence, assault=assault)()
        # 对该实体发起power次并发的行为测试[使用gevent]
        elif power > 1:
            SpawnBooster(docker=[docker, ] * power, silence=silence, assault=assault).run(power)

    # 该方法针对scaffold_spawn 实现相关接口，经典用法为灌入__entropy__
    # 此时认为docker_list.__len__()>=2，否则将会被识别为单个实体分流至其他业务模块
    elif isinstance(docker, list):
        # 每个实体的行为测试被依次发起
        if power == 1:
            for mirror_image in docker:
                ActionShunt.generate_entity(atomic=mirror_image, silence=silence, assault=assault)()
        # 建立多核工作栈，使用弹性分发控件对服务器进行边缘压力测试
        elif power == -1:
            return True
        # 建立协程空间，分发实体行为测试任务[use gevent]
        else:
            SpawnBooster(docker=docker, silence=silence, assault=assault).run(power)
