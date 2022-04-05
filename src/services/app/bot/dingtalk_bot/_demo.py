# -*- coding: utf-8 -*-
# Time       : 2021/8/31 1:19
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:DingTalk bot | V2RCS：分发云彩姬订阅的钉钉机器人
import base64
import hashlib
import hmac
import json
import time
import urllib.parse

import requests


def ding_to_group(
    subscribe: str = "这里是V2Ray云彩姬",
    access_token: str = None,
    timestamp: str = None,
    sign_: str = None,
):
    """
    通过POST接口，传递必要参数，控制指定的机器人向指定的群组发送TEXT类型消息
    :param subscribe: 要发送的订阅
    :param access_token:
    :param timestamp:
    :param sign_:
    :return:
    """
    web_hook = "https://oapi.dingtalk.com/robot/send?"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": access_token, "timestamp": timestamp, "sign": sign_}
    data = {"msgtype": "text", "text": {"content": subscribe}}
    session = requests.session()

    response = session.post(
        web_hook, headers=headers, params=params, data=json.dumps(data)
    )

    print(response.json())


def calculate_the_signature(secret_key: str = None) -> dict:
    """
    实现机器人安全组接口策略，此处使用官方文档中的案例写法
    :param secret_key:
    :return:
    """
    # 机器人安全密钥
    secret = secret_key

    # 计算时间戳
    timestamp = str(round(time.time() * 1000))

    # 计算签名
    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    return {"timestamp": timestamp, "sign": sign}


def get_subscribe() -> str:
    """
    可通过内网访问已部署的项目接口获取订阅，返回字符串形式的明文订阅链接
    :return:
    """

    return "A shareLink of the V2RayCloudSpider server."


def quick_start(secret_key: str, access_token: str):
    """
    一个快速创建的demo
    :param secret_key: see https://developers.dingtalk.com/document/robots/customize-robot-security-settings
    :param access_token: see https://developers.dingtalk.com/document/robots/custom-robot-access
    :return:
    """
    # 获取订阅
    subscribe = get_subscribe()

    # 安全组：计算时间戳和应用签名
    security_group = calculate_the_signature(secret_key=secret_key)

    # 通过post机器人接口发送订阅
    ding_to_group(
        subscribe=subscribe,
        access_token=access_token,
        timestamp=security_group["timestamp"],
        sign_=security_group["sign"],
    )


if __name__ == "__main__":
    quick_start(secret_key="", access_token="")
