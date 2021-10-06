from urllib.parse import urlparse

from gevent import monkey

monkey.patch_all(thread=False)
import csv
import hashlib
import os
import platform
import random
import shutil
import socket
import sys
import threading
import time
import webbrowser
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import List, Tuple

import PySimpleGUI as sg
import colorama
import easygui
import gevent
import pyperclip
import redis
import requests
import yaml
from bs4 import BeautifulSoup
from gevent.queue import Queue
from retry import retry

from .flag import PANEL_VERSION_ID_CURRENT
from .setting import logger, TIME_ZONE_CN, BAND_BATCH, REDIS_SECRET_KEY, \
    REDIS_DB, REDIS_PORT, REDIS_HOST, REDIS_PASSWORD, PROTOCOL_FLAG, PRE_CLEANING_TIME, DIR_DATABASE, \
    DIR_DEFAULT_DOWNLOAD, PATH_FETCH_REQUESTS_HISTORY, PATH_FETCH_AIR_ECOLOGY, PATH_SETTING_YAML, DEFAULT_ADAPTOR, \
    TITLE

# PySimpleGUI 的主题
sg.theme("Reddit")
PROGRESS_METER_TITLE = "VulcanAsh Monitor"

# 进度条颜色主动恢复 兼容Windows工作台
colorama.init(autoreset=True)

# 用于传递机场生态的全局变量
_memory_docker_of_small_spider: dict = {}

# 获取的latest release版本信息
_memory_docker_of_version_control: dict = {}

# 协程任务工作核心数
_kernel_size: int = 8

# 用于协程任务的全局监控
_done_work = Queue()
_max_queue_size = -1

rdb_object = None


class ToolBox:
    @staticmethod
    def reset_rdb_object():
        global rdb_object
        rdb_object = RedisClientIO()

    @staticmethod
    def printer_log(msg: str, status: int):

        print(f"[{str(datetime.now()).split('.')[0]}]", end=' ')
        if status == 1:
            print(colorama.Fore.GREEN + "[✓]", end=' ')
        elif status == 0:
            print(colorama.Fore.RED + "[×]", end=' ')
        elif status == 2:
            print(colorama.Fore.BLUE + "[...]", end=' ')
        print(msg)

    @staticmethod
    def prepare_environment():
        # Definition: ~/database nonFetch.First project creation.
        if not os.path.exists(DIR_DATABASE):
            # create database.
            os.mkdir(DIR_DATABASE)

        # Definition: ~/client nonFetch.First project creation.
        if not os.path.exists(DIR_DEFAULT_DOWNLOAD):
            os.mkdir(DIR_DEFAULT_DOWNLOAD)

        # Create .txt for writing history of requester.
        if not os.path.exists(PATH_FETCH_REQUESTS_HISTORY):
            with open(PATH_FETCH_REQUESTS_HISTORY,
                      "w",
                      encoding="utf-8",
                      newline="") as f:
                f.writelines(["Time", ",", "subscribe", ",", "类型", "\n"])

        # Create .yaml for writing critical startup parameters of panel.
        dark = {
            "version": PANEL_VERSION_ID_CURRENT,
            "latest_startup_path": os.path.dirname(__file__)
        }
        if os.path.exists(PATH_SETTING_YAML):
            with open(PATH_SETTING_YAML, "r", encoding="utf8") as f:
                data = yaml.safe_load(f.read())
                dark.update(data)
        else:
            with open(PATH_SETTING_YAML, "w", encoding="utf8") as f:
                yaml.dump(dark, f, allow_unicode=True)

    @staticmethod
    def create_shortcut(filename, shortcut_name):
        pass

    @staticmethod
    def parse_enhance_sha256(message: str) -> str:
        return hashlib.sha256(bytes(message, "utf8")).hexdigest()

    @staticmethod
    def delete_cache(flag_filename: str):
        """

        :param flag_filename: 递归删除的目标文件夹
        :return:
        """
        try:
            ToolBox.printer_log("Clearing cache", 2)
            shutil.rmtree(flag_filename)
            ToolBox.printer_log("Clearing cache", 1)
        except FileNotFoundError:
            ToolBox.printer_log("Clearing cache", 0)

    @staticmethod
    def fix_garbled(unzip_object: str):
        """
        修复 unzip 解压输出的 云彩姬.exe 中文乱码问题。并不会直接覆盖，而是返回标记。
        请尽量使用英文文件名，减轻开发压力
        :param unzip_object: 需要检查乱码问题的文件目录
        :return: response = {'std': "", "garbled": ""}
        """
        # std 标准输出编码，garbled 原先的乱码文件名
        response = {'std': "", "garbled": ""}

        ToolBox.printer_log("Fixing Chinese garbled characters", 2)
        for obj_ in os.listdir(unzip_object):
            if obj_.endswith('.exe'):
                std_name = obj_.encode("cp437").decode("gbk")
                if "云彩姬" in std_name:
                    response['std'] = std_name
                    response['garbled'] = obj_
                    break
        ToolBox.printer_log("Fix successfully.", 1)

        return response

    @staticmethod
    def unzip_file(zip_object: str,
                   unzip_object: str = None,
                   auto_fix: bool = False):
        """
        解压文件
        :param zip_object: 定位解压文件
        :param unzip_object: 解压输出目录，默认输出到解压文件所在目录
        :param auto_fix: 自动扫描输出目录的乱码文件并修复
        :return:
        """
        unzip_object = os.path.dirname(
            zip_object) if unzip_object is None else unzip_object

        if not os.path.exists(unzip_object):
            os.mkdir(unzip_object)

        # 开始解压文件
        ToolBox.printer_log(f"Unzip files --> {zip_object}", 2)
        with zipfile.ZipFile(zip_object) as z:
            z.extractall(unzip_object)
        ToolBox.printer_log(f"Unzip successfully --> {unzip_object}", 1)

        # 扫描乱码
        if auto_fix:
            return ToolBox.fix_garbled(unzip_object)
        return unzip_object

    @staticmethod
    def preload_cache(cache_file: str, add_block: str):
        """
        创建缓存目录，可传入一个尚未被创建的路径，函数自动检测并构建
        :param add_block: 需要新建的缓存块
        :param cache_file: 缓存块所在路径
        :return:
        """
        # 拼接路径
        cache_block = os.path.join(cache_file, add_block)
        # 自动构建
        if not os.path.exists(cache_block):
            os.mkdir(cache_block)
        return cache_block


