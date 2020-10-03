import csv
import threading
import webbrowser
from datetime import datetime, timedelta
from config import *

try:
    import easygui
    import paramiko
    import pyperclip
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    def init_requirements():
        """自动下载缺失模块"""
        try:
            with open(os.path.join(ROOT_PROJECT_PATH, 'requirements.txt'), 'r', encoding='utf-8') as f:
                r_list = [i for i in f.read().split('\n')]
            for i in range(r_list.__len__()):
                try:
                    model = r_list.pop()
                    os.system('pip install {} -i https://pypi.tuna.tsinghua.edu.cn/simple'.format(model))
                except OSError:
                    pass
            if r_list.__len__() > 0:
                print('>>> 安装失败的模块:{}'.format(r_list))
        except FileNotFoundError:
            pass


    init_requirements()
    import easygui
    import paramiko
    import pyperclip
    import requests
    from bs4 import BeautifulSoup

"""##################进程管理模块########################"""

# -------------------------------
# 进程管理模块
# -------------------------------

# 进程锁状态码
status_lock = 0

# 进程解锁时间
compNum = ''

# 热操作次数(当前版本弃用该参数)
hotOpt = 0
# V2RAY预设信息
v_msg = 'SNI:V_{}'.format(str(datetime.now()).split(' ')[0])
v_success = '获取成功，点击确定自动复制链接'

ssr_attention_link = ''
v2ray_attention_link = ''


# 初始化文档树
def INIT_process_docTree():
    if not os.path.exists(SYS_LOCAL_fPATH):
        os.mkdir(SYS_LOCAL_fPATH)
    try:
        if not SYS_LOCAL_vPATH.split('/')[-1] in os.listdir(SYS_LOCAL_fPATH):
            with open(SYS_LOCAL_vPATH, 'w', encoding='utf-8', newline='') as f:
                f.writelines(['Time', ',', 'AttentionLink', ',', '类型', '\n'])
    except FileExistsError:
        pass


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

    @staticmethod
    def find_aviLink():
        """
        查询池状态
        :return:
        """

        # 获取服务器响应
        avi_info = service_con('python3 {}'.format(AviLINK_FILE_PATH))

        # 弹出提示
        if avi_info != '\n':
            easygui.choicebox(msg='注:如表所示审核日期为北京时间', title=TITLE, choices=avi_info.split('\n'), )
        else:
            easygui.exceptionbox(msg='无可用订阅链接!', title=TITLE)

        # 返回上一页
        return True

    def do_ssrEne(self, ):
        """
        启动 ssr 爬虫
        :return:
        """
        # TODO
        # FIXME:pyinstaller 打包bug；调用修改global value 会使本函数无法被main function transfer
        # FIXME:pyinstaller 打包正确运行情况：


        """调试版代码"""
        # from spiderNest.SSRcS_xjcloud import LocalResp
        # try:
        #     if START_MODE == 'cloud':
        #         # 先看有没有库存，若有直接拿,若无则启动脚本抓取ssr订阅链接
        #         self.ssr_attention_link = service_con('python3 {}'.format(SSR_ENE_FILE_PATH))
        #     elif START_MODE == 'local':
        #         self.ssr_attention_link = LocalResp().start()
        # finally:
        #     # 分发结果
        #     self.resTip(self.ssr_attention_link, 'ssr')
        #     return True

        """软件打包代码"""
        try:
            self.ssr_attention_link = service_con('python3 {}'.format(SSR_ENE_FILE_PATH))
        finally:
            return self.resTip(self.ssr_attention_link, 'ssr')
            # easygui.enterbox(msg=v_success, title=TITLE, default=self.ssr_attention_link)

    def do_v2rayEne(self,):

        """调试版代码"""
        # from spiderNest.V2Ray_vms import LocalResp
        # try:
        #     if START_MODE == 'cloud':
        #         # 获取v2ray订阅链接
        #         self.v2ray_attention_link = service_con('python3 {}'.format(V2RAY_ENE_FILE_PATH))
        #     elif START_MODE == 'local':
        #         self.v2ray_attention_link = LocalResp().start()
        # finally:
        #     # 公示分发结果
        #     return self.resTip(self.v2ray_attention_link, 'v2ray')

        """软件打包代码"""
        try:
            self.v2ray_attention_link = service_con('python3 {}'.format(V2RAY_ENE_FILE_PATH))
        finally:
            return self.resTip(self.v2ray_attention_link, 'v2ray')
            # easygui.enterbox(msg=v_success, title=TITLE, default=self.v2ray_attention_link)


    @staticmethod
    def resTip(AttentionLink: str, task_name):
        """

        :param task_name: 任务类型：ssr ； v2ray
        :param AttentionLink: 订阅链接
        :return:
        """
        # 公示分发结果
        if AttentionLink.strip() != '':
            easygui.enterbox(msg=v_success, title=TITLE, default=AttentionLink)
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
            # 返回上一页
            return True


