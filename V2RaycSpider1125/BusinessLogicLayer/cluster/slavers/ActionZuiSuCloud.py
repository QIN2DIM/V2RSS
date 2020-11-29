from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionZuiSuCloud(ActionMasterGeneral):
    def __init__(self, register_url='https://zuisucloud.cloud/auth/register', silence=True):
        super(ActionZuiSuCloud, self).__init__(register_url, silence)


if __name__ == '__main__':
    # action_speed(ActionZuiSuCloud, power=1, silence=True)
    ActionZuiSuCloud(silence=False).run()