"""################### 数据库管理 ######################"""


class RedisClientIO:
    def __init__(self):
        self.db = redis.StrictRedis(host=REDIS_HOST,
                                    port=REDIS_PORT,
                                    password=REDIS_PASSWORD,
                                    decode_responses=True,
                                    db=REDIS_DB)

    # --------------------
    # Private API
    # --------------------
    def _update_api_status(self, api_name):
        if api_name not in [
                'select', 'get', 'search', 'decouple', 'reset', 'get-cli'
        ]:
            return False
        date_format = str(datetime.now(TIME_ZONE_CN))
        self.db.rpush(f"v2rayc_apis:{api_name}", date_format)
        self.db.incr(f"v2rayc_apis:{api_name}_num")

    # --------------------
    # Public API
    # --------------------
    def sync_remain_subs(self, key_name) -> List[Tuple]:
        return list(self.db.hgetall(REDIS_SECRET_KEY.format(key_name)).items())

    def sync_detach_subs(self, key_name, subscribe):
        self.db.hdel(REDIS_SECRET_KEY.format(key_name), subscribe)
        self._update_api_status('get-cli')

    def upload_stream_for_gardener(self, uid, nodes):
        self.db.hmset(f"v2rayc_gardener:{uid}",
                      dict(zip(nodes, [
                          "1",
                      ] * len(nodes))))

    def quick_get(self, key_name) -> str:

        stream_tag = self.sync_remain_subs(key_name)

        if stream_tag is None:
            return ""

        for subscribe, end_life in reversed(stream_tag):
            try:
                # 订阅连接到期时间 -> datetime(上海时区)
                subs_end_time = datetime.fromisoformat(end_life)
                # 上海时区 -> datetime
                now_time = datetime.fromisoformat(
                    str(datetime.now(TIME_ZONE_CN)).split('.')[0])
                # 时间比对 判断是否过期的响应 -> bool
                is_stale = not subs_end_time > now_time + timedelta(
                    hours=PRE_CLEANING_TIME)
                # 返回具备足够合理的可用时长的订阅
                if not is_stale:
                    return subscribe
            finally:
                ThreadPoolExecutor(max_workers=1).submit(self.sync_detach_subs,
                                                         key_name=key_name,
                                                         subscribe=subscribe)

    def get_alias(self) -> dict:
        return self.db.hgetall("v2rss:alias")


"""################### 进程管理 ######################"""


class ProcessZeus:
    def __init__(self) -> None:

        # 进程锁状态
        self.status_lock: bool = True

        # 初始化解锁时间
        self.unlock_time = datetime.now() + timedelta(seconds=BAND_BATCH)

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
                self.unlock_time = self.stale_res_time + timedelta(
                    seconds=BAND_BATCH)
                # 操作过热则冻结主进程
                self.status_lock = self.unlock_time > datetime.now()
        except (FileExistsError, PermissionError, FileNotFoundError,
                ValueError) as e:
            logger.exception(e)

    def loads_stale_time(self) -> None:
        # FIXME:
        #  这个模块有bug，需要进一步精确锁死方案，当前方案当文件进程被占用就会失效
        with open(PATH_FETCH_REQUESTS_HISTORY, "r", encoding="utf-8") as f:
            date_ = [
                j.split(",")[0] for j in [i.strip() for i in f.readlines()]
                if j
            ].pop()
            if "-" not in date_:
                self.stale_res_time = False
            else:
                self.stale_res_time = datetime.fromisoformat(date_)


"""################### 协程核心 ######################"""


