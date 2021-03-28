# TODO :demand：测试机场是否符合staff标准（use gevent） 用于单步调试机场任务的接口
__all__ = ['GhostFiller', 'gevent_ghost_filler']

from src.BusinessCentralLayer.coroutine_engine import CoroutineSpeedup


class GhostFiller(CoroutineSpeedup):
    def __init__(self, docker: dict, silence: bool = False):
        """

        @param docker: 需要测试或快速填充的抽象步态字典，既仅从cluster-actions中读取
        @param silence: 是否静默启动
        @return:
        """
        super(GhostFiller, self).__init__()

        # 参数初始化
        self.docker = docker
        self.silence = silence
        self.debug_logger = False

        # 根据步态特征获取实例化任务
        from src.BusinessLogicLayer.apis.shunt_cluster import ActionShunt
        self.entity_ = ActionShunt.generate_entity(atomic=docker, silence=silence)
        self.run = self.interface

    def offload_task(self):
        self.work_q.put_nowait(self.entity_)

    def control_driver(self, entity_):
        try:
            entity_()
        except Exception as e:
            print(e)
            return False


def gevent_ghost_filler(docker: dict, silence: bool, power: int = 1):
    import gevent
    from concurrent.futures.thread import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=power) as t:
        for _ in range(power):
            t.submit(GhostFiller(docker=docker, silence=silence).run)

    # task_list = []
    # for _ in range(power):
    #     task = gevent.spawn()
    #     task_list.append(task)
    # gevent.joinall(task_list)
