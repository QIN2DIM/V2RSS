from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionN95Cloud(ActionMasterGeneral):
    def __init__(self, register_url='https://n95cloud.vip/auth/register', silence=True):
        super(ActionN95Cloud, self).__init__(register_url=register_url, silence=silence)


if __name__ == '__main__':
    # action_speed(ActionN95Cloud, power=1, silence=True)
    ActionN95Cloud(silence=False).run()
