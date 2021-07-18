import base64
from urllib.parse import urlparse

import requests


def subs2node(subs: str, timeout: int = None) -> dict:
    """
    将订阅链接解析成节点数据
    @param timeout: 设置requests 超时时间
    一般订阅解包后，两条信息分别用于描述“可用剩余时长”与"可用剩余流量"，其加密特征与节点完全不同
    @param subs: any class_ subscribe 需要解析的订阅链接
    @return:{'subs': subs, "node": info}
    """

    # 订阅类型
    class_ = ''
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53"}
    # 危险操作：流量不通过系统代理
    proxies = {
        'http': None,
        'https': None
    }
    try:
        # 订阅解析
        obj = urlparse(subs)
        # 类型粗识别
        if '1' in obj.query:
            class_ = 'ssr'
        elif '3' in obj.query:
            class_ = 'v2ray'

        obj_analyze = {'net': obj.netloc, 'token': obj.path.split('/')[-1], 'class_': class_}
        if timeout:
            res = requests.get(subs, headers=headers, timeout=timeout)
        else:
            # res = requests.get(subs, headers=headers)
            res = requests.get(subs, headers=headers, proxies=proxies)

        node_info = base64.decodebytes(res.content)

        return {'subs': subs, 'info': obj_analyze, "node": [i for i in node_info.decode("utf8").split("\n") if i]}
    except requests.exceptions.MissingSchema:
        print(f'{subs} -- 传入的subs格式有误或不是订阅链接')
    except requests.exceptions.ProxyError:
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f'{subs} -- {e}')
