# -*- coding: utf-8 -*-
# Time       : 2021/12/21 23:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 女术士集会所/女巫小窝
# =============================================
# - intro: HuoJian
# - plan: Public Welfare
# =============================================
ActionHuoJianCloud = {
    "name": "ActionHuoJianCloud",
    "register_url": "https://www.666hjy.com/auth/register",
    "nest": "sspanel",
    "hyper_params": {"anti_slider": True},
}
# =============================================
# - intro: HuoXing
# - plan: Public Welfare
# =============================================
ActionHuoXingCloud = {
    "name": "ActionHuoXingCloud",
    "register_url": "https://wolaile.icu/auth/register",
    "nest": "sspanel",
    "hyper_params": {"aff": 5},
}
# =============================================
# - intro: Lily
# - plan: 2D10GB 20*10GB[s]
# =============================================
ActionLilyCloud = {
    "name": "ActionLilyCloud",
    "register_url": "https://lilyco.cc/auth/register",
    "nest": "sspanel",
    "hyper_params": {"aff": 2, "usr_email": True},
    "life_cycle": 24 * 2,
}
# =============================================
# - intro: Giraffe
# - plan: 1D1GB 10*2GB[s]
# =============================================
ActionGiraffeCloud = {
    "name": "ActionGiraffeCloud",
    "register_url": "https://www.gftech.cc/auth/register",
    "nest": "sspanel",
    "hyper_params": {"anti_slider": True, "usr_email": True, "aff": 5},
}
# =============================================
# - intro: 酸奶
# - plan: 1D10GB 10*100GB[s]
# =============================================
ActionShyNiaCloud = {
    "name": "ActionShyNiaCloud",
    "register_url": "https://shynia.com/auth/register",
    "nest": "sspanel",
    "hyper_params": {"anti_recaptcha": True, "aff": 1, "skip": True},
}
# =============================================
# - intro: MaTrix
# - plan: 1D10GB 1000*10GB[s]
# =============================================
ActionMaTrixCloud = {
    "name": "ActionMaTrixCloud",
    "register_url": "https://matrixap.com/auth/register",
    "nest": "sspanel",
    "hyper_params": {"anti_email": True},
}
# =============================================
# - intro: Lillian
# - plan: 50D40GB D+N[s]
# =============================================
ActionLillianCloud = {
    "name": "ActionLillianCloud",
    "register_url": "https://ssrr.xyz/#/register",
    "nest": "v2board",
    "hyper_params": {"anti_recaptcha": True, "prism": True, "usr_email": True},
    "life_cycle": 24 * 50,
}
# =============================================
# - intro: Ice
# - plan: 1D1GB 5*2GB[s]
# =============================================
ActionIceCloud = {
    "name": "ActionIceCloud",
    "register_url": "https://iceyun.one/auth/register",
    "nest": "sspanel",
    "hyper_params": {"anti_email": True, "aff": 5},
}
# =============================================
# - intro: 追风岛
# - plan: 1D1GB 9999*2GB[s]
# =============================================
ActionZFDCloud = {
    "name": "ActionZFDCloud",
    "register_url": "https://go.zhuifengdao.com/auth/register",
    "nest": "sspanel",
    "hyper_params": {
        "anti_slider": True,
        "usr_email": True,
        "prism": True,
        "aff": 5,
        "on_v2ray": {
            "xpath": "//div[@class='buttons']//a[contains(@class,'kitsunebi')]",
            "attr": "data-clipboard-text",
        },
    },
    "life_cycle": 24 * 2,
}
# =============================================
# - intro: 速腾
# - plan: 90D20TB
# =============================================
ActionSuTCloud = {
    "name": "ActionSuTCloud",
    "register_url": "https://speedcncn.com/index.php#/register",
    "nest": "v2board",
    "hyper_params": {"anti_recaptcha": True, "usr_email": True},
    "life_cycle": 24 * 90,
}
# =============================================
# - intro: 叉烧
# - plan: 5D5GB
# =============================================
ActionBarbecueCloud = {
    "name": "ActionBarbecueCloud",
    "register_url": "https://chashao.shop#/register",
    "nest": "v2board",
    "hyper_params": {"anti_email": True},
}
# =============================================
# - intro: 泡泡
# - plan: 1D1GB 10*3GB[s]
# =============================================
ActionPaoPaoCloud = {
    "name": "ActionPaoPaoCloud",
    "register_url": "https://ssru6.pw/auth/register",
    "nest": "material",
    "hyper_params": {"usr_email": True, "aff": 5},
}
# =============================================
# - intro: 翻云
# - plan: 1D1GB 100*2GB[s]
# =============================================
ActionFunCloud = {
    "name": "ActionFunCloud",
    "register_url": "https://yaoodi99.com/auth/register",
    "nest": "material",
    "hyper_params": {"usr_email": True, "contact": True, "aff": 5},
}
# =============================================
# - intro: 紫云
# - plan: 1D10GB 10*2GB[s]
# =============================================
ActionPurpleCloud = {
    "name": "ActionPurpleCloud",
    "register_url": "https://ziyun.cyou/auth/register",
    "nest": "material",
    "hyper_params": {"usr_email": True, "contact": True, "aff": 5},
    "life_cycle": 24 * 3,
}
# =============================================
# - intro: 地平线
# - plan: 1D5GB 1000*15GB[s]
# =============================================
ActionHorizonCloud = {
    "name": "ActionHorizonCloud",
    "register_url": "https://1929.work/auth/register",
    "nest": "metron",
    "hyper_params": {
        "tos": True,
        "usr_email": True,
        "anti_email": True,
        "anti_slider": True,
        "aff": 2,
    },
}
# =============================================
# - intro: 土拨鼠
# - plan: 3D9GB 999999*2GB[s]
# =============================================
ActionGroundhogCloud = {
    "name": "ActionGroundhogCloud",
    "register_url": "https://tuboshu.live/auth/register",
    "nest": "metron",
    "hyper_params": {"tos": True, "anti_email": True, "usr_email": True, "aff": 3},
}

