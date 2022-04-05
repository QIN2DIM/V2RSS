# -*- coding: utf-8 -*-
# Time       : 2021/12/31 23:21
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
__all__ = ["app"]

from sanic import Sanic
from sanic.request import Request
from sanic.response import redirect, json, HTTPResponse

from services.app.server.apis import (
    apis_admin_get_subs,
    apis_admin_get_subs_v2,
    apis_admin_get_pool_status,
)
from services.settings import ROUTER_API, ROUTER_NAME

app = Sanic(ROUTER_NAME)


@app.get("/")
def goto_repo_page(request: Request) -> HTTPResponse:
    """
    重定向到项目首页

    :param request:
    :return:
    """
    return redirect("https://github.com/QIN2DIM/V2RayCloudSpider", status=200)


@app.post(ROUTER_API["get_subs_v1"])
def get_subs_v1(request: Request) -> HTTPResponse:
    """
    获取某一类型订阅

    :param request:
    :return:
    """
    data = request.json

    # type_ 订阅类型，开源版本仅支持获取 ``v2ray``
    type_ = data.get("type", "") if data else ""
    if not (type_ and isinstance(type_, str)) or type_ not in ["v2ray", "clash", "ssr"]:
        return json({"msg": "failed", "info": "参数类型错误"})

    return json(apis_admin_get_subs(detach=not app.debug))


@app.post(ROUTER_API["get_subs_v2"])
def get_subs_v2(request: Request) -> HTTPResponse:
    """根据域名模糊匹配手动指定并获取订阅，在 Debug 部署模式下请求的订阅不会被删除。

    如：要获取订阅 https://www.modu.me/link?token=123，
    传入 modu 或 mod 或订阅实例所对应的 action-alias 既可匹配

    alive action-alias 通过 pool_status() 获知，
    alias 格式为 Action[Something]Cloud，如 ActionModuCloud

    :param request:
    :return:
    """
    data = request.json

    # alias 订阅对象的 <domain/remark> 或 <action-alias>
    alias = data.get("alias", "") if data else ""
    if not (alias and isinstance(alias, str)):
        return json({"msg": "failed", "info": "参数类型错误"})

    return json(apis_admin_get_subs_v2(alias=alias))


@app.get(ROUTER_API["get_v2ray"])
def pool_get_v2ray(request: Request):
    """
    调用 v1 接口快速获取 v2ray 订阅

    开源接口仅允许快速获取 v2ray 订阅

    :return:
    """
    return json(apis_admin_get_subs())


@app.route(ROUTER_API["get_pool_status"], methods=["GET", "POST"])
def pool_status(request: Request) -> HTTPResponse:
    """
    查看订阅池活跃状态

    :return: {ActionAlias_1:linkNum, ActionAlias_2:linkNum, ...}
    """

    return json(apis_admin_get_pool_status())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6501, auto_reload=True, access_log=False, workers=1)
