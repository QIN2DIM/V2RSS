__all__ = ['V2RaycSpiderMasterPanel', 'PrepareEnv']

import os
import sys
import csv
import yaml
import webbrowser
import socket
from datetime import datetime, timedelta

import easygui
import pyperclip
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from BusinessCentralLayer.middleware.redis_io import RedisClient
from config import *

# pip install {package-name} -i https://pypi.tuna.tsinghua.edu.cn/simple

"""################### 进程管理 ######################"""


class ProcessZeus(object):
    def __init__(self) -> None:

        # 进程锁状态
        self.status_lock: bool = True

        # 初始化解锁时间
        self.unlock_time = datetime.now() + timedelta(minutes=BAND_BATCH)

        # 过时请求时间
        self.stale_res_time = None

        # 运行状态
        self.runtime_status = None

        # 返回值
        self.response = True

    # 进程锁
    def process_locker(self):
        self.process_sentinel()  # 唤入哨兵，更新
        while True:
            if self.status_lock and self.stale_res_time:

                # 当链接分发成功，立即锁死进程
                usr_a = easygui.ynbox(
                    '请勿频繁请求！\n\n'
                    f'本机IP已被冻结 {str(self.unlock_time - datetime.now()).split(".")[0]}'
                    f' 可在本地文件中查看访问记录\n\n'
                    f'解封时间:{str(self.unlock_time).split(".")[0]}',
                    title=TITLE,
                    choices=['[1]确定', '[2]返回']
                )
                if usr_a:
                    # continue 进程锁死  break 功能限制
                    continue
                # 手动返回
                else:
                    sys.exit()
            else:
                break
        # 正常运行
        return True

    # 哨兵
    def process_sentinel(self):
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

        try:
            # 记录上次请求时间
            if self.stale_res_time is None:
                self.loads_stale_time()
            if self.stale_res_time:
                # 计算进程解锁时间点
                self.unlock_time = self.stale_res_time + timedelta(minutes=BAND_BATCH)
                # 操作过热则冻结主进程
                self.status_lock = True if self.unlock_time > datetime.now() else False
        except (FileExistsError, PermissionError, FileNotFoundError, ValueError) as e:
            logger_local.exception(e)

    def loads_stale_time(self) -> None:
        # FIXME:
        #  这个模块有bug，需要进一步精确锁死方案，当前方案当文件进程被占用就会失效
        with open(LOCAL_PATH_DATABASE_FH, 'r', encoding='utf-8') as f:
            date_ = [j.split(',')[0] for j in [i.strip() for i in f.readlines()] if j].pop()
            if '-' not in date_:
                self.stale_res_time = False
            else:
                self.stale_res_time = datetime.fromisoformat(date_)


"""################### 内置爬虫 ######################"""


