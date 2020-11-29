from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionJfCloud(ActionMasterGeneral):
    def __init__(self, register_url='https://www.jafiyun.cc/auth/register', silence=True):
        super(ActionJfCloud, self).__init__(register_url=register_url, silence=silence,
                                            hyper_params={'anti_slider': True, 'ssr': False})


if __name__ == '__main__':
    ActionJfCloud(silence=False).run()
