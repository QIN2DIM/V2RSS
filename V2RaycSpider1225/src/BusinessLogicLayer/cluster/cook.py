# TODO :demand：用于补充某种类型的链接，将抽象机场信息实例化
# 1. 遍历所有"可用"机场实例
# 2. 审核授权
#   if 该机场不具备该类型链接的采集权限，剔除。
#   elif 该机场同时具备其他类型的采集权限，权限收缩（改写），实例入队。
#   else 该机场仅具备该类型任务的采集权限，实例入队。
__all__ = ['ActionShunt']

from src.BusinessCentralLayer.setting import CRAWLER_SEQUENCE
from src.BusinessLogicLayer.cluster.master import ActionMasterGeneral
from src.BusinessLogicLayer.cluster.slavers import actions


class ActionShunt(object):
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
    def devil_king_armed(alice: dict or list):
        if isinstance(alice, dict):
            return type(
                alice.get("name") if alice.get("name") else "SpawnEntity",
                (ActionMasterGeneral,),
                alice
            )
        elif isinstance(alice, list):
            return [type(signs_information['name'], (ActionMasterGeneral,), signs_information) for signs_information in
                    type("SpawnEntropy", (object,), dict(operator=alice)).operator]

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
        action_list = actions.__entropy__.copy()
        for action_tag in action_list:
            action_entropy = action_tag.get('hyper_params')
            # if 该订阅源不具备某指定类型链接的采集权限，剔除。
            if not action_entropy.get(self.class_):
                continue
            # else 将其添加至指定类型的pending_queue
            else:
                self.atomic_seq.append(action_tag)

    def _pop_atomic(self):
        while True:
            # 当步态特征列表无剩余选项时结束迭代任务
            if self.atomic_seq.__len__() < 1:
                break
            # 取出机场步态特征的原子描述
            atomic = self.atomic_seq.pop()
            # 特征同步及权限原子化
            for passable_trace in self.work_seq:
                if passable_trace != self.class_:
                    atomic['hyper_params'][passable_trace] = False

            # 根据步态特征实例化任务
            entity_ = self.generate_entity(atomic=atomic, silence=self.silence, beat_sync=self.beat_sync)
            # 将实例化任务加入待执行队列
            self.shunt_seq.append(entity_)