"""#####################网络审查模块####################"""

# -------------------------------
# 网络审查模块
# -------------------------------

import socket

# 结果播报容器
report = ''


def getReport():
    global report
    report = checker()
    easygui.msgbox(report, TITLE, )


def isNetChainOK(test_server):
    """

    :param test_server: tuple('ip or domain name', port)
    :return:
    """
    s = socket.socket()
    s.settimeout(2)
    try:
        status = s.connect_ex(test_server)
        if status == 0:
            s.close()
            return True
        else:
            return False
    except socket.error as e:
        return False


def checker():
    global report
    test_list = {
        'google': ('www.google.com', 443),
        'baidu' : ('www.baidu.com', 443)
    }

    PROXY_status = isNetChainOK(test_list['google'])
    PAC_status = isNetChainOK(test_list['baidu'])
    Evaluation = ''
    if PAC_status is True and PROXY_status is False:
        Evaluation = '当前网络状态良好, 网络代理未开启'
    elif PAC_status and PROXY_status is True:
        Evaluation = '网络状态极佳, 代理服务运行正常'
    else:
        Evaluation = '当前网络环境较差，且网络代理运行异常'

    report = ">>> www.google.com, 443, {}\n>>> www.baidu.com, 443, {}\n>>> {}" \
             "".format(str(PROXY_status), str(PAC_status), Evaluation)

    return report


"""#####################机场生态查询模块####################"""

# 机场生态文件输出地址
SYS_LOCAL_aPATH = ''


# 初始化文档树
def INIT_airport_docTree():
    if not os.path.exists(SYS_LOCAL_fPATH):
        os.mkdir(SYS_LOCAL_fPATH)


