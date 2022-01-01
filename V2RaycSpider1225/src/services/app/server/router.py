# -*- coding: utf-8 -*-
# Time       : 2021/12/31 23:21
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
__all__ = ["app"]

import multiprocessing

from sanic import Sanic
from sanic.request import Request
from sanic.response import redirect, json, HTTPResponse

from services.app.server.apis import (
    apis_admin_get_subs,
    apis_admin_get_subs_v2,
    apis_admin_get_pool_status
)
from services.settings import ROUTER_API, ROUTER_NAME

app = Sanic(ROUTER_NAME)


@app.get("/")
async def redirect_to_my_blog(request: Request) -> HTTPResponse:
    """
    重定向到项目首页

    :param request:
    :return:
    """
    return redirect("https://github.com/QIN2DIM/V2RayCloudSpider")


@app.get(ROUTER_API["get_subs"])
async def admin_get_subs(request: Request, command_) -> HTTPResponse:
    """
    获取某一类型订阅

    :param request:
    :param command_: 订阅类型 例如 v2ray
    :return:
    """
    return json(apis_admin_get_subs(command_))


@app.get(ROUTER_API["get_v2ray"])
async def admin_get_v2ray(request: Request):
    """
    快速获取v2ray订阅

    :return:
    """
    return admin_get_subs(command_="v2ray")


@app.get(ROUTER_API["get_subs_v2"])
async def admin_get_subs_v2(request: Request, _entropy_name) -> HTTPResponse:
    """
    根据域名模糊匹配手动指定并获取订阅

    如：订阅 https://www.moudu.me/link?token=123，传入 moudu 或 mou 或订阅实例所对应的 alias 既可匹配

    :param request:
    :param _entropy_name: 域名简写
    :return:
    """
    return json(apis_admin_get_subs_v2(entropy_name=_entropy_name))


@app.get(ROUTER_API["get_subs_v2_debug"])
async def admin_get_subs_v2_debug(request: Request, _entropy_name) -> HTTPResponse:
    """
    根据域名模糊匹配手动指定并获取订阅（debug接口，被请求的订阅不会被移除）

    如：订阅 https://www.moudu.me/link?token=123，传入 moudu 或 mou 或订阅实例所对应的 alias 既可匹配

    :param request:
    :param _entropy_name: 订阅的域名简写或别名，
    活跃的订阅别名通过 admin_get_pool_status() 获知，格式为 Action[Something]Cloud，如 ActionZZCloud
    :return:
    """
    return json(apis_admin_get_subs_v2(entropy_name=_entropy_name, detach=False))


@app.get(ROUTER_API["get_pool_status"])
async def admin_get_pool_status(request: Request) -> HTTPResponse:
    """
    查看订阅池活跃状态

    :return: {ActionAlias_1:linkNum, ActionAlias_2:linkNum, ...}
    """
    return json(apis_admin_get_pool_status())


if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=6501,
        debug=False,
        access_log=False,
        workers=multiprocessing.cpu_count(),
    )
