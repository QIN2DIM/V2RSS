import os

import pytz
from loguru import logger

"""********************************* TOS *********************************"""
# ---------------------------------------------------
# 工程编号与版本号，版本号必须与工程版本(文件名)号一致 请勿改动!
# version命名规则 k.u.r -b
#   --k kernel 内核级更新
#   --u update 加入新功能/模块/机制
#   --r repair 修复已知漏洞或小改动
#   --b branch 分支版本，分为 测试版(beta)、开发版（dev）、稳定版(release)
# project_num命名规则 K25，既每进行一次内核级更新时K+1，如：
#   "4.u.r 0925" -> "5.u.r 1025"
# 请确保发行版本号与此VERSION_ID一致
# ---------------------------------------------------
PANEL_PROJECT_ID_CURRENT = "1225"
PANEL_VERSION_ID_CURRENT = "4.5.1"
# 我就是云彩姬!
TITLE = f"V2Ray云彩姬_v{PANEL_VERSION_ID_CURRENT}"
# Github项目地址
GITHUB_PROJECT = 'https://github.com/QIN2DIM/V2RayCloudSpider'
"""********************************* panel环境变量 *********************************"""
# 时区统一
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")
# ---------------------------------------------------
# TODO (√)BAND_BATCH -- 自闭时间：PC(链接获取)进程锁死的冷却时间
# Defaults type:int = 15 sec
# ---------------------------------------------------
BAND_BATCH: int = 15
# ---------------------------------------------------
# (*)Redis BusinessLogicLayer Server Configuration(SSH-Advanced)
# ---------------------------------------------------
# todo Core settings of the Master's secret key.Do not modify!
REDIS_SECRET_KEY: str = "v2rayc_spider:{}"
# 请确保以下Redis设置与master-redis配置一致
REDIS_HOST: str = ''
REDIS_PASSWORD: str = ''
REDIS_PORT: int = 6379
REDIS_DB: int = 0
# ---------------------------------------------------
# (*) Flask API Setting
# ---------------------------------------------------
# 请确保以下Flask设置与server配置一致
API_PORT = 6500
API_HOST = REDIS_HOST

# ---------------------------------------------------
# 其他全局变量
# ---------------------------------------------------

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

"""********************************* panel本地文档索引路径 *********************************"""
# ---------------------------------------------------
# 工程目录(系统核心文件，请勿删改)基于Windows10设计
# ---------------------------------------------------
"""
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

# 分流器API
DEFAULT_ADAPTOR = ""
ADAPTORS = [
    DEFAULT_ADAPTOR,
    "https://git.yumenaka.net/",
]
