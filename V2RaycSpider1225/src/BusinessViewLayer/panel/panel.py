__all__ = ["V2RaycSpiderMasterPanel", "PrepareEnv"]

import csv
import socket
import sys
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from urllib.parse import urlparse
from uuid import uuid4

import easygui
import pyperclip
import redis
import requests
import yaml
from bs4 import BeautifulSoup

from src.BusinessViewLayer.panel.config_panel import *

"""################### 数据库管理 ######################"""


class RedisClientPanel(object):
    def __init__(self):
        self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True,
                                    db=REDIS_DB)
        self.subscribe = ''

    def get_driver(self) -> redis.StrictRedis:
        return self.db

    def get(self, key_name, pop_=0) -> str or bool:
        """

        :param key_name:
        :param pop_:
        :return:
        """
        while True:
            target_raw: dict = self.db.hgetall(key_name)
            try:
                self.subscribe, end_life = list(target_raw.items()).pop(pop_)
                # 订阅连接到期时间 -> datetime
                subs_end_time = datetime.fromisoformat(end_life)
                # 上海时区 -> datetime
                now_time = datetime.fromisoformat(str(datetime.now(TIME_ZONE_CN)).split('.')[0])
                # 时间比对 判断是否过期的响应 -> bool
                is_stale = False if subs_end_time > now_time + timedelta(hours=3) else True
                if is_stale:
                    continue
                else:
                    return self.subscribe
            except IndexError:
                return False
            finally:
                try:
                    # 清洗出订阅中的token
                    token = urlparse(self.subscribe).path
                    # 遍历所有任务类型
                    for task in ['v2ray', 'ssr']:
                        # 遍历某种类型的链接池
                        for sub in self.db.hgetall(REDIS_SECRET_KEY.format(task)).items():
                            # 匹配用户token
                            if token == urlparse(sub[0]).path:
                                # 若节拍同步，立即移除订阅
                                self.db.hdel(REDIS_SECRET_KEY.format(task), sub[0])
                except Exception as e:
                    print(e)


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
                    "请勿频繁请求！\n\n"
                    f'本机IP已被冻结 {str(self.unlock_time - datetime.now()).split(".")[0]}'
                    f" 可在本地文件中查看访问记录\n\n"
                    f'解封时间:{str(self.unlock_time).split(".")[0]}',
                    title=TITLE,
                    choices=["[1]确定", "[2]返回"],
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
        with open(LOCAL_PATH_DATABASE_FH, "r", encoding="utf-8") as f:
            date_ = [
                j.split(",")[0] for j in [i.strip() for i in f.readlines()] if j
            ].pop()
            if "-" not in date_:
                self.stale_res_time = False
            else:
                self.stale_res_time = datetime.fromisoformat(date_)


"""################### 官能团 ######################"""


