from BusinessLogicLayer.cluster.master import ActionMasterGeneral

__all__ = [
    'ActionMxCloud',  # protection of DDos
    # 'ActionZuiSuCloud', #元素不同
    # 'ActionUfoCloud',# 可能跑路

    'ActionWgCloud',
    # 'ActionJfCloud',
    'ActionN95Cloud',
    'ActionTheSSR',
    'ActionReCloud',
    'ActionOhrCloud',
]


class ActionOhrCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionOhrCloud, self).__init__(register_url='https://ohssr.red/auth/register',
                                             silence=silence, life_cycle=2, anti_slider=False, at_once=at_once)


class ActionKakCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionKakCloud, self).__init__(register_url='https://www.kakayun.cyou/auth/register',
                                             silence=silence, life_cycle=2, anti_slider=True, at_once=at_once,
                                             hyper_params={'ssr': False})


class ActionJfCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionJfCloud, self).__init__(register_url='https://www.jafiyun.cc/auth/register',
                                            silence=silence, anti_slider=True, at_once=at_once,
                                            hyper_params={'ssr': False})


class ActionMxCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionMxCloud, self).__init__(register_url='https://www.mxyssr.me/auth/register',
                                            silence=silence, life_cycle=2, anti_slider=True, at_once=at_once)


class ActionN95Cloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionN95Cloud, self).__init__(register_url='https://n95cloud.vip/auth/register',
                                             silence=silence, anti_slider=False, at_once=at_once, )


class ActionReCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionReCloud, self).__init__(register_url="https://www.rerere.xyz/auth/register",
                                            silence=silence, life_cycle=4, anti_slider=True, at_once=at_once, )


class ActionTheSSR(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionTheSSR, self).__init__(register_url='https://ssrthe.shop/auth/register',
                                           silence=silence, email='@qq.com', anti_slider=False, at_once=at_once, )


class ActionUfoCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionUfoCloud, self).__init__(register_url='https://ufocloud.xyz/auth/register',
                                             silence=silence, email='@qq.com', anti_slider=False, at_once=at_once,
                                             hyper_params={'ssr': False})


class ActionWgCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionWgCloud, self).__init__(register_url='https://www.wiougong.space/auth/register',
                                            silence=silence, life_cycle=30, anti_slider=True, at_once=at_once)


class ActionZuiSuCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionZuiSuCloud, self).__init__(register_url='https://zuisucloud.cloud/auth/register',
                                               silence=silence, anti_slider=True, at_once=at_once, )


if __name__ == '__main__':
    ActionOhrCloud(silence=False).run()
