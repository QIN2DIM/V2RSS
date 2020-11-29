from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionWgCloud(ActionMasterGeneral):
    def __init__(self, register_url='https://www.wiougong.space/auth/register', silence=True):
        super(ActionWgCloud, self).__init__(register_url=register_url, silence=silence, life_cycle=153,
                                            hyper_params={'v2ray': False, 'anti_slider': True})


if __name__ == '__main__':
    # action_speed(ActionWgCloud, power=1, silence=True)
    ActionWgCloud(silence=False).run()
