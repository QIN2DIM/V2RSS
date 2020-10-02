from spiderNest.preIntro import *
from config import SYS_AIRPORT_INFO_PATH

path_ = SYS_AIRPORT_INFO_PATH


def save_login_info(VMess, class_):
    """
    VMess入库
    class_: ssr or v2ray
    """
    now = str(datetime.now()).split('.')[0]
    with open(path_, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 入库时间，Vmess,初始化状态:0
        writer.writerow(['{}'.format(now), '{}'.format(VMess), class_, '0'])


def vmess_IO(class_):
    """
    获取可用订阅链接并刷新存储池
    class_: ssr ; v2ray
    """

    def refresh_log(dataFlow):
        with open(path_, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(dataFlow)

    try:
        with open(path_, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            vm_q = [vm for vm in reader]
            new_q = vm_q
            for i, value in enumerate(reversed(vm_q)):
                if value[-1] == '0' and value[-2] == class_:
                    vm = value[1]
                    new_q[-(i + 1)][-1] = '1'
                    break
        refresh_log(new_q)
        return vm
    except UnboundLocalError:
        return '无可用订阅连接'


def avi_num():
    from datetime import datetime, timedelta
    with open(path_, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        vm_list = [i for i in reader]
        # ['2020-08-06 04:27:59', 'link','class_', '1']

        vm_q = [vm for vm in vm_list if vm[-1] == '0']

        tag_items = ''
        for vm in vm_list:
            if vm[-1] == '0':
                bei_ing_time = datetime.fromisoformat(vm[0]) + timedelta(hours=12)
                tag_items += '\n【√可选】【{}】#{}'.format(bei_ing_time, vm[-2])

        return tag_items
