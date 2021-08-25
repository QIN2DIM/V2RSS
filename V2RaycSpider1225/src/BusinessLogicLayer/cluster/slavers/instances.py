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