class CoroutineEngine:
    def __init__(self,
                 work_q: Queue = None,
                 task_docker=None,
                 done_work: Queue = None,
                 progress_meter_title: str = "VulcanAsh Monitor",
                 use_global_monitor=None):
        # 任务容器：queue
        self.work_q = work_q if work_q else Queue()
        # 任务容器：迭代器
        self.task_docker = task_docker
        # 任务队列满载时刻长度
        self.max_queue_size = 0
        # 下载进度监控头
        self.progress_meter_title = progress_meter_title
        # 已完成的任务标记
        self.done_work = _done_work if done_work is None else done_work
        self.use_global_monitor = use_global_monitor

    def update_status_of_global_monitor(self, flow: str):
        global _max_queue_size
        if flow == "offload":
            _max_queue_size = self.max_queue_size
        elif flow == "ace-agent":
            self.done_work.put_nowait(1)
        elif flow == "kill":
            _max_queue_size = 0
            while not self.done_work.empty():
                self.done_work.get_nowait()

    def launch(self):
        while not self.work_q.empty():
            task_information = self.work_q.get_nowait()
            self.ace_agent(task_information)

    def ace_agent(self, task):
        pass

    def offload_task(self):
        if self.work_q.empty() and self.task_docker:
            for task in self.task_docker:
                self.work_q.put_nowait(task)
        self.max_queue_size = self.work_q.qsize()

        self.update_status_of_global_monitor("offload")

    def killer(self):
        pass

    def flexible_power(self, power):
        return self.max_queue_size if power > self.max_queue_size else power

    def go(self, power: int = 8):
        # 任务重载
        self.offload_task()
        # 配置弹性采集功率
        power = self.flexible_power(power)
        # 任务启动
        task_list = []
        for _ in range(power):
            task = gevent.spawn(self.launch)
            task_list.append(task)
        gevent.joinall(task_list)
        # 缓存回收
        self.killer()


class DownloaderBR(CoroutineEngine):
    """(断点续传版本)基于协程的下载器 用于加速release文件的拉取"""
    def __init__(self, workspace: str, filename: str, parameters: list):
        """

        :param workspace: 下载器工作的目录
        :param filename: 压缩包名 basename
        :param parameters: 下载器配置参数
        """
        super(DownloaderBR, self).__init__(
            task_docker=parameters,
            done_work=_done_work,
            progress_meter_title=PROGRESS_METER_TITLE,
        )

        # X.zip.download.Y
        self.filename = filename
        self.workspace = workspace

        self.cache_label = ".download."
        self.merge_label = ".download.merge"

        self.cache_block = f"{self.filename}{self.cache_label}" + "{}"
        self.merge_object = f"{self.filename}{self.merge_label}"

        # self.breakpoint_ = self.check_workspace(self.workspace)

    def check_workspace(self, workspace, task_id=None):
        breakpoint_ = {}

        if task_id is None:
            for block in os.listdir(workspace):
                if block.startswith(f"{self.filename}{self.cache_label}"
                                    ) and not block.endswith(self.merge_label):
                    block_path = os.path.join(workspace, block)
                    block_size = os.path.getsize(block_path)
                    block_id = block.split('.')[-1]
                    breakpoint_[str(block_id)] = {
                        "size": block_size,
                        "path": block_path
                    }
        else:
            block_path = os.path.join(workspace,
                                      self.cache_block.format(task_id))
            if os.path.exists(block_path):
                block_size = os.path.getsize(block_path)
                breakpoint_[str(task_id)] = {
                    "size": block_size,
                    "path": block_path
                }
        return breakpoint_

    @retry(
        tries=3,
        delay=1,
    )
    def ace_agent(self, task):

        # ------------------------------------
        # preload
        # ------------------------------------
        headers = task.get("headers").copy()
        boundary = task.get('task_boundary')
        task_id = task.get("task_id")

        # breakpoint_ = self.check_workspace(self.workspace, task_id).get(task_id)
        # if breakpoint_:
        #     heart_flow = breakpoint_['size']
        #     block_path = breakpoint_['path']
        #     if boundary[0] + heart_flow < boundary[-1]:
        #         boundary[0] += + heart_flow
        #     else:
        #         os.remove(block_path)
        headers['Range'] = f"bytes={boundary[0]}-{boundary[-1]}"
        # ------------------------------------
        # pull
        # ------------------------------------

        session = task.get("session")
        url = task.get("download_url")
        res: requests.Response = session.get(url, headers=headers, stream=True)

        cache_block_name = self.cache_block.format(task_id)
        cache_block_path = os.path.join(self.workspace, cache_block_name)
        with open(cache_block_path, "wb") as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        ToolBox.printer_log(
            f"DownloaderBR | heart_flow --> {cache_block_name} [{boundary[0]}-{boundary[-1]}]",
            1)

        self.update_status_of_global_monitor("ace-agent")

    def killer(self):
        # ~/client/cache/version_id/
        cache_blocks = [
            i for i in os.listdir(self.workspace) if self.cache_label in i
        ]
        # ~/client/cache/version_id/.zip.download.merge
        merge_object = os.path.join(self.workspace, self.merge_object)
        # ~/client/cache/version_id/.zip
        response_object = os.path.join(self.workspace, self.filename)

        merge_file = open(merge_object, "wb")

        try:
            for block in cache_blocks:
                block_path = os.path.join(self.workspace, block)
                ToolBox.printer_log(f"DownloaderBR | merge -->{block_path}", 1)
                with open(block_path, 'rb') as f:
                    stream = f.read()
                merge_file.write(stream)
        finally:
            merge_file.close()

        # .download.merge --> .zip
        if os.path.exists(response_object):
            os.remove(response_object)
        os.rename(merge_object, response_object)

        self.update_status_of_global_monitor("kill")


"""################### 版本管理 ######################"""


