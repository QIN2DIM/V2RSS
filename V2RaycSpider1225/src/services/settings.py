# -*- coding: utf-8 -*-
# Time       : 2021/12/25 16:56
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
from os.path import join, dirname, exists
from typing import Dict, Union, Optional

import pytz

from services.utils import ToolBox

"""
================================================ ʕ•ﻌ•ʔ ================================================
                                       (·▽·)欢迎使用 V2RSS云彩姬
================================================ ʕ•ﻌ•ʔ ================================================
"""
# ---------------------------------------------------
# [√]工程根目录定位
# ---------------------------------------------------
# 系统根目录
PROJECT_ROOT = dirname(dirname(__file__))
# 文件数据库目录
PROJECT_DATABASE = join(PROJECT_ROOT, "database")
# 运行缓存目录
DIR_TEMP_CACHE = join(PROJECT_DATABASE, "temp_cache")
# 滑动验证运行缓存目录
DIR_CACHE_IMAGE = join(DIR_TEMP_CACHE, "_img")
# 声纹验证运行缓存目录
DIR_CACHE_AUDIO = join(DIR_TEMP_CACHE, "_audio")
# sspanel-mining 组件运行缓存目录
DIR_CACHE_MINING = join(DIR_TEMP_CACHE, "_mining")
DIR_CACHE_CLASSIFY = join(DIR_CACHE_MINING, "classify")
# 服务日志目录
DIR_LOG = join(PROJECT_DATABASE, "logs")
DIR_LOG_COLLECTOR = join(DIR_LOG, "collector")
DIR_LOG_SYNERGY = join(DIR_LOG, "synergy")
# ---------------------------------------------------
# [√]服务器日志配置
# ---------------------------------------------------
logger = ToolBox.init_log(
    error=join(DIR_LOG, "error.log"), runtime=join(DIR_LOG, "runtime.log")
)
# ---------------------------------------------------
# 路径补全
# ---------------------------------------------------
for _pending in [
    PROJECT_DATABASE,
    DIR_TEMP_CACHE,
    DIR_CACHE_IMAGE,
    DIR_CACHE_AUDIO,
    DIR_CACHE_MINING,
    DIR_CACHE_CLASSIFY,
    DIR_LOG,
    DIR_LOG_COLLECTOR,
    DIR_LOG_SYNERGY,
]:
    if not exists(_pending):
        os.mkdir(_pending)

# ---------------------------------------------------
# 合并配置文件参数
# ---------------------------------------------------
# 时区
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")
TIME_ZONE_NY = pytz.timezone("America/New_York")

# 密钥变量
DETACH_SUBSCRIPTIONS = "DETACH_SUBSCRIPTIONS"

"""
================================================== ʕ•ﻌ•ʔ ==================================================
                        如果您并非 - V2RSS云彩姬 - 项目开发者 请勿修改以下变量的默认参数
================================================== ʕ•ﻌ•ʔ ==================================================

                                            Enjoy it -> ♂ main.py
"""

config_ = ToolBox.check_sample_yaml(
    path_output=join(dirname(dirname(__file__)), "config.yaml"),
    path_sample=join(dirname(dirname(__file__)), "config-sample.yaml"),
    block=not os.getenv("REDIS_URL"),
)
# --------------------------------
# [√] Redis node configuration
# --------------------------------
if os.getenv("REDIS_URL"):
    # REDIS_URL: "host#password#port#db"
    redis_params = os.environ["REDIS_URL"].split("#")
    REDIS_NODE = {
        "host": redis_params[0],
        "password": redis_params[1],
        "port": int(redis_params[2]),
        "db": int(redis_params[3]),
    }
elif not config_.get("REDIS_NODE"):
    REDIS_NODE = {"host": "127.0.0.1", "password": "", "port": 6379, "db": 0}
else:
    REDIS_NODE: Optional[Dict[str, Union[str, int]]] = config_["REDIS_NODE"]
# --------------------------------
# [√]Subscription pool capacity
# --------------------------------
POOL_CAP: Optional[int] = config_.get("POOL_CAP", 8)

# --------------------------------
# [√]Scheduled task configuration
# --------------------------------
if not config_.get("scheduler"):
    SCHEDULER_SETTINGS = {
        "collector": {"enable": True, "interval": 120},
        "decoupler": {"enable": True, "interval": 600},
    }
else:
    SCHEDULER_SETTINGS = config_["scheduler"]
# --------------------------------
# [√]External API interface
# --------------------------------
if not config_.get("router"):
    ROUTER_SETTINGS = {
        "name": "V2RSS",
        "host": "127.0.0.1",
        "port": 22333,
        "apis": {
            "get_v2ray": "/api/v2rss/get/v2ray",
            "get_subs_V1": "/api/v2rss/get_subs/v1",
            "get_subs_V2": "/api/v2rss/get_sbus/v2",
            "get_pool_status": "/api/v2rss/status",
        },
    }
else:
    ROUTER_SETTINGS = config_.get("router")
ROUTER_NAME: Optional[str] = ROUTER_SETTINGS["name"]
ROUTER_HOST: Optional[str] = ROUTER_SETTINGS["host"]
ROUTER_PORT: Optional[int] = ROUTER_SETTINGS["port"]
ROUTER_API = ROUTER_SETTINGS["apis"]
URI_GET_V2RAY: str = ROUTER_API["get_v2ray"]
URI_GET_SUBS_V1: str = ROUTER_API["get_subs_v1"]
URI_GET_SUBS_V2: str = ROUTER_API["get_subs_v2"]
URI_GET_POOL_STATUS: str = ROUTER_API["get_pool_status"]

# 读取环境变量覆盖用户态设置，但脚手架传参优先级更高
ROUTER_HOST = ROUTER_HOST if not os.getenv("ROUTER_HOST") else os.getenv("ROUTER_HOST")
ROUTER_PORT = ROUTER_PORT if not os.getenv("ROUTER_PORT") else os.getenv("ROUTER_PORT")
