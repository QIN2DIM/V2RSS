from ..prism import Prism


class ActionAaxCloud(Prism):
    atomic = {
        'name': "ActionAaxCloud",
        'register_url': "https://aaxc.club/auth/register",
        'anti_slider': False,
        'hyper_params': {'ssr': False, 'v2ray': True, 'usr_email': False}
    }

    def __init__(self, silence=True, assault=True):
        super(ActionAaxCloud, self).__init__(atomic=ActionAaxCloud.atomic, silence=silence, assault=assault)


class Action500mlCloud(Prism):
    atomic = {
        'name': "Action500mlCloud",
        'register_url': "https://500ml.buzz/auth/register",
        'anti_slider': False,
        'hyper_params': {'ssr': False, 'v2ray': True, 'usr_email': False}
    }

    def __init__(self, silence=True, assault=True):
        super(Action500mlCloud, self).__init__(Action500mlCloud.atomic, silence=silence, assault=assault)
