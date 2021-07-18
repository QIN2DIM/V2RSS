"""
- 核心功能：
    - 测试机场是否符合staff标准
    - 用于actions单步调试机场任务
"""
from src.BusinessLogicLayer.plugins.accelerator.core import CoroutineSpeedup


class ActionBooster(CoroutineSpeedup):
    def __init__(self, docker: dict, silence: bool = False, assault=False):
        """

        @param docker: 需要测试或快速填充的抽象步态字典，既仅从cluster-actions中读取
        @param silence: 是否静默启动
        @return:
        """
        super(ActionBooster, self).__init__()

        # ====================================================
        # 参数初始化
        # ====================================================
        self.docker = docker
        self.silence = silence
        self.debug_logger = False
        self.run = self.interface

        # ====================================================
        # 根据步态特征获取实例化任务
        # ====================================================
        from src.BusinessLogicLayer.cluster.cook import ActionShunt
        # entity: ActionMaster 的行为抽象，此处为原子化操作，实体数仅为1
        self.entity_ = ActionShunt.generate_entity(atomic=docker, silence=silence, assault=assault)

    def offload_task(self):
        self.work_q.put_nowait(self.entity_)

    def control_driver(self, entity_):
        try:
            # 将高度抽象（压缩）的行为（Function）解压执行
            entity_()
        except Exception as e:
            print(e)
            return False


def booster(docker: dict or list, silence: bool, power: int = 1, assault=False):
    import gevent

    task_list = []

    if isinstance(docker, list) and docker.__len__() == 1 and isinstance(docker[0], dict):
        docker = docker[0]

    # 对单个实体进行行为测试
    if isinstance(docker, dict):
        # 默认对该实体发起一次行为测试
        if power == 1:
            ActionBooster(docker=docker, silence=silence, assault=assault).run()
        # 对该实体发起power次并发的行为测试[使用gevent]
        elif power > 1:
            for _ in range(power):
                task = gevent.spawn(ActionBooster(docker=docker, silence=silence, assault=assault).run)
                task_list.append(task)
            gevent.joinall(task_list)

    # 对多个实体进行行为测试（length of entity_set >= 2）
    elif isinstance(docker, list):
        # 每个实体的行为测试被依次发起
        if power == 1:
            for i in range(docker.__len__()):
                ActionBooster(docker=docker[i], silence=silence, assault=assault).run()
        # 建立协程空间，分发实体行为测试任务[use gevent]
        elif power == docker.__len__():
            for i in range(docker.__len__()):
                task = gevent.spawn(ActionBooster(docker=docker[i], silence=silence, assault=assault).run)
                task_list.append(task)
            gevent.joinall(task_list)
        # 建立多核工作栈，使用弹性分发控件对服务器进行边缘压力测试
        elif power == -1:
            return True
