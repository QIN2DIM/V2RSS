# -*- coding: utf-8 -*-
# Time       : 2021/12/31 23:21
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from typing import Dict

from services.middleware.subscribe_io import SubscribeManager
from services.utils import ToolBox


def apis_admin_get_subs(command_: str) -> Dict[str, str]:
    """

    :param command_:
    :return:
    """
    if not (command_ and isinstance(command_, str)) or command_ not in ["v2ray", "clash", "ssr"]:
        return {"msg": "failed", "info": "参数类型错误"}

    sm = SubscribeManager()
    urls = sm.sync()

    if not urls:
        return {"msg": "failed", "info": "无可用订阅"}

    subscribe = urls.pop()
    try:
        sm.detach(subscribe=subscribe, transfer=True, motive="ADMIN - GetSubs")
        sm.update_api_status(api_name="get")
    finally:
        return {"msg": "success", "subscribe": subscribe}


def apis_admin_get_subs_v2(entropy_name: str = None, detach=True) -> dict:
    """

    :param entropy_name: 缩写
    :param detach: 被选中的链接不会被移除，在测试接口时使用
    :return:
    """
    # 连接缓存
    sm = SubscribeManager()

    # 根据别名匹配链接
    if entropy_name.startswith("Action") and entropy_name.endswith("Cloud"):
        alias2urls = {sm.get_alias(ToolBox.reset_url(url, get_domain=True)): url for url in sm.sync()}
        pending_urls = [alias2urls[alias] for alias in alias2urls.keys() if entropy_name == alias]
    # 根据订阅域名匹配链接
    else:
        domain2urls = {ToolBox.reset_url(url, get_domain=True): url for url in sm.sync()}
        pending_urls = [domain2urls[domain] for domain in domain2urls.keys() if entropy_name in domain]

    # 无匹配项
    if not pending_urls:
        return {"msg": "failed", "input": entropy_name, "info": "需要获取的netloc订阅不存在"}

    # 提取第一条有效链接作为返回值
    subscribe = pending_urls[0]
    try:
        # 移除订阅并更新API用量
        if detach is True:
            sm.detach(subscribe=subscribe, transfer=True, motive="ADMIN - MatchSubs")
            sm.update_api_status(api_name="get")
    finally:
        return {"msg": "success", "subscribe": subscribe}


def apis_admin_get_pool_status():
    pool_status = SubscribeManager().get_pool_status()
    return {"msg": "success", "status": pool_status}