class PanelVersionControl:
    def __init__(self):
        # 访问此API不需要过墙
        self.REPO_RELEASE_API = "https://api.github.com/repos/QIN2DIM/V2rayCloudSpider/releases"
        # 直连拉取需要过墙
        self.REPO_RELEASE_HTML = "https://github.com/QIN2DIM/V2rayCloudSpider/releases"
        # 区分用户系统
        self.FLAG_PLATFORM = {
            'Windows': "Windows",
            "Linux": "Linux",
            "Darwin": "MacOS"
        }
        self.FLAG_NAME = self.FLAG_PLATFORM[platform.system()]

        # 同步仓库特性
        self.RELEASE_DESC = self.sync_repo_release()

    def sync_repo_release(self) -> dict:

        proxy_ = {'http': None, "https": None}
        headers = {
            'Content-Type': 'application/json',
        }

        res = requests.get(self.REPO_RELEASE_API,
                           proxies=proxy_,
                           headers=headers)

        release_trace = res.json()

        # get latest release project
        ToolBox.printer_log(release_trace, 2)
        data: dict = release_trace[0]

        return {
            'version_id': data.get("tag_name"),
            'name': data.get("name"),
            'is_prerelease': ".prerelease" if data.get("prerelease") else "",
            "publish_time": self.std_time(data.get("published_at")),
            'sketch': data.get("body"),
            'latest_packages': data.get("assets"),
            "status": release_trace,
            "tag2time": {
                release_['tag_name']: self.std_time(release_['published_at'])
                for release_ in release_trace
            }
        }

    @staticmethod
    def std_time(repo_time) -> datetime:
        return datetime.fromisoformat(
            repo_time.replace("T", " ").replace("Z", ""))

    def is_need_to_update(self) -> dict:
        # 因部分分支版本号规则较为混乱，单纯比较版本id的方法确认是否有版本更新不可靠
        new_t = self.RELEASE_DESC["publish_time"]
        # 防止版本游离，作者手动删除分支，或历史遗留问题导致的版本错乱
        old_t = self.RELEASE_DESC["tag2time"].get(
            f"v{PANEL_VERSION_ID_CURRENT}")
        # 当版本游离时，无法自动化拉取更新，需要用户自行判断是否有版本更新（提示最新版本特性），到github中下载
        return {
            "datetime_of_latest_release": new_t,
            "datetime_of_my_panel": old_t,
            "result": new_t > old_t if old_t else None
        }

    def parse_download_url(self):
        latest_packages = self.RELEASE_DESC.get("latest_packages")
        for package_ in latest_packages:
            if self.FLAG_NAME in package_['name']:
                self.RELEASE_DESC.update({
                    "download_url":
                    package_.get("browser_download_url"),
                    "latest_change_time":
                    self.std_time(package_.get("updated_at")),
                    "size-info":
                    f"{round(float(package_.get('size')) / 1024 ** 2, 2)}MB",
                    "size":
                    package_.get('size')
                })
                break


"""################### 顶层设计 ######################"""


class SubscribeRequester:
    """内嵌微型爬虫-订阅链接请求"""
    def __init__(self):
        # 启动GUI
        # self.Home()

        self.subscribe = ""
        if rdb_object is None:
            self.rc = RedisClientIO()
        else:
            self.rc = rdb_object

    @staticmethod
    def save_flow(data_flow="N/A", class_=""):
        with open(PATH_FETCH_REQUESTS_HISTORY, "a", encoding="utf-8") as f:
            now_ = str(datetime.now()).split(".")[0]
            f.writelines([now_, ",", data_flow.strip(), ",", class_, "\n"])

    def check_pool(self):
        avi_info = []
        for task_type in list(PROTOCOL_FLAG.keys()):
            avi_info.extend(
                sorted([(i[-1], f"{task_type}", i[0])
                        for i in self.rc.sync_remain_subs(task_type)]))
        if not avi_info:
            return {"status": False, "msg": []}
        return {"status": True, "msg": avi_info}

    def find_available_subscribe(self, cache: dict = None):
        """
        查询池状态
        :return:
        """

        pool = cache if cache else self.check_pool()

        if not pool['status']:
            return True

        # 可用订阅信息 type:list
        avi_info = pool['msg']

        # 隐藏订阅 Token
        alias: dict = self.rc.get_alias()
        sub2uid = {
            i[-1]: alias.get(str(urlparse(i[-1]).netloc),
                             str(urlparse(i[-1]).netloc))
            for i in avi_info
        }

        uid2sub = {i[-1]: i[0] for i in sub2uid.items()}

        info_canvas = [f"{i[0]}  {i[1]}  {sub2uid[i[-1]]}" for i in avi_info]

        avi_info = [
            "".center(2, " ").join(["过期时间", "订阅类型", "订阅链接"]),
        ] + info_canvas

        usr_choice = easygui.choicebox(msg="注:审核标准为北京时区；点击获取，链接自动复制",
                                       title=TITLE,
                                       choices=avi_info,
                                       preselect=1)

        logger.info(usr_choice)

        if "-" in usr_choice:

            subscribe, task_name = uid2sub[usr_choice.split("  ")
                                           [-1]], usr_choice.split("  ")[1]

            self.resp_tip(subscribe, task_name)

            self.rc.sync_detach_subs(task_name, subscribe)

        elif "过期时间" in usr_choice:

            logger.warning("链接选择错误")

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
            easygui.enterbox(msg="获取成功，点击确定自动复制链接",
                             title=TITLE,
                             default=subscribe)
        try:
            # 获取成功
            if "http" in subscribe:
                logger.success("GET--{}".format(subscribe))
                # 自动复制
                pyperclip.copy(subscribe)
                # 将数据存入本地文件
                self.save_flow(subscribe, task_name)
            # 获取异常
            else:
                logger.critical("SubscribeGetException")
                easygui.exceptionbox(
                    title=TITLE,
                    msg="LoggerCritical:T_{}".format(
                        str(datetime.now()).split(" ")[0]) + "\n\n订阅获取异常，请重试！"
                    "\n\n若多次重试仍不可用，请访问本项目寻求解答"
                    "\n\n项目地址:https://github.com/QIN2DIM",
                )
        finally:
            # 返回上一页
            return True

    def quick_get(self, type_of_subscribe: str):
        """

        :param type_of_subscribe: ssr,v2ray,trojan...
        :return:
        """
        # 防止乱点
        if type_of_subscribe in PROTOCOL_FLAG:
            self.resp_tip(self.rc.quick_get(type_of_subscribe),
                          type_of_subscribe)
        return True


