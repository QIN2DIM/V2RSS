from BusinessLogicLayer.cluster.master import *


class ActionXjCloud(ActionMasterGeneral):
    def __init__(self, register_url='https://www.xjycloud.xyz/auth/register', silence=True):
        super(ActionXjCloud, self).__init__(register_url=register_url, silence=silence, email='@qq.com', life_cycle=62,
                                            hyper_params={'anti_slider': True})
