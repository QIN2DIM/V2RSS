# windows10 下不可用
import sys

sys.path.append('/qinse/V2RaycSpider0825')
from config import NGINX_SSR_PATH

from MiddleKey.VMes_IO import vmess_IO
from spiderNest.SSRcS_xjcloud import UFO_Spider

if __name__ == '__main__':
    vio = vmess_IO('ssr')
    if '无' in vio:
        UFO_Spider()
        ssr = vmess_IO('ssr')
        print(ssr)
        with open(NGINX_SSR_PATH, 'w', encoding='utf-8') as f:
            f.write(ssr)

    else:
        print(vio)