class VulcanSpiderAir(CoroutineEngine):
    """内嵌微型爬虫-查看机场生态"""
    def __init__(self, url2type, task_docker):
        super(VulcanSpiderAir, self).__init__(task_docker=task_docker)

        self.url2type = url2type

        self.pending_docker = Queue()

    @staticmethod
    def invite_code_cleaner(hrefs):
        """
        # 清洗链接中的邀请码和注册码，返回纯净的链接
        @param hrefs:
        @return:
        """
        clean_href = []
        for href in hrefs:
            if "?" in href:
                href = href.split("?")[0]
                clean_href.append(href)
            else:
                clean_href.append(href)
        return clean_href

    @staticmethod
    def merger_for_show(fetch_runtime_response: dict):
        names = fetch_runtime_response.get('names')
        hrefs = fetch_runtime_response.get('hrefs')

        mode_show = ["序号    机场名    官网链接"] + [
            "【{}】 【{}】 【{}】".format(i + 1,
                                    list(x)[0],
                                    list(x)[-1])
            for i, x in enumerate(zip(names, hrefs)) if "http" in list(x)[-1]
        ]

        mode_save = [
            ["序号", "机场名", "官网连接"],
        ] + [[i + 1, list(x)[0], list(x)[-1]]
             for i, x in enumerate(zip(names, hrefs)) if "http" in list(x)[-1]]

        return {'show': mode_show, 'save': mode_save}

    def fetch(self, url):
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
        }
        proxies = {"http": None, "https": None}
        try:
            res = requests.get(url, headers=headers, proxies=proxies)
            res.raise_for_status()
        except requests.exceptions.RequestException:
            return False

        # 定位项目
        items = BeautifulSoup(res.text,
                              "html.parser").find_all("li", class_="link-item")
        # 机场名
        names = [
            item.find("span", class_="sitename").text.strip() for item in items
        ]
        # 获取去除邀请码的机场链接
        hrefs = self.invite_code_cleaner(
            [item.find("a")["href"] for item in items])

        return {"names": names, "hrefs": hrefs}

    def ace_agent(self, task):

        fetch_runtime_response = self.fetch(task)

        docker_ = self.merger_for_show(fetch_runtime_response)

        self.pending_docker.put_nowait({self.url2type[task]: docker_})

    def killer(self):
        global _memory_docker_of_small_spider
        docker_ = {}
        while not self.pending_docker.empty():
            block = self.pending_docker.get_nowait()
            docker_.update(block)
        _memory_docker_of_small_spider = docker_


