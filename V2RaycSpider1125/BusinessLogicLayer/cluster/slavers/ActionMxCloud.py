from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionMxCloud(ActionMasterGeneral):
    def __init__(self, register_url='https://www.mxyssr.me/auth/register', silence=True):
        super(ActionMxCloud, self).__init__(register_url=register_url, silence=silence, life_cycle=2,
                                            hyper_params={'anti_slider': True})


if __name__ == '__main__':
    # action_speed(ActionMxCloud, power=1, silence=True)
    ActionMxCloud(silence=False).run()
