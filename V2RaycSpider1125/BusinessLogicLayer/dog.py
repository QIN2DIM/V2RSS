import base64

import requests

from BusinessLogicLayer.plugins import get_header


def subs2node(cache_path: str, subs: str) -> dict:
    """

    @param cache_path: .txt
    @param subs: any class_ subscribe
    @return:pure links of these node
    """
    if not cache_path.endswith('.txt'):
        return {}

    headers = {'user-agent': get_header()}
    res = requests.get(subs, headers=headers)
    if res.status_code == 200:
        with open(cache_path, 'wb') as f:
            f.write(base64.decodebytes(res.content))
        with open(cache_path, 'r') as f:
            data = [i.strip() for i in f.readlines()]
    return {'subs': subs, "node": data[2:]}