__entropy__ = [
    # ------------------------------------------
    # Public Welfare
    # ------------------------------------------
    # ActionHuoXingCloud,  # sspanel
    # ActionHuoJianCloud,  # sspanel
    # ------------------------------------------
    # 标准实例
    # ------------------------------------------
    ActionPurpleCloud,  # material 1D10GB 10*2GB[s]
    ActionFunCloud,  # material  1D1GB 100*2GB[s]
    ActionPaoPaoCloud,  # material 1D1GB 10*3GB[s]
    # ------------------------------------------
    # 滑动验证
    # ------------------------------------------
    # ActionGiraffeCloud,  # sspanel 2D3GB 10*2GB[s]
    ActionZFDCloud,  # sspanel 1D1GB 9999*2GB[s]
    ActionHorizonCloud,  # metron 1D5GB 1000*15GB[s]
    # ------------------------------------------
    # 邮箱验证
    # ------------------------------------------
    ActionGroundhogCloud,  # metron 3D9G 99999*2GB[s]
    ActionIceCloud,  # sspanel 1D1GB 9999*2GB[s]
    ActionLilyCloud,  # sspanel  2D10GB 20*10GB[s]
    ActionMaTrixCloud,  # sspanel 1D10GB 1000*2GB[s]
    ActionBarbecueCloud,  # v2board 1D5GB
    # ------------------------------------------
    # 声纹验证
    # ------------------------------------------
    ActionSuTCloud,  # v2board 90D20TB
    ActionLillianCloud,  # v2board 50D40GB D+N[s]
    ActionShyNiaCloud,  # sspanel 1D10GB 10*100GB[s]
    # ------------------------------------------
    # 超级泛型实例
    # ------------------------------------------
    # https://rinki.xyz/auth/register
    # https://qbklj.xyz/auth/register
    # https://www.flybar.cc/auth/register
]
