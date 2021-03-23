ActionOhrCloud = {
    'name': "ActionOhrCloud",
    'register_url': "https://www.ssr99.xyz/auth/register",
    'life_cycle': 2,
    'anti_slider': False,
    'hyper_params': {'ssr': True, "v2ray": True},
    'email': '@gmail.com'
}

ActionKakCloud = {
    'name': "ActionKakCloud",
    'register_url': "https://www.kakayun.cyou/auth/register",
    'life_cycle': 1,
    'anti_slider': True,
    'hyper_params': {'ssr': False, "v2ray": True},
    'email': '@gmail.com'
}

ActionJfCloud = {
    'name': "ActionJfCloud",
    'register_url': "https://www.jafiyun.cc/auth/register",
    'life_cycle': 1,
    'anti_slider': False,
    'hyper_params': {'ssr': False, "v2ray": True},
    'email': '@gmail.com'
}

ActionN95Cloud = {
    'name': "ActionN95Cloud",
    'register_url': "https://n95cloud.vip/auth/register",
    'life_cycle': 1,
    'anti_slider': False,
    'hyper_params': {'ssr': True, "v2ray": True},
    'email': '@gmail.com'
}

ActionTheSSR = {
    'name': "ActionTheSSR",
    'register_url': "https://ssrthe.shop/auth/register",
    'life_cycle': 1,
    'anti_slider': False,
    'hyper_params': {'ssr': True, "v2ray": True},
    'email': '@qq.com'
}

ActionUfoCloud = {
    'name': "ActionUfoCloud",
    'register_url': "https://ufocloud.xyz/auth/register",
    'life_cycle': 1,
    'anti_slider': False,
    'hyper_params': {'ssr': False, "v2ray": True},
    'email': '@qq.com'
}

ActionWgCloud = {
    'name': "ActionWgCloud",
    'register_url': "https://www.wiougong.space/auth/register",
    'life_cycle': 1,
    'anti_slider': True,
    'hyper_params': {'ssr': True, "v2ray": True},
    'email': '@gmail.com'
}

ActionZuiSuCloud = {
    'name': "ActionZuiSuCloud",
    'register_url': "https://zuisucloud.cloud/auth/register",
    'life_cycle': 1,
    'anti_slider': True,
    'hyper_params': {'ssr': True, "v2ray": True},
    'email': '@gmail.com'
}

ActionJdSuCloud = {
    'name': "ActionJdSuCloud",
    'register_url': "https://jdycloud.xyz/auth/register",
    'life_cycle': 1,
    'anti_slider': True,
    'hyper_params': {'ssr': True, "v2ray": False, 'usr_email': True},
    'email': '@gmail.com'
}

ActionHuoJianCloud = {
    'name': "ActionHuoJianCloud",
    'register_url': "https://huojian987.com/auth/register",
    'life_cycle': 1,
    'anti_slider': True,
    'hyper_params': {'ssr': True, "v2ray": False},
    'email': '@qq.com'
}

ActionUUCloud = {
    'name': "ActionUUCloud",
    'register_url': "https://www.uuyun.club/auth/register",
    'life_cycle': 1,
    'anti_slider': False,
    'hyper_params': {'ssr': False, "v2ray": True},
    'email': '@gmail.com'
}

ActionSuFeiCloud = {
    'name': "ActionSuFeiCloud",
    'register_url': "https://www.dagewokuaitule.icu/auth/register",
    'life_cycle': 2,
    'anti_slider': True,
    'hyper_params': {'ssr': True, "v2ray": True},
    'email': '@gmail.com'
}

ActionMiTaoCloud = {
    'name': "ActionMiTaoCloud",
    'register_url': "https://mitaocloud.net/auth/register",
    'life_cycle': 1,
    'anti_slider': False,
    'hyper_params': {'ssr': False, "v2ray": True},
    'email': '@gmail.com'
}

ActionReCloud = {
    'name': "ActionReCloud",
    'register_url': "https://www.rerere.xyz/auth/register",
    'life_cycle': 1,
    'anti_slider': True,
    'hyper_params': {'ssr': True, "v2ray": True},
    'email': '@gmail.com'
}

ActionMxCloud = {
    'name': "ActionMxCloud",
    'register_url': "https://www.mxyssr.fun/auth/register",
    'life_cycle': 1,
    'anti_slider': True,
    'hyper_params': {'ssr': True, "v2ray": False},
    'email': '@gmail.com'
}

__entropy__ = [
    # ---------------------
    # 无障碍
    # ---------------------
    # ActionMiTaoCloud,  # 1day 10G

    # ---------------------
    # 需要滑动验证
    # ---------------------
    ActionReCloud,  # 1day 10G

    ActionKakCloud,  # 1day 10G

    ActionSuFeiCloud,  # 2day 5G

    # ---------------------
    # 公益节点
    # ---------------------
    # 'ActionHuoJianCloud',  # public welfare

    # ---------------------
    # 需要邮箱验证
    # ---------------------
    # "ActionUUCloud",

    # ---------------------
    # 优惠政策有待调整
    # ---------------------
    # 'ActionWgCloud',
    # 'ActionJdSuCloud',
    # 'ActionOhrCloud',  # error Null and No new users are accepted
    # 'ActionJfCloud',  # 1day 1G

    ActionMxCloud,  # 1day 2G

    # ---------------------
    # DDoS防御 or 系统宕机
    # ---------------------
    # 'ActionZuiSuCloud', # error 521 web server is down

    # ---------------------
    # fixme:滑动验证元素方案不通用
    # ---------------------

    # ---------------------
    # 跑路/域名弃用
    # ---------------------
    # 'ActionTheSSR',
    # 'ActionUfoCloud',
    # 'ActionN95Cloud',

]

if __name__ == '__main__':
    # 单步调试，启动指定机场的采集任务
    from src.BusinessLogicLayer.apis.ghost_filler import gevent_ghost_filler

    gevent_ghost_filler(docker=ActionKakCloud, silence=True)
