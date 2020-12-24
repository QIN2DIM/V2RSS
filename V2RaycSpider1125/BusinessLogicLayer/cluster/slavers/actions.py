from BusinessLogicLayer.cluster.master import ActionMasterGeneral

__all__ = [
    # ---------------------
    # 无障碍
    # ---------------------
    'ActionUfoCloud',
    'ActionN95Cloud',
    # 'ActionTheSSR',
    'ActionOhrCloud',

    # ---------------------
    # 需要滑动验证
    # ---------------------
    'ActionReCloud',
    'ActionJdSuCloud',
    'ActionWgCloud',
    'ActionHuoJianCloud',
    'ActionMxCloud',
    "ActionKaiKaiCloud",

    # ---------------------
    # DDOS防御
    # ---------------------
    # 'ActionJfCloud',
    # ---------------------
    # 弃用：元素不同
    # ---------------------
    # 'ActionZuiSuCloud',

]


class ActionOhrCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionOhrCloud, self).__init__(register_url='https://www.ssr99.xyz/auth/register',
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
        super(ActionMxCloud, self).__init__(register_url='https://www.mxyssr.fun/auth/register',
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


class ActionJdSuCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionJdSuCloud, self).__init__(register_url='https://jdycloud.xyz/auth/register',
                                              silence=silence, life_cycle=30, anti_slider=True, at_once=at_once,
                                              hyper_params={'usr_email': True})


class ActionHuoJianCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionHuoJianCloud, self).__init__(register_url='https://huojian987.com/auth/register',
                                                 silence=silence, life_cycle=30, anti_slider=True, at_once=at_once,
                                                 hyper_params={'v2ray': False})


class ActionKaiKaiCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionKaiKaiCloud, self).__init__(register_url='https://www.kaikaiyun.cyou/auth/register',
                                                silence=silence, life_cycle=2, anti_slider=True, at_once=at_once,
                                                hyper_params={'ssr': False})


if __name__ == '__main__':
    ActionMxCloud(silence=False).run()
