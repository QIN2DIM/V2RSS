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
# - intro: SuFei
# - plan: 2D1GB 3*2GB[s]
# =============================================
ActionSuFeiCloud = {
    "name": "ActionSuFeiCloud",
    "register_url": "https://www.sufeiyun.icu/auth/register",
    "nest": "sspanel",
    "hyper_params": {"anti_slider": True, "aff": 3},
    "life_cycle": 24 * 2,
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
# - plan: 2D3GB 10*2GB[s]
# =============================================
ActionGiraffeCloud = {
    "name": "ActionGiraffeCloud",
    "register_url": "https://www.gftech.cc/auth/register",
    "nest": "sspanel",
    "hyper_params": {"anti_email": True, "aff": 5},
    "life_cycle": 24 * 2,
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
__entropy__ = [
    # ------------------------------------------
    # Public Welfare
    # ------------------------------------------
    ActionHuoXingCloud,  # sspanel
    ActionHuoJianCloud,  # sspanel
    # ------------------------------------------
    # 滑动验证
    # ------------------------------------------
    ActionSuFeiCloud,  # sspanel 2D1GB 3*2GB[s]
    ActionZFDCloud,  # sspanel 1D1GB 9999*2GB[s]
    # ------------------------------------------
    # 邮箱验证
    # ------------------------------------------
    ActionIceCloud,  # sspanel 1D1GB 9999*2GB[s]
    ActionLilyCloud,  # v2board  2D10GB 20*10GB[s]
    ActionGiraffeCloud,  # sspanel 2D3GB 10*2GB[s]
    ActionMaTrixCloud,  # sspanel 1D10GB 1000*2GB[s]
    # ------------------------------------------
    # 需要声纹验证
    # ------------------------------------------
    ActionLillianCloud,  # v2board 50D40GB D+N[s]
    ActionShyNiaCloud,  # v2board 1D10GB 10*100GB[s]
]