class PublicPool:
    """preview version: 通过跳板机搜集国内可访问的可靠节点信息"""
    @staticmethod
    def rest_protocol_vless(node_detail: str, remark=None):
        """
        给订阅连接赋值 remark 别名
        :param node_detail:
        :param remark:
        :return:
        """
        remark = random.randint(0, 99) if remark is None else remark
        features = node_detail.split("&")
        security = "xtls"
        type_ = "tcp"
        sni_ = ""
        for feature in features:
            if "security=" in feature:
                security = feature.split("=")[-1]
            elif "type" in feature:
                type_ = feature.split("=")[-1]
            elif "host" in feature:
                sni_ = feature.split("=")[-1]
        new_protocol = f"{node_detail}&sni_={sni_}&headerType=none#XrayCore | {security}_{type_}_{remark} by v2rss"
        return new_protocol

    @retry(tries=2, delay=1)
    def pull_from_iyideng(self, to_clipboard: bool = None):
        """
        测试工程 | 从第三方站点拉取订阅
        :param to_clipboard: 是否自动复制到剪贴板
        :return:
        """

        # ---------------------------------
        # get verify-code
        # ---------------------------------
        iyideng_github_io = "https://raw.githubusercontent.com/iyidengme/iyidengme.github.io/master/README.md"
        res = requests.get(DEFAULT_ADAPTOR + iyideng_github_io)
        soup = BeautifulSoup(res.text, "html.parser")
        verify_code = [
            i.replace(":", "\t").replace("：", "\t").split("\t")[-1]
            for i in soup.text.split('\n') if "验证码" in i
        ][0]

        # ---------------------------------
        # get nodes
        # ---------------------------------
        url = "https://iyideng.win/welfare/free-v2ray-vmess-node.html"
        session = requests.session()
        data = {"huoduan_verifycode": verify_code}
        headers = {
            'user-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78",
            'origin':
            "https://iyideng.win",
            'referer':
            "https://iyideng.win/welfare/free-v2ray-vmess-node.html",
            'pragma':
            'no-cache',
            'cache-control':
            'no-cache',
        }
        response = session.post(url,
                                headers=headers,
                                data=data,
                                allow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        tree = soup.find("main").find("div")

        # ---------------------------------
        # parse nodes
        # ---------------------------------
        vless_nodes = []
        for i, node in enumerate(tree.text.split('\n')):
            if "vless://" in node:
                vless_nodes.append(self.rest_protocol_vless(node, i))

        # ---------------------------------
        # get nodes to clipboard
        # ---------------------------------
        if to_clipboard:
            pyperclip.copy("\n".join(vless_nodes))

        return vless_nodes


"""################### 网络审查 ######################"""


class NetChainReview:
    """诊断网络连接状态的一系列工具箱"""
    def __init__(self):
        self.response = None
        self.s = socket.socket()
        self.s.settimeout(2)

    def run(self):
        """
        诊断网络连接状态
        :return:
        """
        test_list = {
            "baidu": ("www.baidu.com", 443),
        }

        try:
            status = self.s.connect_ex(test_list["baidu"])
            self.response = status == 0
        except socket.error:
            self.response = False
        finally:
            self.s.close()
            return self.response


"""################### 菜单入口 ######################"""


class PaneInterfaceIO:
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
            "[1]白嫖机场", "[2]高端机场", "[3]机场汇总", "[4]返回", "[5]退出"
        ]
        # 机场生态内页
        self.airport_function_menu = ["[1]查看", "[2]保存", "[3]返回"]
        # 根据配置信息自动选择采集模式
        self.ssr_home_menu = [
            "[1]V2Ray订阅链接",
            "[2]SSR订阅链接",
            "[3]查询可用链接",
            # "[4]园丁模式",
            # "[5]垂直挖掘模式",
            # "[6]破冰船一键代理",
            "[7]返回",
            "[8]退出",
        ]

    def home_menu(self):
        """主菜单"""
        # ----------------------------------------
        # UI功能选择
        # ----------------------------------------
        resp = True
        usr_choice: str = easygui.choicebox("功能列表",
                                            TITLE,
                                            self.main_home_menu,
                                            preselect=1)
        logger.info(usr_choice)
        if usr_choice is None:
            return True
        try:
            if "查看机场生态" in usr_choice:
                # Skip step --> 利用子线程进行爬虫作业，而非交互确认后的临时提交的爬虫作业，提升应用性能
                SubThreadPoolIO.air_ecology_spider()
                #  返回交互页面
                resp = self.submenu_air_ecology()
            elif "获取订阅链接" in usr_choice:
                resp = self.submenu_subscribe_requester()
            elif "打开本地文件" in usr_choice:
                os.startfile(PATH_FETCH_REQUESTS_HISTORY)
                resp = False
            elif "检查版本更新" in usr_choice:
                # 通过扫描 GitHub API 查询比对版本信息来确定是否需要更新
                # yes 用户交互：确认更新  policy 版本比对信息，true 可更新
                yes, policy = GlobalInterfaceIO.api_is_need_to_update()
                if policy:
                    # 若可更新且用户确认更新
                    if yes:
                        # childThread --> 拉起子线程交互 UI 引导安装
                        SubThreadPoolIO.update_guider()
                        # mainThread 拉取发行客户端
                        resp = not GlobalInterfaceIO.download_release_by_adaptor(
                        )
                else:
                    # 若用户取消更新，返回主菜单
                    if yes is False:
                        resp = False
            else:
                resp = False
        # usr_choice is None
        except TypeError:
            resp = False
        finally:
            if resp:
                self.home_menu()
            else:
                return True

    def submenu_air_ecology(self):
        """air_port_menu GUI导航"""
        # ----------------------------------------
        # UI功能选择
        # ----------------------------------------
        usr_c = easygui.choicebox("功能列表",
                                  TITLE,
                                  self.airport_home_menu,
                                  preselect=0)
        logger.info(usr_c)
        resp = True
        try:
            if "返回" in usr_c:
                resp = True
            elif "退出" in usr_c:
                resp = False
            else:
                SubmenuAirEcology(usr_c).interact()
        except TypeError:
            resp = True
        finally:
            return resp

    def submenu_subscribe_requester(self):
        """
        一级菜单
        :mode: True:本地采集，False 服务器采集
        :return:
        """
        # ----------------------------------------
        # 初始化进程冻结锁
        # ----------------------------------------
        sr = SubscribeRequester()
        ProcessZeus().process_locker()
        resp = True
        # ----------------------------------------
        # UI功能选择
        # ----------------------------------------
        pool = sr.check_pool()
        if not pool['status']:
            easygui.msgbox("无可用订阅", TITLE)
            return True

        usr_choice: str = easygui.choicebox("功能列表",
                                            TITLE,
                                            self.ssr_home_menu,
                                            preselect=1)
        logger.info(usr_choice)
        if usr_choice is None:
            return True
        try:
            if "[1]V2Ray订阅链接" in usr_choice:
                resp = sr.quick_get("v2ray")
            elif "[2]SSR订阅链接" in usr_choice:
                resp = sr.quick_get("ssr")
            elif "[3]查询可用链接" in usr_choice:
                resp = sr.find_available_subscribe(pool)
            elif "返回" in usr_choice:
                resp = True
            else:
                resp = False
        except TypeError:
            resp = True
        finally:
            return resp