class SubscribeRequester(object):
    """内嵌微型爬虫-订阅链接请求"""

    def __init__(self):
        # 启动GUI
        # self.Home()

        self.subscribe = ""

    @staticmethod
    def save_flow(data_flow="N/A", class_=""):
        with open(LOCAL_PATH_DATABASE_FH, "a", encoding="utf-8") as f:
            now_ = str(datetime.now()).split(".")[0]
            f.writelines([now_, ",", data_flow.strip(), ",", class_, "\n"])

    def find_available_subscribe(self):
        """
        查询池状态
        :return:
        """

        def search(redis_driver) -> list:
            target_list = []
            for task_type in ["v2ray", "ssr", "trojan"]:
                # List[Tuple[subs,end_life]]
                target = list(
                    redis_driver.hgetall(REDIS_SECRET_KEY.format(task_type)).items()
                )
                # end_life, class_, subs
                # 过期时间， 订阅类型， 订阅链接
                target_list += [
                    "".center(2, " ").join([i[-1], f"{task_type}", i[0]])
                    for i in target
                ]
            return target_list

        avi_info = search(rc.get_driver())

        avi2id = dict(zip([str(uuid4()) for _ in range(len(avi_info))], avi_info))

        temp_info = [
            "{}  {}  {}".format(i[-1].split("  ")[0], i[-1].split("  ")[1], i[0])
            for i in avi2id.items()
        ]

        avi_info = [
                       "".center(2, " ").join(["过期时间", "订阅类型", "订阅链接"]),
                   ] + temp_info

        usr_choice = easygui.choicebox(
            msg="注:审核标准为北京时区；点击获取，链接自动复制", title=TITLE, choices=avi_info, preselect=1
        )

        logger_local.info(usr_choice)
        if "-" in usr_choice:
            task_name, subscribe = (
                usr_choice.split("  ")[1],
                avi2id[usr_choice.split("  ")[-1]].split("  ")[-1],
            )
            self.resp_tip(subscribe, task_name)
            rc.get_driver().hdel(REDIS_SECRET_KEY.format(task_name), subscribe)
        elif "过期时间" in usr_choice:
            logger_local.warning("链接选择错误")
            easygui.msgbox("请选择有效链接", TITLE)
            self.find_available_subscribe()

        # 返回上一页
        return True

    def resp_tip(self, subscribe: str, task_name):
        """

        :param task_name: 任务类型：ssr ； v2ray;trojan
        :param subscribe: 订阅链接
        :return:
        """
        # 公示分发结果
        if subscribe.strip():
            easygui.enterbox(msg="获取成功，点击确定自动复制链接", title=TITLE, default=subscribe)
        try:
            # 获取成功
            if "http" in subscribe:
                logger_local.success("GET--{}".format(subscribe))
                # 自动复制
                pyperclip.copy(subscribe)
                # 将数据存入本地文件
                self.save_flow(subscribe, task_name)
            # 获取异常
            else:
                logger_local.critical("SubscribeGetException")
                easygui.exceptionbox(
                    title=TITLE,
                    msg="SNI:V_{}".format(str(datetime.now()).split(" ")[0])
                        + "\n\n请将V2Ray云彩姬更新至最新版本!"
                          "\n\n项目地址:https://github.com/QIN2DIM",
                )
                subscribe = requests.get(
                    "https://t.qinse.top/subscribe/{}.txt".format(task_name)
                ).text
                easygui.enterbox(
                    msg=f"点击获取{task_name}备用链接", title=TITLE, default=subscribe
                )
                # 自动复制
                pyperclip.copy(subscribe)
                # 将数据存入本地文件
                self.save_flow(subscribe, task_name)
        finally:
            # 返回上一页
            return True

    def run(self, mode: str):
        """
        mode: ssr,v2ray,trojan
        work_interface:

        """

        try:
            self.subscribe = rc.get(REDIS_SECRET_KEY.format(mode))
        finally:
            return self.resp_tip(self.subscribe, mode)


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
        self.ae_task = "https://52bp.org/{}"

        if "高端" in kwargs.get("type", "none"):
            self.ae_url = self.ae_task.format("vip-airport.html")
        elif "白嫖" in kwargs.get("type", "none"):
            self.ae_url = self.ae_task.format("free-airport.html")
        else:
            self.ae_url = self.ae_task.format("airport.html")

    def show(self):
        usr_c = easygui.choicebox(
            msg="选中即可跳转目标网址,部分机场需要代理才能访问", title=TITLE, choices=self.data_list
        )
        logger_local.info(usr_c)
        if usr_c:
            if "http" in usr_c:
                url = usr_c.split(" ")[-1][1:-1]
                webbrowser.open(url)
            else:
                logger_local.warning("机场网址失效或操作有误")
                easygui.msgbox("机场网址失效或操作有误", title=TITLE, ok_button="返回")
                self.show()
        elif usr_c is None:
            return "present"

    def save(self, data_flow=None, default_path=None):
        if data_flow is None:
            data_flow = self.response
        if default_path is None:
            default_path = LOCAL_PATH_AIRPORT_INFO
        try:
            with open(default_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for x in data_flow:
                    writer.writerow(x)
            logger_local.info("机场生态信息保存")
        except PermissionError as e:
            logger_local.exception(e)
            easygui.exceptionbox("核心文件被占用:{}".format(default_path))
            default_path = os.path.join(
                easygui.diropenbox(msg="选择存储目录", title=TITLE),
                os.path.basename(LOCAL_PATH_AIRPORT_INFO),
            )
            self.save(data_flow=data_flow, default_path=default_path)
        finally:
            self.default_path = default_path
            return default_path

    @staticmethod
    def handle_html(url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            return res.text
        except requests.exceptions.ProxyError:
            easygui.exceptionbox("请关闭系统代理后使用此功能！", TITLE)
            logger_local.warning("请关闭系统代理后使用此功能！")
            return False
        except Exception as e:
            logger_local.exception(e)
            return False

    def parse_html(self, response):
        soup = BeautifulSoup(response, "html.parser")

        # 定位项目
        items = soup.find_all("li", class_="link-item")
        # 获取去除邀请码的机场链接
        hrefs = [item.find("a")["href"] for item in items]
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
                if "?" in href:
                    href = href.split("?")[0]
                    clean_href.append(href)
                else:
                    clean_href.append(href)
            return clean_href

        elif isinstance(hrefs, str):
            return hrefs.split("?")[0]

    def show_data(self, show=True, names: list = None, hrefs: list = None):

        if show:
            # 使用全局变量输出前端信息
            out_flow = ["序号    机场名    官网链接"]
            self.data_list = out_flow + [
                "【{}】 【{}】 【{}】".format(i + 1, list(x)[0], list(x)[-1])
                for i, x in enumerate(zip(names, hrefs))
                if "http" in list(x)[-1]
            ]
            # 前端展示API
            return self.show()
        else:
            response_ = [["序号", "机场名", "官网连接"], ] + [
                [i + 1, list(x)[0], list(x)[-1]]
                for i, x in enumerate(zip(names, hrefs))
                if "http" in list(x)[-1]
            ]
            return response_

    def run(self, url=None):
        if url is None:
            url = self.ae_url
        func_list = ["[1]查看", "[2]保存", "[3]返回"]
        usr_choice = easygui.choicebox(title=TITLE, choices=func_list)
        logger_local.info(usr_choice)
        if "返回" in usr_choice:
            return True

        response = self.handle_html(url)
        if response:
            # 定位项目
            items = BeautifulSoup(response, "html.parser").find_all("li", class_="link-item")
            # 机场名
            names = [item.find("span", class_="sitename").text.strip() for item in items]
            # 获取去除邀请码的机场链接
            hrefs = [item.find("a")["href"] for item in items]
            hrefs = self.href_cleaner(hrefs)
            if "保存" in usr_choice:
                self.response = self.show_data(show=False, names=names, hrefs=hrefs)
                self.save()
                os.startfile(self.default_path)
            elif "查看" in usr_choice:
                return self.show_data(show=True, names=names, hrefs=hrefs)


class WalkingOnThinIce(object):
    """垂直挖掘——采集、脱敏、优选、分发全网节点订阅源"""

    def __init__(self):
        pass


class GardenerSystem(object):
    """园丁系统——低代码实现的永久订阅模型"""

    def __init__(self):
        pass


class Icebreaker(object):
    """破冰船——利用分布式终端代理实现混淆神经网络（ONN）"""

    def __init__(self):
        pass


"""################### 网络审查 ######################"""


class NetChainReview(object):
    def __init__(self):
        self.response = None
        self.s = socket.socket()
        self.s.settimeout(2)

    def run(self):
        test_list = {
            "baidu": ("www.baidu.com", 443),
        }

        try:
            status = self.s.connect_ex(test_list["baidu"])
            if status == 0:
                self.response = True
            else:
                self.response = False
        except socket.error:
            self.response = False
        finally:
            self.s.close()
            return self.response


"""################### 版本管理 ######################"""


class VersionConsole(object):
    def __init__(self):
        self.vcs_res: dict = {}

    @staticmethod
    def dev_update():
        usr_choice = easygui.ynbox(
            f"当前版本:{TITLE} v{version}-dev "
            f"\n\n开发版不提供自动更新通道，请关注项目动态"
            f"\n\n{GITHUB_PROJECT}",
            "v2ray云彩姬安装向导",
            choices=['Redirect', 'Cancel']
        )
        if usr_choice:
            webbrowser.open(GITHUB_PROJECT)
        return True

    def release_update(self):
        """

        :return:
        """


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
                LOCAL_DIR_DATABASE,
                LOCAL_PATH_DATABASE_FH,
                LOCAL_PATH_DATABASE_YAML,
                LOCAL_DIR_DEPOT,
                LOCAL_DIR_DEPOT_CLIENT,
            ]
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
                                with open(
                                        child_, "w", encoding="utf-8", newline=""
                                ) as f:
                                    f.writelines(
                                        ["Time", ",", "subscribe", ",", "类型", "\n"]
                                    )
                                logger_local.success(f"系统文件链接成功->{child_}")
                            elif child_ == LOCAL_PATH_DATABASE_YAML:
                                with open(
                                        LOCAL_PATH_DATABASE_YAML, "w", encoding="utf-8"
                                ) as f:
                                    USER_YAML.update({"path": os.path.abspath("../..")})
                                    yaml.dump(USER_YAML, f, allow_unicode=True)
                                logger_local.success(f"系统文件链接成功->{child_}")

                    except Exception as e:
                        logger_local.exception(e)
        finally:
            logger_local.success("运行环境链接完毕")


"""################### 程序入口 ######################"""


class V2RaycSpiderMasterPanel(object):
    def __init__(self):
        # 主菜单
        self.main_home_menu = [
            "[1]查看机场生态",
            "[2]获取订阅链接",
            "[3]打开本地文件",
            "[4]检查版本更新",
            "[5]退出",
        ]
        # 机场生态首页
        self.airport_home_menu = [
            "[1]白嫖机场",
            "[2]高端机场",
            "[3]机场汇总",
            "[4]返回",
            "[5]退出"
        ]
        # 机场生态内页
        self.airport_function_menu = [
            "[1]查看",
            "[2]保存",
            "[3]返回"
        ]
        # 根据配置信息自动选择采集模式
        self.ssr_home_menu = [
            "[1]V2Ray订阅链接",
            "[2]SSR订阅链接",
            "[3]查询可用链接",
            # "[4]园丁模式",
            # "[5]垂直挖掘模式",
            # "[6]破冰船一键代理",
            "返回",
            "退出",
        ]

    def home_menu(self):
        """主菜单"""
        # ----------------------------------------
        # UI功能选择
        # ----------------------------------------
        resp = True
        usr_choice: str = easygui.choicebox("功能列表", TITLE, self.main_home_menu, preselect=1)
        logger_local.info(usr_choice)
        try:
            if usr_choice.startswith("[1]查看机场生态"):
                resp = self.air_port_menu()
            elif usr_choice.startswith("[2]获取订阅链接"):
                resp = self.subs_require_menu()
            elif usr_choice.startswith("[3]打开本地文件"):
                os.startfile(LOCAL_PATH_DATABASE_FH)
                resp = False
            elif usr_choice.startswith("[4]检查版本更新"):
                ThreadPoolExecutor(max_workers=1).submit(VersionConsole().dev_update)
            else:
                resp = False
        except TypeError:
            # 若出现未知异常，强制退出
            resp = False
        finally:
            if resp:
                self.home_menu()
            else:
                sys.exit()

    def air_port_menu(self):
        """air_port_menu GUI导航"""
        # ----------------------------------------
        # UI功能选择
        # ----------------------------------------
        usr_c = easygui.choicebox("功能列表", TITLE, self.airport_home_menu, preselect=0)
        logger_local.info(usr_c)
        resp = True
        try:
            if "[4]返回" in usr_c:
                resp = True
            else:
                resp = AirEcologySpider(type=usr_c).run()
        except TypeError:
            resp = True
        finally:
            return resp

    def subs_require_menu(self):
        """
        一级菜单
        :mode: True:本地采集，False 服务器采集
        :return:
        """
        # ----------------------------------------
        # 初始化进程冻结锁
        # ----------------------------------------
        ProcessZeus().process_locker()
        resp = True
        # ----------------------------------------
        # UI功能选择
        # ----------------------------------------
        usr_c: str = easygui.choicebox("功能列表", TITLE, self.ssr_home_menu, preselect=1)
        logger_local.info(usr_c)
        sr = SubscribeRequester()
        try:
            if "[1]V2Ray订阅链接" in usr_c:
                resp = sr.run(mode="v2ray")
            elif "[2]SSR订阅链接" in usr_c:
                resp = sr.run(mode="ssr")
            elif "[3]查询可用链接" in usr_c:
                resp = sr.find_available_subscribe()
            elif "[4]园丁模式" in usr_c:
                resp = GardenerSystem()
            elif "返回" in usr_c:
                resp = True
            else:
                resp = False
        except TypeError:
            resp = True
        finally:
            return resp


"""################### 启动检测 ######################"""
try:
    # 运行环境初始化
    PrepareEnv()
    # 握手检测
    if ThreadPoolExecutor(max_workers=1).submit(NetChainReview().run).result():
        rc = RedisClientPanel()
    else:
        logger_local.warning("网络异常")
        easygui.msgbox("网络异常", title=TITLE)
        exit()
except Exception as et:
    # Tcl_AsyncDelete: async handler deleted by the wrong thread ?
    easygui.exceptionbox(str(et))

if __name__ == '__main__':
    V2RaycSpiderMasterPanel().home_menu()
