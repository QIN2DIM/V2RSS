# -*- coding: utf-8 -*-
# Time       : 2022/1/9 15:44
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

from sanic import Request


def how_dare_you(request: Request):
    _token = request.headers.get("token")
    if not _token:
        return {"msg": "[🔨] how date you!?"}


def register_token(request: Request):
    pass
