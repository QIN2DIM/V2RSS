from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionReCloud(ActionMasterGeneral):
    def __init__(self, register_url='https://www.rerere.xyz/auth/register', silence=True):
        super(ActionReCloud, self).__init__(register_url=register_url, silence=silence, life_cycle=4,
                                            hyper_params={'anti_slider': True})


if __name__ == '__main__':
    # action_speed(ActionReCloud, power=1, silence=True)
    ActionReCloud(silence=False).run()
