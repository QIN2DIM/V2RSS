# -*- coding: utf-8 -*-
# Time       : 2021/12/31 23:21
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
from typing import Dict

from services.middleware.subscribe_io import SubscribeManager
from services.utils import ToolBox

sm = SubscribeManager()


def _auto_detach():
    """
    在 Scaffold 启动时手动指定环境变量控制链接分离，此处默认不分离。
    当从路由层调用API时，若调用时就指定了 "detach" 则此环境变量无效
    :return:
    """
    return bool(os.getenv("DETACH_SUBSCRIPTIONS", False))


def apis_admin_get_subs(detach: bool = None) -> Dict[str, str]:
    """

    :param detach:
    :return:
    """
    detach = _auto_detach() if detach is None else detach

    # 连接订阅池
    urls = sm.sync()

    if not urls:
        return {"msg": "failed", "info": "无可用订阅"}

    subscribe = urls.pop()
    try:
        # 移除订阅并更新API用量
        if detach:
            sm.detach(subscribe=subscribe, transfer=True, motive="ADMIN - GetSubs")
            sm.update_api_status(api_name="get")
    finally:
        return {"msg": "success", "subscribe": subscribe}


def apis_admin_get_subs_v2(alias: str = None, detach: bool = None) -> dict:
    """

    :param alias: 缩写
    :param detach: 被选中的链接不会被移除，在测试接口时使用
    :return:
    """
    detach = _auto_detach() if detach is None else detach

    # 连接订阅池
    urls = sm.sync()

    if not urls:
        return {"msg": "failed", "info": "无可用订阅"}

    # 优先匹配 action-alias
    if alias.startswith("Action") and alias.endswith("Cloud"):
        alias2urls = {
            sm.get_alias(ToolBox.reset_url(url, get_domain=True)): url for url in urls
        }
        pending_urls = [alias2urls[alias]]
    # 匹配 action-domain
    else:
        domain2urls = {ToolBox.reset_url(url, get_domain=True): url for url in urls}
        pending_urls = [
            domain2urls[domain] for domain in domain2urls.keys() if alias in domain
        ]

    # 无匹配项
    if not pending_urls:
        return {"msg": "failed", "input": alias, "info": "需要获取的netloc订阅不存在"}

    # 提取第一条有效链接作为返回值
    subscribe = pending_urls[0]
    try:
        # 移除订阅并更新API用量
        if detach is True:
            sm.detach(subscribe=subscribe, transfer=True, motive="ADMIN - MatchSubs")
            sm.update_api_status(api_name="get")
    finally:
        return {"msg": "success", "subscribe": subscribe}


def apis_admin_get_pool_status() -> dict:
    pool_status = sm.get_pool_status()
    return {"msg": "success", "status": pool_status}
