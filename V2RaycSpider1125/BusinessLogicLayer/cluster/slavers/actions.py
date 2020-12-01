from BusinessLogicLayer.cluster.master import ActionMasterGeneral

__all__ = [
    # 'ActionMxCloud',# protection of DDos
    # 'ActionWgCloud',# 关闭注册
    # 'ActionJfCloud',
    'ActionN95Cloud',
    'ActionTheSSR',
    'ActionReCloud',
    'ActionUfoCloud',
    'ActionZuiSuCloud',
    'ActionOhrCloud',
]


class ActionOhrCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionOhrCloud, self).__init__(register_url='https://ohssr.red/auth/register',
                                             silence=silence, life_cycle=2, anti_slider=False)


class ActionKakCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionKakCloud, self).__init__(register_url='https://www.kakayun.cyou/auth/register',
                                             silence=silence, life_cycle=2, anti_slider=True,
                                             hyper_params={'ssr': False})


class ActionJfCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionJfCloud, self).__init__(register_url='https://www.jafiyun.cc/auth/register',
                                            silence=silence, life_cycle=1, anti_slider=True,
                                            hyper_params={'ssr': False})


class ActionMxCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionMxCloud, self).__init__(register_url='https://www.mxyssr.me/auth/register',
                                            silence=silence, life_cycle=2, anti_slider=True)


class ActionN95Cloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionN95Cloud, self).__init__(register_url='https://n95cloud.vip/auth/register',
                                             silence=silence, life_cycle=1, anti_slider=False)


class ActionReCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionReCloud, self).__init__(register_url="https://www.rerere.xyz/auth/register",
                                            silence=silence, life_cycle=4, anti_slider=True)


class ActionTheSSR(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionTheSSR, self).__init__(register_url='https://thessr.site/auth/register',
                                           silence=silence, email='@qq.com', life_cycle=1, anti_slider=False)


class ActionUfoCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionUfoCloud, self).__init__(register_url='https://ufocloud.xyz/auth/register',
                                             silence=silence, email='@qq.com', life_cycle=1, anti_slider=False,
                                             hyper_params={'ssr': False})


class ActionWgCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionWgCloud, self).__init__(register_url='https://www.wiougong.space/auth/register',
                                            silence=silence, life_cycle=153, anti_slider=True,
                                            hyper_params={'v2ray': False})


class ActionZuiSuCloud(ActionMasterGeneral):
    def __init__(self, silence=True):
        super(ActionZuiSuCloud, self).__init__(register_url='https://zuisucloud.cloud/auth/register',
                                               silence=silence, life_cycle=1, anti_slider=False)


if __name__ == '__main__':
    ActionJfCloud(silence=False).run()
