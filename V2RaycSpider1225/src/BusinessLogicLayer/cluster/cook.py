# TODO :demand：用于补充某种类型的链接，将抽象机场信息实例化
# 1. 遍历所有"可用"机场实例
# 2. 审核授权
#   if 该机场不具备该类型链接的采集权限，剔除。
#   elif 该机场同时具备其他类型的采集权限，权限收缩（改写），实例入队。
#   else 该机场仅具备该类型任务的采集权限，实例入队。
__all__ = ['ActionShunt', 'devil_king_armed', 'reset_task']

from src.BusinessCentralLayer.setting import CRAWLER_SEQUENCE, CHROMEDRIVER_PATH
from .master import ActionMasterGeneral
from .slavers import __entropy__


class ActionShunt:
    def __init__(self, class_, silence=True, beat_sync=True):
        """

        :param class_: 订阅类型
        :param silence:
        :param beat_sync:
        """
        self.class_ = class_
        self.work_seq = CRAWLER_SEQUENCE
        self.silence, self.beat_sync = silence, beat_sync

        # output
        self.shunt_seq = []
        self.atomic_seq = []

    # -----------------------------------------
    # public
    # -----------------------------------------

    @staticmethod
    def generate_entity(atomic: dict, silence=True, beat_sync=True, assault=False):
        return ActionMasterGeneral(
            silence=silence,
            beat_sync=beat_sync,
            action_name=atomic['name'],
            register_url=atomic['register_url'],
            anti_slider=atomic['anti_slider'],
            life_cycle=atomic['life_cycle'],
            email=atomic['email'],
            hyper_params=atomic['hyper_params'],
            assault=assault
        ).run

    def shunt(self):
        self._shunt_action()
        self._pop_atomic()
        return self.shunt_seq

    # -----------------------------------------
    # private
    # -----------------------------------------

    def _shunt_action(self):
        action_list = __entropy__.copy()
        for action_tag in action_list:
            action_entropy = action_tag.get('hyper_params')
            # if 该订阅源不具备某指定类型链接的采集权限，剔除。
            if not action_entropy.get(self.class_):
                continue
            self.atomic_seq.append(action_tag)

    def _pop_atomic(self):
        while True:
            # 当步态特征列表无剩余选项时结束迭代任务
            if self.atomic_seq.__len__() < 1:
                break
            # 取出机场步态特征的原子描述
            atomic = self.atomic_seq.pop()
            # 权限原子化 ‘ssr’ or 'v2ray' ...
            for passable_trace in self.work_seq:
                if passable_trace != self.class_:
                    atomic['hyper_params'][passable_trace] = False

            # 根据步态特征实例化任务
            entity_ = self.generate_entity(atomic=atomic, silence=self.silence, beat_sync=self.beat_sync)
            # 将实例化任务加入待执行队列
            self.shunt_seq.append(entity_)


class DevilKingArmed(ActionMasterGeneral):

    def __init__(self, register_url, chromedriver_path,
                 silence: bool = True, assault: bool = False, beat_sync: bool = True,
                 email: str = None, life_cycle: int = None, anti_slider: bool = False,
                 hyper_params: dict = None, action_name: str = None, debug: bool = False, ):
        super(DevilKingArmed, self).__init__(register_url=register_url, chromedriver_path=chromedriver_path,
                                             silence=silence, assault=assault, beat_sync=beat_sync,
                                             email=email, life_cycle=life_cycle, anti_slider=anti_slider,
                                             hyper_params=hyper_params, action_name=action_name, debug=debug)


def devil_king_armed(atomic: dict, silence=True, beat_sync=True, assault=False):
    return DevilKingArmed(
        beat_sync=beat_sync,
        assault=assault,
        silence=silence,
        chromedriver_path=CHROMEDRIVER_PATH,
        register_url=atomic['register_url'],
        action_name=atomic['name'],
        anti_slider=atomic['anti_slider'],
        life_cycle=atomic['life_cycle'],
        email=atomic['email'],
        hyper_params=atomic['hyper_params'],
    )


def reset_task() -> list:
    import random
    from src.BusinessCentralLayer.middleware.redis_io import RedisClient
    from src.BusinessCentralLayer.setting import SINGLE_TASK_CAP, REDIS_SECRET_KEY

    rc = RedisClient()
    running_state = dict(zip(CRAWLER_SEQUENCE, [[] for _ in range(len(CRAWLER_SEQUENCE))]))
    action_list = __entropy__.copy()
    qsize = len(action_list)
    random.shuffle(action_list)
    try:
        # 进行各个类型的实体任务的分类
        for task_name in CRAWLER_SEQUENCE:
            # 获取池中对应类型的数据剩余
            storage_remain: int = rc.get_len(REDIS_SECRET_KEY.format(f'{task_name}'))
            # 进行各个类型的实体任务的分类
            for atomic in action_list:
                permission = {} if atomic.get('hyper_params') is None else atomic.get('hyper_params')
                if permission.get(task_name) is True:
                    running_state[task_name].append(atomic)
            # 在库数据溢出 返回空执行队列
            if storage_remain >= SINGLE_TASK_CAP:
                running_state[task_name] = []
            # 缓存+保存数据超过风险阈值
            while storage_remain + qsize > int(SINGLE_TASK_CAP * 0.8):
                if len(running_state[task_name]) < 1:
                    break
                running_state[task_name].pop()
                qsize -= 1

        instances = [atomic for i in list(running_state.values()) if i for atomic in i]
        return instances
    # 网络异常，主动捕获RedisClient()的连接错误
    except ConnectionError:
        return []
