__all__ = ['subs2node']

import base64
from urllib.parse import urlparse

import requests

debug_sub = 'https://www.recear.xyz/link/jOQfjDcGnXO8iOcf?sub=1'


def _is_available(subs_node: list, cache_path: str = 'node_info.txt'):
    sub_node = b"djFoazAwNy5yZWNhcmUudG9wOjExMTA3OmF1dGhfYWVzMTI4X3NoYTE6Y2hhY2hhMjAtaWV0ZjpodHRwX3NpbXBsZTpVbGRvV1d4Qi8_b2Jmc3BhcmFtPU5ERm1OelUwTlRJNU55NXRhV055YjNOdlpuUXVZMjl0JnByb3RvcGFyYW09TkRVeU9UYzZZVGs0T0hGdCZyZW1hcmtzPTc3aXhUSFl4NzdpeFcxTlRVbDNrdUszb3ZhenZ1TEhwcHBubXVLOGc0cEdqSUMwZ01URXhNRGNnNVkyVjU2dXY1WS1qJmdyb3VwPVVrVQ "

    sub_info = base64.decodebytes(sub_node)
    print(sub_info)


def subs2node(subs: str, cache_path: str or bool = 'node_info.txt', timeout: int = None) -> dict:
    """
    将订阅连接转换成节点数据
    @param timeout:
    @todo: 规则清洗。
    一般订阅解包后，两条信息分别用于描述“可用剩余时长”与"可用剩余流量"，其加密特征与节点完全不同
    @param cache_path: .txt 缓存文件路径
    @param subs: any class_ subscribe 需要解析的订阅链接
    @return:{'subs': subs, "node": info}
    """

    # 参数初始化
    class_ = ''
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53"}
    # 危险操作：使流量不通过系统代理
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

        if cache_path:
            with open(cache_path, 'wb') as f:
                f.write(node_info)

        return {'subs': subs, 'info': obj_analyze, "node": [i for i in node_info.decode("utf8").split("\n") if i]}
    except requests.exceptions.MissingSchema:
        print(f'{subs} -- 传入的subs格式有误或不是订阅链接')
    except requests.exceptions.ProxyError:
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f'{subs} -- {e}')