# 保存数据至本地
def out_flow(dataFlow, reFP=''):
    global SYS_LOCAL_aPATH
    SYS_LOCAL_aPATH = os.path.join(easygui.diropenbox('选择保存地址', TITLE), 'AirportURL.csv')
    try:
        with open(SYS_LOCAL_aPATH, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for x in dataFlow:
                writer.writerow(x)
    except PermissionError:
        easygui.exceptionbox('系统监测到您正在占用核心文件，请解除该文件的资源占用:{}'.format(SYS_LOCAL_aPATH))


# 通过前端panel展示数据
dataList = []


def show_response():
    """

    :return:
    """
    usr_c = easygui.choicebox(msg='选中即可跳转目标网址,部分机场需要代理才能访问', title=TITLE, choices=dataList)
    if usr_c:
        if 'http' in usr_c:
            url = usr_c.split(' ')[-1][1:-1]
            webbrowser.open(url)
        else:
            easygui.msgbox('机场网址失效或操作有误', title=TITLE, ok_button='返回')
            show_response()
    elif usr_c is None:
        return 'present'


class sAirportSpider(object):

    @staticmethod
    def slaver(url, ):

        # 审查网络状况
        def layer():
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
                res = requests.get(url, headers=headers)
                res.raise_for_status()
                return res.text
            except Exception as e:
                print(e)
                return False

        # 获取导航语
        def h3Log(target):
            own = target.find_all('span', class_='fake-TITLE')
            souls = []
            for soul in own:
                try:
                    soul = soul.text.split('.')[-1].strip()
                    souls.append(soul)
                except TypeError as e:
                    print(e)
            return souls

        # 清洗链接中的邀请码和注册码，返回纯净的链接
        def href_cleaner(hrefTarget, ):
            if isinstance(hrefTarget, list):
                clean_href = []
                for href in hrefs:
                    if '?' in href:
                        href = href.split('?')[0]
                        clean_href.append(href)
                    else:
                        clean_href.append(href)
                return clean_href

            elif isinstance(hrefTarget, str):
                return hrefTarget.split('?')[0]

        def show_data(show=True):
            # 使用全局变量输出前端信息
            global dataList
            Out_flow = ['序号    机场名    官网链接']

            if show:
                dataList = Out_flow + ['【{}】 【{}】 【{}】'.format(i + 1, list(x)[0], list(x)[-1]) for i, x in
                                       enumerate(zip(names, hrefs)) if 'http' in list(x)[-1]]
                # 前端展示API
                return show_response()
            else:
                return [['序号', '机场名', '官网连接'], ] + \
                       [[i + 1, list(x)[0], list(x)[-1]] for i, x in
                        enumerate(zip(names, hrefs)) if 'http' in list(x)[-1]]

        func_list = ['[1]查看', '[2]保存', '[3]返回']
        usr_d = easygui.choicebox(title=TITLE, choices=func_list)
        if '返回' in usr_d:
            return True

        response = layer()
        if response:
            soup = BeautifulSoup(response, 'html.parser')

            # 定位导航语
            # barInfo = h3Log(soup)

            # 定位项目
            items = soup.find_all('li', class_='link-item')

            # 机场名
            names = [item.find('span', class_='sitename').text.strip() for item in items]

            # 获取去除邀请码的机场链接
            hrefs = [item.find('a')['href'] for item in items]
            hrefs = href_cleaner(hrefs)

            if '保存' in usr_d:
                # 保存至本地
                out_flow(show_data(show=False))
                # 自动打开
                os.startfile(SYS_LOCAL_aPATH)
            elif '查看' in usr_d:
                # 前端打印
                return show_data()


"""###################主菜单######################"""


# 所有初始化设置函数请在此编写
class PrepareENV(object):
    """环境初始化检测"""

    @staticmethod
    def init_fake_user_agent():
        """
        将伪装请求头文件写入系统缓存，不执行该初始化步骤 fake-useragent库将发生致命错误
        :return:
        """
        import tempfile
        # fake_useragent json file name
        fup = 'fake_useragent_0.1.11.json'
        if fup not in os.listdir(tempfile.gettempdir()):
            os.system('copy {} {}'.format(
                os.path.join(ROOT_DATABASE, fup),
                os.path.join(tempfile.gettempdir(), fup)
            ))
            easygui.exceptionbox('>>> 环境初始化成功,正在尝试重启脚本', TITLE)
            try:
                os.system('python {}'.format(os.path.join(ROOT_PROJECT_PATH, 'main.py')))
                sys.exit()
            except OSError:
                easygui.exceptionbox('查找失败，请手动重启脚本', TITLE)

    @staticmethod
    def init_service_info():
        """检查服务器书写是否正确"""
        msg = """
        >>> ECS_HOSTNAME:{}\n
        >>> ECS_PORT:{}\n
        >>> ECS_PASSWORD:{}\n
        >>> ECS_USERNAME:{}\n""".format(ECS_HOSTNAME, ECS_PORT, ECS_PASSWORD, ECS_USERNAME)
        if ECS_HOSTNAME == '':
            easygui.textbox('\n系统监测到您config.py服务器配置异常'
                            '\n\n当hostname为空时,默认启动本地采集', TITLE, msg, codebox=True)

    @staticmethod
    def init_requirements():
        """自动下载缺失模块"""
        try:
            with open(os.path.join(ROOT_PROJECT_PATH, 'requirements.txt'), 'r', encoding='utf-8') as f:
                r_list = [i for i in f.read().split('\n')]
            for i in range(r_list.__len__()):
                try:
                    model = r_list.pop()
                    os.system('pip install {} -i https://pypi.tuna.tsinghua.edu.cn/simple '.format(model))
                except OSError:
                    pass
            if r_list.__len__() > 0:
                print('>>> 安装失败的模块:{}'.format(r_list))
        except FileNotFoundError:
            pass

    def run_start(self, init=False):
        if init is True:
            # 初始化用户账号
            self.init_fake_user_agent()

            # 初始化服务器信息
            self.init_service_info()

            # 初始化Python第三方库
            # self.init_requirements()

            # 初始化核心文档树
            INIT_process_docTree()

            # 初始化机场狗文档树
            INIT_airport_docTree()


class V2RaycSpider_Master_Panel(object):

    def __init__(self, init=True):

        # 主菜单
        self.MAIN_HOME_MENU = ['[1]查看机场生态', '[2]获取订阅链接', '[3]检查网络状态', '[4]检查版本更新', '[5]退出', ]

        # air_port_menu
        self.AIRPORT_HOME_MENU = ['[1]白嫖机场', '[2]高端机场', '[3]机场汇总', '[4]返回', '[5]退出']
        self.AIRPORT_FUNCTION_MENU = ['[1]查看', '[2]保存', '[3]返回']
        self.airHome = 'https://52bp.org'

        # 根据配置信息自动选择采集模式
        self.SSR_HOME_MENU = ['[1]V2Ray订阅链接', '[2]SSR订阅链接', '[3]打开本地文件', '[4]查询可用链接', '[5]返回',
                              '[6]退出'] if START_MODE == 'cloud' else \
            ['[1]V2Ray订阅链接', '[2]SSR订阅链接', '[3]打开本地文件', '[4]返回', '[5]退出']

        # 环境初始化
        pe = PrepareENV()
        pe.run_start(init=init)

        # 自启
        # self.home_menu()

    @staticmethod
    def kill(info):
        try:
            easygui.exceptionbox(info, TITLE)
        except FileNotFoundError:
            pass

    def home_menu(self):
        """主菜单"""
        # ['[1]查看机场生态', '[2]获取订阅链接', '[3]检查网络状态', '[4]检查版本更新', '[5]退出', ]
        resp = True
        usr_c = easygui.choicebox('功能列表', TITLE, self.MAIN_HOME_MENU, preselect=1)
        try:
            if '[1]查看机场生态' in usr_c:
                resp = self.air_port_menu()
            elif '[2]获取订阅链接' in usr_c:
                resp = self.ssr_spider_menu()
            elif '网络' in usr_c:
                threading.Thread(target=getReport, ).start()
                easygui.ynbox('正在审查网络环境', 'V2Ray云彩姬')
            elif '更新' in usr_c:
                easygui.textbox("封测阶段暂不开放联网更新接口！", title='V2Ray云彩姬')
            else:
                resp = False
        except TypeError:
            # 若出现未知异常，则启动垃圾回收机制，强制退出
            resp = False
        finally:
            if resp:
                self.home_menu()
            else:
                sys.exit()

    def air_port_menu(self):
        """air_port_menu GUI导航"""
        # ['[1]白嫖机场', '[2]高端机场', '[3]机场汇总', '[4]返回', '[5]退出']
        usr_c = easygui.choicebox('功能列表', TITLE, self.AIRPORT_HOME_MENU, preselect=0)
        resp = True
        try:
            if '[1]白嫖机场' in usr_c:
                resp = sAirportSpider.slaver(self.airHome + '/free-airport.html', )
            elif '[2]高端机场' in usr_c:
                resp = sAirportSpider.slaver(self.airHome + '/vip-airport.html', )
            elif '[3]机场汇总' in usr_c:
                resp = sAirportSpider.slaver(self.airHome + '/airport.html', )
            elif '[4]返回' in usr_c:
                resp = True
            else:
                resp = False
        except TypeError:
            resp = False
        finally:
            # 返回
            return resp

    def ssr_spider_menu(self):
        """
        一级菜单
        :mode: True:本地采集，False 服务器采集
        :return:
        """
        # 初始化进程冻结锁
        Freeze()
        resp = True

        # UI功能选择
        usr_c = easygui.choicebox('功能列表', TITLE, self.SSR_HOME_MENU, preselect=1)
        try:
            sp = SSRcS_panel()
            if '[1]V2Ray订阅链接' in usr_c:
                resp = sp.do_v2rayEne()
            elif '[2]SSR订阅链接' in usr_c:
                resp = sp.do_ssrEne()
            elif '[3]打开本地文件' in usr_c:
                os.startfile(SYS_LOCAL_vPATH)
            elif '[4]查询可用链接' in usr_c:
                resp = sp.find_aviLink()
            elif '[5]返回' in usr_c:
                resp = True
            else:
                resp = False
        except TypeError:
            resp = False
        finally:
            return resp
