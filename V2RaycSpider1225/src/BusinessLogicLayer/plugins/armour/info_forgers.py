import json
import urllib.request

import requests

from src.BusinessCentralLayer.setting import PROXY_POOL


def get_header(use_faker=False) -> str:
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                             " Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71"}
    if not use_faker:
        return headers['User-Agent']


def get_proxy(protocol: str = "http"):
    """

    :param protocol: http https socket
    :return:
    """
    params = {
        "type": protocol
    }
    host = PROXY_POOL['host']
    port = PROXY_POOL['port']
    session = requests.session()
    try:
        response = session.get(f"http://{host}:{port}/pop", params=params)
        proxy = response.json()['proxy']
        return {protocol: proxy}
    # 接口不可用 / 代理池欠维护
    except (requests.exceptions.ConnectionError, KeyError, json.decoder.JSONDecodeError):
        return {}


def flow_probe(url: str) -> dict:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31"
    }
    # 获取本地代理，若未开启系统代理 proxies={}，若开启 proxies={'http':"", 'https':"", 'socket':""}
    proxies: dict = urllib.request.getproxies()

    # 重试N次
    while True:
        try:
            # 首次，使用本地代理探测网站，若成功则直接返回 localhost proxies。使用空代理进行后续作业。
            # 若干次，在重试区间内不断刷新代理头并探测网站，若成功则返回可用 proxies
            session = requests.session()
            response = session.get(url, headers=headers, proxies=proxies, timeout=5)
            if response.status_code != 200:
                raise requests.exceptions.SSLError
            break
        except (requests.exceptions.SSLError, requests.exceptions.Timeout, requests.exceptions.ProxyError):
            # TODO 刷新 https 代理头，获取代理头依赖第三方项目 proxy-pool
            proxy = get_proxy(protocol="https")
            if proxy:
                proxies.update(proxy)
            else:
                return proxy
    return proxies
