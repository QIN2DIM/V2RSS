from BusinessLogicLayer.cluster.master import ActionMasterGeneral

__all__ = [
    # ---------------------
    # 无障碍
    # ---------------------
    # 'ActionUfoCloud',
    # 'ActionN95Cloud',
    'ActionJfCloud',
    'ActionIcuCloud',

    # ---------------------
    # 需要滑动验证
    # ---------------------
    'ActionReCloud',
    # 'ActionJdSuCloud',
    # 'ActionWgCloud',
    'ActionHuoJianCloud',
    'ActionMxCloud',
    "ActionKaiKaiCloud",
    "ActionUUCloud",

    # ---------------------
    # DDOS防御
    # ---------------------

    # ---------------------
    # fixme:滑动验证元素方案不通用
    # ---------------------
    # 'ActionZuiSuCloud',
    # 'ActionOhrCloud',

    # ---------------------
    # 跑路/域名弃用
    # ---------------------
    # 'ActionTheSSR',

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
                                            silence=silence, anti_slider=False, at_once=at_once,
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
                                            silence=silence, life_cycle=1, anti_slider=True, at_once=at_once, )


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
                                            silence=silence, life_cycle=1, anti_slider=True, at_once=at_once)


class ActionZuiSuCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionZuiSuCloud, self).__init__(register_url='https://zuisucloud.cloud/auth/register',
                                               silence=silence, anti_slider=True, at_once=at_once, )


class ActionJdSuCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionJdSuCloud, self).__init__(register_url='https://jdycloud.xyz/auth/register',
                                              silence=silence, life_cycle=30, anti_slider=True, at_once=at_once,
                                              hyper_params={'usr_email': True, 'v2ray': False})


class ActionHuoJianCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionHuoJianCloud, self).__init__(register_url='https://huojian987.com/auth/register',
                                                 silence=silence, email='@qq.com', life_cycle=30, anti_slider=True,
                                                 at_once=at_once,
                                                 hyper_params={'v2ray': False})


class ActionKaiKaiCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionKaiKaiCloud, self).__init__(register_url='https://www.kakayun.cyou/auth/register',
                                                silence=silence, life_cycle=1, anti_slider=True, at_once=at_once,
                                                hyper_params={'ssr': False})


class ActionUUCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionUUCloud, self).__init__(register_url='https://www.uuyun.club/auth/register',
                                            silence=silence, life_cycle=1, anti_slider=False, at_once=at_once,
                                            hyper_params={'ssr': False})


class ActionIcuCloud(ActionMasterGeneral):
    def __init__(self, silence=True, at_once=True):
        super(ActionIcuCloud, self).__init__(register_url='https://www.dagewokuaitule.icu/auth/register',
                                             silence=silence, life_cycle=30, anti_slider=False, at_once=at_once)


if __name__ == '__main__':
    from BusinessCentralLayer.coroutine_engine import lsu


    class GhostFiller(lsu):
        def __init__(self, docker, silence: bool = False, power: int = 1):
            """

            @param docker: 需要测试或快速填充的机场实例
            @param silence: 是否静默启动
            @param power: 发起次数,采用协程策略，既一次性并发count个任务
            @return:
            """
            super(GhostFiller, self).__init__()

            # 参数初始化
            self.power = power
            self.docker = docker
            self.silence = silence
            self.docker_behavior = "self.docker(self.silence).run()"

            # 为并发任务打入协程加速补丁
            if power > 1:
                exec("from gevent import monkey\nmonkey.patch_all(ssl=False)")

            # 自启任务
            self.interface()

        def offload_task(self):
            for _ in range(self.power):
                self.work_q.put_nowait(self.docker_behavior)

        def control_driver(self, docker_behavior: str):
            exec(docker_behavior)


    GhostFiller(docker=ActionIcuCloud, silence=True, power=2)
