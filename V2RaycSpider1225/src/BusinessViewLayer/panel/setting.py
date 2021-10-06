# -*- coding: utf-8 -*-
# Time       : 2021/9/16 23:08
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os

import PySimpleGUI as sg
import pytz
from loguru import logger

"""********************************* Panel Path *********************************"""
"""
# 工程目录(系统核心文件，请勿删改)基于Windows10设计
~/Documents/V2RayCloudSpider
    --*logs
        --*error.log
        --*runtime.log
   --database
        --FetchRequestsHistory.txt
        --[FetchAirEcologyInfo.csv]
        --setting.yaml      
   --client
        -- 4.6.1
            --[V2Ray云彩姬.exe]
"""
# 软件本地根目录
PROJECT_ROOT = os.path.join(os.path.expanduser("~"), "Documents\\V2RayCloudSpider")

# 软件本地日志目录
DIR_LOG = os.path.join(PROJECT_ROOT, "logs")

# 本地运行日志
logger.add(
    os.path.join(DIR_LOG, "runtime_local.log"),
    level="DEBUG",
    rotation="1 week",
    retention="20 days",
    encoding="utf8",
)

logger.add(
    os.path.join(DIR_LOG, "error_local.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
)

# 软件本地数据仓库
DIR_DATABASE = os.path.join(PROJECT_ROOT, "database")

# 各版本panel默认下载根目录，在此目录下以版本号为子目录，如4.6.1，并以此为工作空间
DIR_DEFAULT_DOWNLOAD = os.path.join(PROJECT_ROOT, "client")

# panel 于本地的订阅请求历史
PATH_FETCH_REQUESTS_HISTORY = os.path.join(DIR_DATABASE, "FetchRequestsHistory.txt")

# panel 于本地的机场生态缓存文件
PATH_FETCH_AIR_ECOLOGY = os.path.join(DIR_DATABASE, "FetchAirEcologyInfo.csv")

# panel 于本地的客户端配置文件
PATH_SETTING_YAML = os.path.join(DIR_DATABASE, "setting.yaml")
"""********************************* Panel Env *********************************"""
# ---------------------------------------------------
# TODO (√)BAND_BATCH -- 自闭时间：PC(链接获取)进程锁死的冷却时间
# ---------------------------------------------------
# Defaults type:int = 25 sec
BAND_BATCH: int = 25
# ---------------------------------------------------
# TODO (*)Redis BusinessLogicLayer Server Configuration(SSH-Advanced)
# ---------------------------------------------------
# Core settings of the Master's secret key.Do not modify!
REDIS_SECRET_KEY: str = "v2rayc_spider:{}"
# 请确保以下Redis设置与master-redis配置一致
REDIS_HOST: str = ''
REDIS_PASSWORD: str = ''
REDIS_PORT: int = 6379
REDIS_DB: int = 0
# ---------------------------------------------------
# TODO (*) 其他全局变量
# ---------------------------------------------------
from .flag import PANEL_VERSION_ID_CURRENT

# 我就是云彩姬!
TITLE = f"V2Ray云彩姬_v{PANEL_VERSION_ID_CURRENT}"

# Github项目地址
GITHUB_PROJECT = 'https://github.com/QIN2DIM/V2RayCloudSpider'

# 时区统一
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")

# 主流协议头
PROTOCOL_FLAG = {
    "ss": "ss://",
    "shadowsocks": "ss://",
    "ssr": "ssr://",
    "shadowsocksr": "ssr://",
    "v2ray": "vmess://",
    "trojan": "trojan://",
    "trojan-go": "trojan-go://",
    "xray": "vless://",
}
PROTOCOL_TYPE = ['ss', 'ssr', 'v2ray', 'trojan', 'xray']

# 预清洗时间 /hour 过滤存活时间少于PRE_CLEANING_TIME小时的订阅
PRE_CLEANING_TIME: int = 6

# CFW 加速github repo拉取速度 请填入你自己的部署连接
DEFAULT_ADAPTOR = "https://git.yumenaka.net/"
ADAPTORS = [
    DEFAULT_ADAPTOR,
    "https://git.yumenaka.net/",
]

# PySimpleGUI 进度条Title
PROGRESS_METER_TITLE = "VulcanAsh Monitor"

# PySimpleGUI 的主题
sg.theme("Reddit")

# URL-Scheme of clash
SCHEME_AUTOSTART_CLASH = "clash://install-config?url={}"

# 兼容 scaffold 传参
if not REDIS_HOST:
    from src.BusinessCentralLayer.setting import REDIS_MASTER

    REDIS_HOST = REDIS_MASTER.get('host')
if not REDIS_PASSWORD:
    from src.BusinessCentralLayer.setting import REDIS_MASTER

    REDIS_PASSWORD = REDIS_MASTER.get('password')
if REDIS_PORT == 0:
    from src.BusinessCentralLayer.setting import REDIS_MASTER

    REDIS_PASSWORD = REDIS_MASTER.get('port')
