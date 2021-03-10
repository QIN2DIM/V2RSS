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
        self.class_ = class_
        self.work_seq = CRAWLER_SEQUENCE
        self.silence, self.beat_sync = silence, beat_sync

        # output
        self.shunt_seq = []
        self.atomic_seq = []

    def _shunt_action(self):
        action_list = actions.__entropy__.copy()
        for action_tag in action_list:
            action_entropy = action_tag.get('hyper_params')
            # if 该机场不具备该类型链接的采集权限，剔除。
            if not action_entropy.get(self.class_):
                continue
            else:
                self.atomic_seq.append(action_tag)

    def _pop_atomic(self):

        while True:
            if self.atomic_seq.__len__() < 1:
                break
            action_atomic = self.atomic_seq.pop()
            for passable_trace in self.work_seq:
                if passable_trace != self.class_:
                    action_atomic['hyper_params'][passable_trace] = False

            amg = ActionMasterGeneral(
                silence=self.silence,
                beat_sync=self.beat_sync,
                action_name=action_atomic['name'],
                register_url=action_atomic['register_url'],
                anti_slider=action_atomic['anti_slider'],
                life_cycle=action_atomic['life_cycle'],
                email=action_atomic['email'],
                hyper_params=action_atomic['hyper_params'],
            ).run
            self.shunt_seq.append(amg)

    def shunt(self):
        self._shunt_action()
        self._pop_atomic()
        return self.shunt_seq
