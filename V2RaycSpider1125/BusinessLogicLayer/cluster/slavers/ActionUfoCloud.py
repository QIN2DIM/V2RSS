from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionUfoCloud(ActionMasterGeneral):
    def __init__(self, register_url='https://ufocloud.xyz/auth/register', silence=True):
        super(ActionUfoCloud, self).__init__(register_url=register_url, silence=silence, email='@qq.com',
                                             hyper_params={'ssr': False})


if __name__ == '__main__':
    # action_speed(ActionUfoCloud)
    ActionUfoCloud(silence=False).run()
