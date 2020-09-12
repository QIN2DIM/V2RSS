# windows10 下不可用
import sys
sys.path.append('/qinse/V2RaycSpider0817')

from MiddleKey.VMes_IO import vmess_IO
from spiderNest.V2Ray_vms import UFO_Spider

if __name__ == '__main__':
    vio = vmess_IO('v2ray')
    if '无' in vio:
        UFO_Spider()
        print(vmess_IO('v2ray'))
    else:
        print(vio)