class SubmenuAirEcology:
    """批量获取 register-url of Providers """
    def __init__(self, air_type):
        self.func_list = ["[1]查看", "[2]保存", "[3]返回"]
        self.air_type = air_type

        self.data_save = None
        self.data_show = None

    def save(self, data_flow, default_path=None):
        """
        缓存采集结果
        :param data_flow:
        :param default_path:
        :return:
        """
        default_path = PATH_FETCH_AIR_ECOLOGY if default_path is None else default_path

        try:
            with open(default_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for x in data_flow:
                    writer.writerow(x)
            logger.info("机场生态信息保存")
        except PermissionError as e:
            logger.exception(e)
            easygui.exceptionbox("核心文件被占用:{}".format(default_path))
            default_path = os.path.join(
                easygui.diropenbox(msg="选择存储目录", title=TITLE),
                os.path.basename(PATH_FETCH_AIR_ECOLOGY),
            )
            self.save(data_flow=data_flow, default_path=default_path)

        return default_path

    def show(self):
        """
        呈现采集结果
        :return:
        """
        usr_choice = easygui.choicebox(msg="选中即可跳转目标网址,部分机场需要代理才能访问",
                                       title=TITLE,
                                       choices=self.data_show)
        if usr_choice is None:
            return True
        if "http" in usr_choice:
            url = usr_choice.split(" ")[-1][1:-1]
            webbrowser.open(url)
            return None
        logger.warning("机场网址失效或操作有误")
        easygui.msgbox("机场网址失效或操作有误", title=TITLE, ok_button="返回")
        return self.show()

    def interact(self):
        """
        交互面板--查看机场生态
        :return:
        """
        usr_choice = easygui.choicebox(title=TITLE, choices=self.func_list)
        logger.info(usr_choice)

        while True:
            if _memory_docker_of_small_spider == {}:
                continue
            for type_, docker_ in _memory_docker_of_small_spider.items():
                if type_ in self.air_type:
                    self.data_save, self.data_show = docker_['save'], docker_[
                        'show']
                    break
            break

        if usr_choice is None:
            return None
        if "返回" in usr_choice:
            return True
        if "保存" in usr_choice:
            path_ = self.save(self.data_save)
            os.startfile(path_)
            return None
        if "查看" in usr_choice:
            return self.show()
        return True


"""################### 接口管理 ######################"""


class GlobalInterfaceIO:
    @staticmethod
    def download_release_by_adaptor():
        """
        通过 CFW 引导下载 GitHub Release。
        接管无法过墙的访问流量，用户无需使用代理也可更新客户端
        :return:
        """
        global _done_work, _max_queue_size

        # 获取发行客户端信息
        release_status = _memory_docker_of_version_control['release']
        download_url = release_status['download_url']
        size = release_status['size']
        filename = "v2rss.zip"

        # 管口大小，用于流下载每批次大小
        chunk_size = 2048
        _max_queue_size = int(size / chunk_size)

        # 读取 CFW 全球加速节点为国内 IP 提供代理下载
        adaptor = DEFAULT_ADAPTOR

        # 探测包头信息
        session = requests.session()

        # 将{文件名}用以拼接本地下载目录 ~/documents/v2rss/client/versionID/v2rss.zip
        cache_merge = ToolBox.preload_cache(DIR_DEFAULT_DOWNLOAD,
                                            PANEL_VERSION_ID_CURRENT)
        cache_merge = os.path.join(cache_merge, filename)

        # 将 CFW 全球加速接点与 release's download url 拼接
        response = session.get(adaptor + download_url, stream=True)

        # 使用“流模式”下载发行客户端
        with open(cache_merge, "wb") as f:
            for chunk in response.iter_content(chunk_size):
                # 单位流的工作完成，向全局变量推送更新进度。既任务完成数+1
                _done_work.put_nowait(1)
                f.write(chunk)

        # 解压可执行文件 --> ~/documents/v2rss/client/versionID/v2rss.exe
        v2rss_exe_path = ToolBox.unzip_file(cache_merge)
        v2rss_exe_basename = "v2rss.exe"
        # v2rss_exe_basename = "v2ray╘╞▓╩╝º.exe"
        desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')

        # 当桌面不存在同名文件时，将解压好的 v2rss.exe 移动到桌面
        src_path = os.path.join(v2rss_exe_path, v2rss_exe_basename)
        if os.path.exists(os.path.join(desktop_path, v2rss_exe_basename)):
            v2rss_exe_basename = f"{v2rss_exe_basename.split('.exe')[0]}_{random.randint(1, 5)}.exe"
        dst_path = os.path.join(desktop_path, v2rss_exe_basename)

        try:
            # 移动文件 src_path --> dst_path
            shutil.move(src_path, dst_path)
            # 自动打开 latest release
            os.startfile(dst_path)
            # 清除下载缓存
            ToolBox.delete_cache(os.path.dirname(cache_merge))
        except FileNotFoundError:
            ToolBox.printer_log(f"文件移动失败 {src_path} --> {dst_path}", 0)

        # 控制 release 自动退出
        return True

    @staticmethod
    def api_update_guider():
        """
        监听客户端更新进度，提供 GUI 监控面板
        :return:
        """

        # 任务暂未初始化
        while _max_queue_size == -1:
            loop = sg.OneLineProgressMeter(PROGRESS_METER_TITLE,
                                           0,
                                           1,
                                           grab_anywhere=True,
                                           no_titlebar=True,
                                           keep_on_top=True)
            if not loop:
                return

        # 任务启动
        while _max_queue_size >= _done_work.qsize():
            # loop 监听流进度，if Cancel: loop is None
            loop = sg.OneLineProgressMeter(PROGRESS_METER_TITLE,
                                           _done_work.qsize(),
                                           _max_queue_size,
                                           grab_anywhere=True,
                                           no_titlebar=True,
                                           keep_on_top=True)
            # 如用户手动取消任务,退出流的监听状态
            if not loop and _max_queue_size >= _done_work.qsize():
                break
            time.sleep(0.01)

        sg.SystemTray.notify("V2Ray云彩姬", "资源下载完毕")

    @staticmethod
    def api_is_need_to_update() -> tuple:
        """
        客户端更新引导，检测客户端是否可以更新，以及接受用户更新客户端的决定
        :return:
        """
        global _memory_docker_of_version_control

        pvc = PanelVersionControl()

        policy = pvc.is_need_to_update()
        ToolBox.printer_log("API | check version of release file", 1)

        pvc.parse_download_url()
        ToolBox.printer_log("API | parse download url", 1)

        _memory_docker_of_version_control['release'] = pvc.RELEASE_DESC
        ToolBox.printer_log(
            "API | The hash code of the release software was successfully compared.",
            1)

        if policy['result'] is True:
            need_to_update = easygui.ynbox(
                msg=
                f"检测到新的安装包：{pvc.RELEASE_DESC['name']}{pvc.RELEASE_DESC['is_prerelease']},是否下载？"
                f"\n\n--> 软体大小：{pvc.RELEASE_DESC['size-info']}"
                f"\n\n--> 推送时间：{pvc.RELEASE_DESC['latest_change_time']}"
                f"\n\n--> 资源描述：{pvc.RELEASE_DESC['sketch']}",
                title=TITLE,
                choices=["[<F1>]更新", "[<F2>]退出"],
                default_choice="[<F1>]更新",
                cancel_choice="[<F2>退出]")

            if need_to_update:
                return True, policy['result']
            return False, policy['result']

        if policy['result'] is None:
            visit_repo = easygui.ynbox(
                msg=
                f"Warning：{pvc.RELEASE_DESC['name']} The software update is abnormal!"
                f"\n\n--> 可能原因：(1)您使用的软体对应的版本标签已被作者删除，无法比较版本新旧；"
                f"\n\n              (2)您使用的软体已被二次编译，版本签名与分支树不符；"
                f"\n\n              (3)Calm down!也有可能是您目前的网络状况不佳，请稍后重试；"
                f"\n\n{''.center(80, '_')}"
                f"\n\n以下信息为当前最新版本特性，可根据实际情况访问项目仓库手动下载"
                f"\n\n{pvc.REPO_RELEASE_HTML}"
                f"\n\n--> 开源软体：{pvc.RELEASE_DESC['name']}{pvc.RELEASE_DESC['is_prerelease']}"
                f"\n\n--> 软体大小：{pvc.RELEASE_DESC['size-info']}"
                f"\n\n--> 推送时间：{pvc.RELEASE_DESC['latest_change_time']}"
                f"\n\n--> 资源描述：{pvc.RELEASE_DESC['sketch']}",
                title=TITLE,
                choices=["[<F1>]访问仓库", "[<F2>]返回首页"],
                default_choice="[<F1>]访问仓库",
                cancel_choice="[<F2>退出]")
            if visit_repo:
                webbrowser.open(pvc.REPO_RELEASE_HTML)
                return False, policy['result']
            return None, policy['result']

        if policy['result'] is False:
            easygui.msgbox(msg=f"当前软体：{TITLE} 已是最新版本！",
                           title=TITLE,
                           ok_button="确定")
            return None, policy['result']

    @staticmethod
    def api_air_ecology_spider():
        """
        Policy-1 当前网络状态良好时拉取第三方的站点描述信息（obj-rss）
        :return:
        """
        task_docker = [
            # 高端机场
            "https://52bp.org/vip-airport.html",
            # 白嫖机场
            "https://52bp.org/free-airport.html",
            # 机场汇总
            "https://52bp.org/airport.html",
        ]
        url2type = dict(zip(task_docker, ["高端机场", "白嫖机场", "机场汇总"]))

        VulcanSpiderAir(task_docker=task_docker, url2type=url2type).go()

        ToolBox.printer_log("API | air_ecology_spider", 1)


class SubThreadPoolIO:
    @staticmethod
    def update_guider():
        """
        客户端更新的进度条 GUI
        :return:
        """
        threading.Thread(name="updater",
                         target=GlobalInterfaceIO.api_update_guider,
                         daemon=True).start()
        ToolBox.printer_log("SubThread | api_update_guider", 1)

    @staticmethod
    def air_ecology_spider():
        """
        启动子线程爬虫访问第三方站点
        :return:
        """
        if _memory_docker_of_small_spider == {}:
            threading.Thread(name="air-spider",
                             target=GlobalInterfaceIO.api_air_ecology_spider,
                             daemon=True).start()

        ToolBox.printer_log("SubThread | air_ecology_spider", 1)


@logger.catch()
def startup_from_platform():
    """
    fixme paneL中存在大量try...finally...写法，该写法可能会丢失Exception信息
    :return:
    """
    threading.Thread(target=ToolBox.reset_rdb_object).start()
    try:
        # 运行环境初始化
        ToolBox.prepare_environment()
        # # 网络检测
        if NetChainReview().run():
            PaneInterfaceIO().home_menu()
        else:
            logger.warning("网络异常")
            easygui.msgbox("网络异常", title=TITLE)
    except Exception as es_global:
        easygui.exceptionbox(str(es_global))


if __name__ == '__main__':
    startup_from_platform()
