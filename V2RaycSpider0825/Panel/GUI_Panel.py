from datetime import datetime, timedelta
import easygui
import paramiko
import pyperclip

from config import *

"""##########################################"""

# 进程锁状态码
status_lock = 0

# 进程解锁时间
compNum = ''

# 热操作次数(当前版本弃用该参数)
hotOpt = 0
# V2RAY预设信息
v_msg = 'SNI:V_{}'.format(str(datetime.now()).split(' ')[0])
v_success = '获取成功，点击确定自动复制链接'

"""##########################################"""


# 初始化文档树
def INIT_docTree():
    if not os.path.exists(SYS_LOCAL_fPATH):
        os.mkdir(SYS_LOCAL_fPATH)
    try:
        if not SYS_LOCAL_vPATH.split('/')[-1] in os.listdir(SYS_LOCAL_fPATH):
            with open(SYS_LOCAL_vPATH, 'w', encoding='utf-8', newline='') as f:
                f.writelines(['Time', ',', 'AttentionLink', ',', '类型', '\n'])
    except FileExistsError:
        pass


INIT_docTree()
resp = True


# 进程冻结
def Freeze():
    # 冻结进程
    proLock()
    while True:
        if status_lock:
            usr_a = easygui.ynbox(
                '>>> 请勿频繁请求！\n本机IP已被冻结 {} 可在本地文件中查看访问记录'
                '\n解封时间:{}'.format(str(compNum - datetime.now()).split('.')[0], compNum),
                title=TITLE,
                choices=['[1]确定', '[2]返回']
            )
            if usr_a:
                # continue 内核锁死  break 功能限制
                continue
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
        # 使用deltatime，minute + 1，并将deltatime->str写入txt
    """

    global compNum, status_lock

    try:
        with open(SYS_LOCAL_vPATH, 'r', encoding='utf-8') as f:
            dataFlow = [vm for vm in f.read().split('\n') if vm != ''][-1].split(',')[0]
            dateFlow = dataFlow.split(',')[0]
            if '-' not in dateFlow:
                return False
        # 记录上次请求时间
        open_time = datetime.fromisoformat(dateFlow)
        # 获取本地时间
        now_ = datetime.now()
        # 比对时间
        compBool = (open_time + timedelta(minutes=BAND_BATCH)) > now_
        # 计算进程冻结结束时间点
        lock_Break = open_time + timedelta(minutes=BAND_BATCH)
        compNum = lock_Break

        # 操作过热则冻结主进程
        if compBool is True:
            status_lock = 1
        else:
            status_lock = 0
    except (FileExistsError, PermissionError, FileNotFoundError, ValueError) as e:
        print(e)


# 数据IO管理，本地存储，必选
def save_flow(dataFlow='N/A', class_=''):
    with open(SYS_LOCAL_vPATH, 'a', encoding='utf-8') as f:
        now_ = str(datetime.now()).split('.')[0]
        f.writelines([now_, ',', dataFlow.strip(), ',', class_, '\n'])


"""#########################################"""


# Service connection
def service_con(command):
    # TODO: Hide server private information
    # FIXME: fix this bug now!!
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=ECS_HOSTNAME,
            port=ECS_PORT,
            username=ECS_USERNAME,
            password=ECS_PASSWORD
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
        # self.Home()
        self.ssr_attention_link = ''
        self.v2ray_attention_link = ''
        pass

    def Home(self, ):
        """
        一级菜单
        :mode: True:本地采集，False 服务器采集
        :return:
        """
        global resp

        # 初始化进程冻结锁
        Freeze()

        # 根据配置信息自动选择采集模式
        choice_list = ['[1]V2Ray订阅链接', '[2]SSR订阅链接', '[3]打开本地文件', '[4]查询可用链接', '[5]返回',
                       '[6]退出'] if START_MODE == 'cloud' else \
            ['[1]V2Ray订阅链接', '[2]SSR订阅链接', '[3]打开本地文件', '[4]返回', '[5]退出']
        # UI功能选择
        usr_c = easygui.choicebox('功能列表', TITLE, choice_list, preselect=1)
        try:
            if 'V2Ray' in usr_c:
                self.do_v2rayEne()
            elif 'SSR' in usr_c:
                self.do_ssrEne()
            elif '打开本地文件' in usr_c:
                os.startfile(SYS_LOCAL_vPATH)
            elif '查询可用链接' in usr_c:
                self.find_aviLink()
            elif '返回' in usr_c:
                # __retrace__('返回')
                return resp
            else:
                # __retrace__('退出')
                resp = False
        except TypeError:
            return False
        finally:
            return resp

    def find_aviLink(self):
        """
        查询池状态
        :return:
        """

        # 获取服务器响应
        avi_info = service_con('python3 {}'.format(AviLINK_FILE_PATH))

        # 弹出提示
        easygui.choicebox(msg='注:如表所示审核日期为北京时间', title=TITLE, choices=avi_info.split('\n'), )

        # 返回主菜单
        self.Home()

    def do_ssrEne(self):
        """
        启动 ssr 爬虫
        :return:
        """
        from spiderNest.SSRcS_xjcloud import LocalResp
        try:
            if START_MODE == 'cloud':
                # 先看有没有库存，若有直接拿,若无则启动脚本抓取ssr订阅链接
                self.ssr_attention_link = service_con('python3 {}'.format(SSR_ENE_FILE_PATH))
            elif START_MODE == 'local':
                self.ssr_attention_link = LocalResp().start()
        finally:
            # 分发结果
            self.resTip(self.ssr_attention_link, 'ssr')

    def do_v2rayEne(self):
        from spiderNest.V2Ray_vms import LocalResp
        try:
            if START_MODE == 'cloud':
                # 获取v2ray订阅链接
                self.v2ray_attention_link = service_con('python3 {}'.format(V2RAY_ENE_FILE_PATH))
            elif START_MODE == 'local':
                self.v2ray_attention_link = LocalResp().start()
        finally:
            # 公示分发结果
            self.resTip(self.v2ray_attention_link, 'v2ray')

    def resTip(self, AttentionLink: str, task_name):
        """

        :param task_name: 任务类型：ssr ； v2ray
        :param AttentionLink: 订阅链接
        :return:
        """
        global hotOpt
        # 公示分发结果
        if AttentionLink.strip() != '':
            easygui.enterbox(msg=v_success, title=TITLE, default=AttentionLink)
            hotOpt += 1
        try:
            # 获取成功
            if 'http' in AttentionLink:
                # 自动复制
                pyperclip.copy(AttentionLink)
                # 将数据存入本地文件
                save_flow(AttentionLink, task_name)
            # 获取异常
            else:
                easygui.exceptionbox(
                    msg=v_msg + '\n服务器维护中，请稍后再试;\n请勿频繁请求，您的操作权限可能已被冻结',
                    title=TITLE
                )

        finally:
            # 返回主菜单
            self.Home()


"""#########################################"""

if __name__ == '__main__':
    # proLock()
    SSRcS_panel()
