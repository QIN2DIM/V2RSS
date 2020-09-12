# windows10 下不可用
import sys
sys.path.append('/qinse/V2RaycSpider0817')

from MiddleKey.VMes_IO import vmess_IO
from spiderNest.SSRcS_xjcloud import UFO_Spider

if __name__ == '__main__':
    vio = vmess_IO('ssr')
    if '无' in vio :
        UFO_Spider()
        print(vmess_IO('ssr'))
    else :
        print(vio)