from BusinessLogicLayer.cluster.master import ActionMasterGeneral


class ActionTheSSR(ActionMasterGeneral):
    def __init__(self, register_url='https://thessr.site/auth/register', silence=True):
        super(ActionTheSSR, self).__init__(register_url=register_url, silence=silence, email='@qq.com')


if __name__ == '__main__':
    # action_speed(ActionTheSSR)
    ActionTheSSR(silence=False).run()
