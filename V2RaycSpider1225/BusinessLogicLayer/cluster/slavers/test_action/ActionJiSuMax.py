from BusinessLogicLayer.cluster.master import *


class ActionJiSuMax(ActionMasterGeneral):
    def __init__(self, register_url='https://jisumax.com/#/register?', silence=True):
        super(ActionJiSuMax, self).__init__(register_url=register_url, silence=silence, email='@qq.com', life_cycle=61,
                                            hyper_params={'anti_slider': True, 'trojan': True})