class SubscribeRequester(object):
    """内嵌微型爬虫-订阅链接请求"""

    def __init__(self):
        # 启动GUI
        # self.Home()

        self.subscribe = ''
        self.v2ray_attention_link = ''

    @staticmethod
    def save_flow(dataFlow='N/A', class_=''):
        with open(LOCAL_PATH_DATABASE_FH, 'a', encoding='utf-8') as f:
            now_ = str(datetime.now()).split('.')[0]
            f.writelines([now_, ',', dataFlow.strip(), ',', class_, '\n'])

    def find_aviLink(self):
        """
        查询池状态
        :return:
        """
        from uuid import uuid4

        def search(redis_driver) -> list:
            target_list = []
            for task_type in ['v2ray', 'ssr', 'trojan']:
                target = list(redis_driver.hgetall(
                    REDIS_SECRET_KEY.format(task_type)).items())
                target_list += [''.center(2, ' ').join([i[-1], '{}'.format(task_type), i[0]]) for i in
                                target]
            return target_list

        avi_info = search(rc.get_driver())

        avi2id = dict(zip([str(uuid4())
                           for _ in range(len(avi_info))], avi_info))

        temp_info = ['{}  {}  {}'.format(
            i[-1].split('  ')[0], i[-1].split('  ')[1], i[0]) for i in avi2id.items()]

        avi_info = [''.center(2, ' ').join(
            ['过期时间', '订阅类型', '订阅链接']), ] + temp_info

        usr_choice = easygui.choicebox(msg='注:审核标准为北京时区；点击获取，链接自动复制', title=TITLE, choices=avi_info,
                                       preselect=1)
        logger_local.info(usr_choice)
        if '-' in usr_choice:
            task_name, subscribe = usr_choice.split(
                '  ')[1], avi2id[usr_choice.split('  ')[-1]].split('  ')[-1]
            self.resTip(subscribe, task_name)
            rc.get_driver().hdel(REDIS_SECRET_KEY.format(task_name), subscribe)
        elif '过期时间' in usr_choice:
            logger_local.warning('链接选择错误')
            easygui.msgbox('请选择有效链接', TITLE)
            self.find_aviLink()

        # 返回上一页
        return True

    def resTip(self, subscribe: str, task_name):
        """

        :param task_name: 任务类型：ssr ； v2ray;trojan
        :param subscribe: 订阅链接
        :return:
        """
        # 公示分发结果
        if subscribe.strip():
            easygui.enterbox(msg='获取成功，点击确定自动复制链接',
                             title=TITLE, default=subscribe)
        try:
            # 获取成功
            if 'http' in subscribe:
                logger_local.success("GET--{}".format(subscribe))
                # 自动复制
                pyperclip.copy(subscribe)
                # 将数据存入本地文件
                self.save_flow(subscribe, task_name)
            # 获取异常
            else:
                logger_local.critical('SubscribeGetException')
                easygui.exceptionbox(
                    title=TITLE,
                    msg='SNI:V_{}'.format(str(datetime.now()).split(' ')[0]) +
                        '\n\n请将V2Ray云彩姬更新至最新版本!'
                        '\n\n项目地址:https://github.com/QIN2DIM/V2RayCloudSpider',
                )
                subscribe = requests.get(
                    'https://your_domain/subscribe/{}.txt'.format(task_name)).text
                easygui.enterbox(
                    msg=f'点击获取{task_name}备用链接',
                    title=TITLE,
                    default=subscribe
                )
                # 自动复制
                pyperclip.copy(subscribe)
                # 将数据存入本地文件
                self.save_flow(subscribe, task_name)
        finally:
            # 返回上一页
            return True

    def run(self, mode: str, work_interface: str = '/v2raycs/api/item/subscribe'):
        """
        mode: ssr,v2ray,trojan
        work_interface:

        """
        # TODO:
        #  替换为<弹性伸缩>方案
        # FIXME:
        #  pyinstaller 打包bug；调用修改global value 会使本函数无法被main function transfer

        try:
            self.subscribe = rc.get(REDIS_SECRET_KEY.format(mode))
            if not self.subscribe:
                self.subscribe = requests.post(f"http://{API_HOST}:{API_PORT}{work_interface}",
                                               data={'type': f'{mode}'}).json().get('info')
        finally:
            return self.resTip(self.subscribe, mode)


