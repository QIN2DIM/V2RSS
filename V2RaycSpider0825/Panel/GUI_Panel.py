import os
import sys
from datetime import datetime, timedelta
import easygui
import paramiko
import pyperclip
from Panel.reball import __retrace__

"""##########################################"""
# 我就是V2Ray云采姬
title = 'V2Ray云彩姬'

# 默认导出路径
out_fp = 'C:/V2RaySpider'
out_vp = out_fp + '/log_VMess.txt'

# 进程锁状态码
status_lock = 0
# 进程锁死时长，type：float∈[1,60]
bandBatch = 1
# 进程解锁时间
compNum = ''

# V2RAY预设信息
v_msg = 'SNI:V_{}'.format(str(datetime.now()).split(' ')[0])
v_success = '获取成功，点击确定自动复制链接'
"""##########################################"""


# 初始化文档树
def INIT_docTree():
    if not os.path.exists(out_fp):
        os.mkdir(out_fp)
    try:
        if not out_vp.split('/')[-1] in os.listdir(out_fp):
            with open(out_vp, 'w', encoding='utf-8', newline='') as f:
                f.writelines(['Time', ',', 'AttentionLink', ',', '类型', '\n'])
    except FileExistsError:
        pass


INIT_docTree()


# 进程冻结
def Freeze():
    # 冻结进程
    proLock()
    while True:
        if status_lock:
            usr_a = easygui.ynbox(
                '请勿频繁操作,链接已复制到剪贴板\n本机IP已被冻结,可在本地文件中查看访问记录\n解封时间:{}'.format(compNum),
                title=title,
                choices=['[1]返回主菜单', '[2]退出']
            )
            if usr_a:
                break
            else:
                sys.exit()
        else:
            break
    # 正常使用
    return True


# 进程锁
def proLock():
    """
    : 进程锁
    # GUI启动时，先检索预设目的地（dir），若存在，则检查txt状态
        # 读取 txt，将str->deltatime，记录now-datetime->deltatime
        # 时间比对，若 difference >= 1 minute, 则认为是过热文件
            # 删除过热文件
        # 否则保留
    # 若没有，则初始化文档树
        # 创建文件夹
        # 建立临时txt
        # 使用deltatime，minute + 1，并将daltatime->str写入txt
    """

    global compNum, status_lock

    try:
        with open(out_vp, 'r', encoding='utf-8') as f:
            dataFlow = [vm for vm in f.read().split('\n') if vm != ''][-1].split(',')[0]
            dateFlow = dataFlow.split(',')[0]
            # dateFlow = f.readlines()[-1].split(',')[0].strip()
            if '-' not in dateFlow:
                return False
        # 记录上次请求时间
        open_time = datetime.fromisoformat(dateFlow)
        # 获取本地时间
        now_ = datetime.now()
        # 比对时间
        compBool = (open_time + timedelta(minutes=bandBatch)) > now_
        # 计算进程冻结结束时间点
        lock_Break = open_time + timedelta(minutes=bandBatch)
        compNum = lock_Break

        # 操作过热则冻结主进程
        if compBool is True:
            status_lock = 1
    except (FileExistsError, PermissionError, FileNotFoundError, ValueError) as e:
        print(e)


# 数据IO管理，本地存储，必选
def save_flow(dataFlow='N/A', class_=''):
    with open(out_vp, 'a', encoding='utf-8') as f:
        now_ = str(datetime.now()).split('.')[0]
        f.writelines([now_, ',', dataFlow.strip(), ',', class_, '\n'])


"""#########################################"""

# 文件路径:查询可用订阅连接
aviLink_fp = '/qinse/V2RaycSpider0817/funcBase/func_avi_num.py'

# 文件路径:ssr链接抓取接口
ssrEne_fp = '/qinse/V2RaycSpider0817/funcBase/get_ssr_link.py'

# 文件路径:v2ray链接抓取接口
v2rayEne_fp = '/qinse/V2RaycSpider0817/funcBase/get_v2ray_link.py'


# Service connection
def service_con(command):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname='104.224.177.249',
            port=29710,
            username='root',
            password='KYU77wh7vpRK'
        )
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read().decode()


# Lock behavior
def locker():
    while True:
        if Freeze() and status_lock != 1:
            break


# Main process behavior
class SSRcS_panel(object):

    def __init__(self):
        # 启动GUI
        if Freeze():
            self.Home()

    def Home(self):
        """
        一级菜单
        :return:
        """
        choice_list = ['[1]V2Ray订阅链接', '[2]SSR订阅链接', '[3]打开本地文件', '[4]查询可用链接', '[5]返回', '[6]退出']
        usr_c = easygui.choicebox('功能列表', title, choice_list, preselect=1)
        try:
            if '[1]' in usr_c:
                self.do_v2rayEne()
            elif '[2]' in usr_c:
                self.do_ssrEne()
            elif '[3]' in usr_c:
                os.startfile(out_vp)
            elif '[4]' in usr_c:
                self.find_aviLink()
            elif '[5]' in usr_c:
                __retrace__('返回')
            else:
                __retrace__('退出')
        except TypeError:
            pass

    def find_aviLink(self):
        """
        查询池状态
        :return:
        """

        # 获取服务器响应
        avi_info = service_con('python3 {}'.format(aviLink_fp))

        # 弹出提示
        easygui.choicebox(msg='注:如表所示审核日期为北京时间', title=title, choices=avi_info.split('\n'), )

        # 返回主菜单
        self.Home()

    def do_ssrEne(self):
        """
        启动 ssr 爬虫
        :return:
        """

        # 先看又没有库存，若有直接拿,若无则启动脚本抓取ssr订阅链接
        ssr_attention_link = service_con('python3 {}'.format(ssrEne_fp))

        # 分发结果
        self.resTip(ssr_attention_link, 'ssr')

    def do_v2rayEne(self):

        # 获取v2ray订阅链接
        v2ray_attention_link = service_con('python3 {}'.format(v2rayEne_fp))

        # 公示分发结果
        self.resTip(v2ray_attention_link, 'v2ray')

    def resTip(self, AttentionLink, task_name):
        """

        :param task_name: 任务类型：ssr ； v2ray
        :param AttentionLink: 订阅链接
        :return:
        """

        # 公示分发结果
        easygui.enterbox(msg=v_success, title=title, default=AttentionLink)

        try:
            # 获取成功
            if 'http' in AttentionLink:
                # 自动复制
                pyperclip.copy(AttentionLink)
                # 将数据存入本地文件
                save_flow(AttentionLink, task_name)
            # 获取异常
            else:
                easygui.enterbox(msg=v_msg, title=title, default='功能未开放')

        finally:
            # 返回主菜单
            self.Home()


"""#########################################"""

if __name__ == '__main__':
    # proLock()
    SSRcS_panel()
