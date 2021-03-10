import os
from sys import platform

from loguru import logger as logger_local

"""********************************* panel环境变量 *********************************"""
# 我就是云彩姬!
TITLE = "V2Ray云彩姬"

# ---------------------------------------------------
# TODO (√)BAND_BATCH -- 自闭时间：PC(链接获取)进程锁死的冷却时间
# Defaults type:float = 0.75 minute
# ---------------------------------------------------
BAND_BATCH: float = 0.75

# ---------------------------------------------------
# (*)Redis BusinessLogicLayer Server Configuration(SSH-Advanced)
# ---------------------------------------------------
# (*) Core settings of the Master's secret key.Do not modify!
REDIS_SECRET_KEY: str = "v2rayc_spider:{}"

# ---------------------------------------------------
# 工程编号与版本号，版本号必须与工程版本(文件名)号一致 请勿改动!
# version命名规则 k.u.r -b
#   --k kernel 内核级更新
#   --u update 加入新功能/模块/机制
#   --r repair 修复已知漏洞或小改动
#   --b branch 分支版本，分为 测试版(beta)、稳定版(release)
# project_num命名规则 K25，既每进行一次内核级更新时K+1，如：
#   "4.u.r 0925" -> "5.u.r 1025"
# ---------------------------------------------------
project_num = "1225"
version = "5.1.0"

"""********************************* panel系统索引路径 *********************************"""
# ---------------------------------------------------
# 工程目录(系统核心文件，请勿删改)基于Windows10设计
# ---------------------------------------------------
"""
--ROOT
   --logs
       --*error.log
       --*runtime.log
   --database
       --FetchRequestsHistory.txt
       --*FetchAirEcologyInfo.csv
       --user.yaml
   --depot
       --client
           --*[v2raycs.v.exe ...]
       --*updated.exe
"""
# 软件本地根目录
ROOT_DIR_PROJECT = "C:\\Program Files\\V2RaySpider" if "win" in platform else os.path.dirname(__file__)

# 软件本地日志目录
LOCAL_DIR_LOG = os.path.join(ROOT_DIR_PROJECT, "logs")

# 本地运行日志
logger_local.add(
    os.path.join(LOCAL_DIR_LOG, "runtime_local.log"),
    level="DEBUG",
    rotation="1 week",
    retention="20 days",
    encoding="utf8",
)

logger_local.add(
    os.path.join(LOCAL_DIR_LOG, "error_local.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
)

# 软件本地数据仓库
LOCAL_DIR_DATABASE = os.path.join(ROOT_DIR_PROJECT, "Database")

# 软件本地请求历史
LOCAL_PATH_DATABASE_FH = os.path.join(LOCAL_DIR_DATABASE, "FetchRequestsHistory.txt")

# 软件查看机场生态的缓存文件
LOCAL_PATH_AIRPORT_INFO = os.path.join(LOCAL_DIR_DATABASE, "FetchAirEcologyInfo.csv")

# 软件本地的客户端配置文件
LOCAL_PATH_DATABASE_YAML = os.path.join(LOCAL_DIR_DATABASE, "user.yaml")

# 软件本地的客户端配置信息
USER_YAML = {"path": "", "version": f"{version}"}

# 软件默认下载仓库
LOCAL_DIR_DEPOT = os.path.join(ROOT_DIR_PROJECT, "depot")

# 软件更新模组
PLUGIN_UPDATED_MODULE = os.path.join(LOCAL_DIR_DEPOT, "updated.exe")

# 各版本v2raycs默认下载路径
LOCAL_DIR_DEPOT_CLIENT = os.path.join(LOCAL_DIR_DEPOT, "client")