class AirEcologySpider(object):
    """内嵌微型爬虫-查看机场生态"""

    # TODO：
    #  该模块当前版本仅针对一家网站的公开资源进行访，
    #  在未来版本中增加该模块的侵入性及采集广度，
    #  若本地运行压力较大则可部署到云端运行。
    def __init__(self, **kwargs):
        self.response = None
        self.default_path = None
        self.data_list = None
        self.ae_task = 'https://52bp.org/{}'

        if '高端' in kwargs.get('type', 'none'):
            self.ae_url = self.ae_task.format("vip-airport.html")
        elif '白嫖' in kwargs.get('type', 'none'):
            self.ae_url = self.ae_task.format("free-airport.html")
        else:
            self.ae_url = self.ae_task.format("airport.html")

    def show(self):
        usr_c = easygui.choicebox(
            msg='选中即可跳转目标网址,部分机场需要代理才能访问', title=TITLE, choices=self.data_list)
        logger_local.info(usr_c)
        if usr_c:
            if 'http' in usr_c:
                url = usr_c.split(' ')[-1][1:-1]
                webbrowser.open(url)
            else:
                logger_local.warning('机场网址失效或操作有误')
                easygui.msgbox('机场网址失效或操作有误', title=TITLE, ok_button='返回')
                self.show()
        elif usr_c is None:
            return 'present'

    def save(self, data_flow=None, default_path=None):
        if data_flow is None:
            data_flow = self.response
        if default_path is None:
            default_path = LOCAL_PATH_AIRPORT_INFO
        try:
            with open(default_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for x in data_flow:
                    writer.writerow(x)
            logger_local.info('机场生态信息保存')
        except PermissionError as e:
            logger_local.exception(e)
            easygui.exceptionbox('核心文件被占用:{}'.format(default_path))
            default_path = os.path.join(easygui.diropenbox(msg='选择存储目录', title=TITLE),
                                        os.path.basename(LOCAL_PATH_AIRPORT_INFO))
            self.save(data_flow=data_flow, default_path=default_path)
        finally:
            self.default_path = default_path
            return default_path

    @staticmethod
    def handle_html(url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            return res.text
        except Exception as e:
            logger_local.exception(e)
            return False

    def parse_html(self, response):
        soup = BeautifulSoup(response, 'html.parser')

        # 定位项目
        items = soup.find_all('li', class_='link-item')

        # 机场名
        names = [item.find('span', class_='sitename').text.strip()
                 for item in items]

        # 获取去除邀请码的机场链接
        hrefs = [item.find('a')['href'] for item in items]
        hrefs = self.href_cleaner(hrefs)
        return hrefs

    @staticmethod
    def href_cleaner(hrefs):
        """
        # 清洗链接中的邀请码和注册码，返回纯净的链接
        @param hrefs:
        @return:
        """
        if isinstance(hrefs, list):
            clean_href = []
            for href in hrefs:
                if '?' in href:
                    href = href.split('?')[0]
                    clean_href.append(href)
                else:
                    clean_href.append(href)
            return clean_href

        elif isinstance(hrefs, str):
            return hrefs.split('?')[0]

    def run(self, url=None):
        if url is None:
            url = self.ae_url

        # 清洗链接中的邀请码和注册码，返回纯净的链接
        def href_cleaner(hrefTarget):
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
            Out_flow = ['序号    机场名    官网链接']

            if show:
                data_list = Out_flow + ['【{}】 【{}】 【{}】'.format(i + 1, list(x)[0], list(x)[-1]) for i, x in
                                        enumerate(zip(names, hrefs)) if 'http' in list(x)[-1]]
                # 前端展示API
                return self.show()
            else:
                response_ = [['序号', '机场名', '官网连接'], ] + \
                            [[i + 1, list(x)[0], list(x)[-1]] for i, x in
                             enumerate(zip(names, hrefs)) if 'http' in list(x)[-1]]
                return response_

        func_list = ['[1]查看', '[2]保存', '[3]返回']
        usr_d = easygui.choicebox(title=TITLE, choices=func_list)
        logger_local.info(usr_d)
        if '返回' in usr_d:
            return True

        response = self.handle_html(url)
        if response:
            soup = BeautifulSoup(response, 'html.parser')

            # 定位项目
            items = soup.find_all('li', class_='link-item')

            # 机场名
            names = [item.find('span', class_='sitename').text.strip()
                     for item in items]

            # 获取去除邀请码的机场链接
            hrefs = [item.find('a')['href'] for item in items]
            hrefs = href_cleaner(hrefs)

            if '保存' in usr_d:
                # 保存至本地
                self.response = show_data(show=False)
                self.save()
                # 自动打开
                os.startfile(self.default_path)
            elif '查看' in usr_d:
                # 前端打印
                return show_data()


"""################### 网络审查 ######################"""


class NetChainReview(object):
    def __init__(self):
        self.response = None
        self.s = socket.socket()
        self.s.settimeout(2)

    def run(self):
        test_list = {
            'baidu': ('www.baidu.com', 443),
        }

        try:
            status = self.s.connect_ex(test_list['baidu'])
            if status == 0:
                self.response = True
            else:
                self.response = False
        except socket.error as e:
            self.response = False
        finally:
            self.s.close()
            return self.response


"""################### 版本管理 ######################"""


# FIXME 该模块未完成，请勿调用
class VersionConsole(object):
    def __init__(self):
        self.vcs_res: dict = requests.post(f'http://{API_HOST}:{API_PORT}{ROUTE_API["version_manager"]}',
                                           data={'local_version': version}).json()

    def run(self):

        # 若已有新版本可下载：
        if self.vcs_res.get('need_update'):

            # 判断本地缓冲目录是否有该版本文件
            #       若不存在
            #           尝试：
            #               扫描缓冲目录是否有冲突文件
            #                   若无：启动`update process`守护进程拉取项目文件

            # todo:启动修复程序
            # from config import PLUGIN_UPDATED_MODULE
            # if usr_choice:
            #     os.startfile(PLUGIN_UPDATED_MODULE)

            #           翻车：
            #               回滚操作历史，删除残缺的下载文件
            #       若存在
            #           启动view询问是否更新文件
            #               若更新
            #                   - 关闭主进程
            #                   - 将新版本软件解压到旧版本软件所在目录的上一级目录
            #                   >> 自动打开新版软件 >>
            #                   << 删除旧版本项目文件 <<
            # 若无新版本可下载：退出该模块所在线程

            usr_choice = easygui.ynbox(f'当前版本:{TITLE}'
                                       f'\n\n最新版本：v{self.vcs_res.get("version-server")}'
                                       f'\n\n发现新版本软件！是否更新？',
                                       'v2ray云彩姬安装向导')
        else:
            easygui.msgbox(f'当前版本:{TITLE}'
                           f'\n\n已是最新版本',
                           'v2ray云彩姬安装向导')


"""################### 系统查全 ######################"""


class PrepareEnv(object):
    """环境初始化检测 Please write all initialization functions here"""

    def __init__(self) -> None:
        self.is_new_user = False
        try:

            # 检查默认下载地址是否残缺 深度优先初始化系统文件
            root = [
                ROOT_DIR_PROJECT,
                LOCAL_DIR_LOG,
                LOCAL_DIR_DATABASE, LOCAL_PATH_DATABASE_FH, LOCAL_PATH_DATABASE_YAML,
                LOCAL_DIR_DEPOT, LOCAL_DIR_DEPOT_CLIENT,
            ]
            # TODO:
            #  通过ROOT是否存在来判断该用户是否为新用 --> 加入更多参数断言
            if not os.path.exists(ROOT_DIR_PROJECT):
                self.is_new_user = True

            logger_local.debug("启动<环境检测>模块...")
            for child_ in root:
                if not os.path.exists(child_):
                    logger_local.error(f"系统文件缺失 {child_}")
                    try:
                        logger_local.debug(f"尝试链接系统文件 {child_}")
                        # 初始化文件夹
                        if os.path.isdir(child_) or not os.path.splitext(child_)[-1]:
                            os.mkdir(child_)
                            logger_local.success(f"系统文件链接成功->{child_}")
                        # 初始化文件
                        else:
                            if child_ == LOCAL_PATH_DATABASE_FH:
                                with open(child_, 'w', encoding='utf-8', newline='') as f:
                                    f.writelines(['Time', ',', 'subscribe', ',', '类型', '\n'])
                                logger_local.success(f"系统文件链接成功->{child_}")
                            elif child_ == LOCAL_PATH_DATABASE_YAML:
                                with open(LOCAL_PATH_DATABASE_YAML, 'w', encoding='utf-8') as f:
                                    USER_YAML.update({'path': os.path.abspath('../..')})
                                    yaml.dump(USER_YAML, f, allow_unicode=True)
                                logger_local.success(f"系统文件链接成功->{child_}")

                    except Exception as e:
                        logger_local.exception(e)
        finally:
            logger_local.success("运行环境链接完毕")

    @staticmethod
    def check_update():
        # FIXME:修改这个更新模块，panel无法实现自动更新功能
        def pull_updated_model():
            res = requests.get('https://your_domain/updated.exe')
            with open(PLUGIN_UPDATED_MODULE, 'wb', ) as f:
                f.write(res.content)

        if os.path.basename(PLUGIN_UPDATED_MODULE) not in os.listdir(LOCAL_DIR_DATABASE):
            logger_local.info('pull updated_module')
            ThreadPoolExecutor(max_workers=1).submit(pull_updated_model)
        else:
            ThreadPoolExecutor(max_workers=1).submit(
                VersionConsole().run, True)

    def run(self):

        # 检查版本更新
        self.check_update()

        return rc.test()


"""################### 程序入口 ######################"""


class V2RaycSpiderMasterPanel(object):

    def __init__(self, init=True):

        # 环境初始化
        PrepareEnv()
        # 主菜单
        self.MAIN_HOME_MENU = ['[1]查看机场生态', '[2]获取订阅链接',
                               '[3]打开本地文件', '[4]检查版本更新', '[5]退出', ]

        # air_port_menu
        self.AIRPORT_HOME_MENU = ['[1]白嫖机场',
                                  '[2]高端机场', '[3]机场汇总', '[4]返回', '[5]退出']
        self.AIRPORT_FUNCTION_MENU = ['[1]查看', '[2]保存', '[3]返回']
        self.airHome = 'https://52bp.org'

        # 根据配置信息自动选择采集模式
        self.SSR_HOME_MENU = ['[1]V2Ray订阅链接', '[2]SSR订阅链接', '[3]Trojan订阅连接', '[4]查询可用链接', '[5]返回',
                              '[6]退出']

    @staticmethod
    def kill():
        try:
            rc.kill()
        except Exception as e:
            logger_local.exception(e)

    @staticmethod
    def debug(info):
        logger_local.debug(info)

    def home_menu(self):
        """主菜单"""
        # ['[1]查看机场生态', '[2]获取订阅链接', '[3]检查版本更新', '[4]退出', ]
        resp = True
        usr_c = easygui.choicebox(
            '功能列表', TITLE, self.MAIN_HOME_MENU, preselect=1)
        logger_local.info(usr_c)
        try:
            if '[1]查看机场生态' in usr_c:
                resp = self.air_port_menu()
            elif '[2]获取订阅链接' in usr_c:
                resp = self.ssr_spider_menu()
            elif '[3]打开本地文件' in usr_c:
                os.startfile(LOCAL_PATH_DATABASE_FH)
                resp = False
            elif '更新' in usr_c:
                ThreadPoolExecutor(max_workers=1).submit(VersionConsole().run)
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
        usr_c = easygui.choicebox(
            '功能列表', TITLE, self.AIRPORT_HOME_MENU, preselect=0)
        logger_local.info(usr_c)
        resp = True
        try:
            if '[4]返回' in usr_c:
                resp = True
            else:
                resp = AirEcologySpider(type=usr_c).run()
        except TypeError:
            resp = True
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
        # process_locker()
        ProcessZeus().process_locker()
        resp = True
        # UI功能选择
        usr_c = easygui.choicebox(
            '功能列表', TITLE, self.SSR_HOME_MENU, preselect=1)
        logger_local.info(usr_c)
        sp = SubscribeRequester()
        try:
            if '[1]V2Ray订阅链接' in usr_c:
                resp = sp.run(mode='v2ray')
            elif '[2]SSR订阅链接' in usr_c:
                resp = sp.run(mode='ssr')
            elif '[3]Trojan订阅连接' in usr_c:
                resp = sp.run(mode='trojan')
            elif '[4]查询可用链接' in usr_c:
                resp = sp.find_aviLink()
            elif '[5]返回' in usr_c:
                resp = True
            else:
                resp = False
        except TypeError:
            resp = True
        finally:
            return resp


# --------------------------------
# 权限验证
# --------------------------------
if ThreadPoolExecutor(max_workers=1).submit(NetChainReview().run).result():
    rc = RedisClient()
else:
    logger_local.warning('网络异常')
    easygui.msgbox('网络异常', title=TITLE)
    exit()
