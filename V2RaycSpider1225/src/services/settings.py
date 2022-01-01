# -*- coding: utf-8 -*-
# Time       : 2021/12/25 16:56
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import sys
from os.path import join, dirname, exists

from loguru import logger

# ---------------------------------------------------
# TODO [√]工程根目录定位
# ---------------------------------------------------
# 系统根目录
PROJECT_ROOT = dirname(dirname(__file__))
# 驱动器目录
DIR_DRIVERS = join(PROJECT_ROOT, "driver")
# chromedriver 所在路径
if "win" in sys.platform:
    PATH_CHROMEDRIVER = join(DIR_DRIVERS, "chromedriver.exe")
# elif "linux" in sys.app:
else:
    PATH_CHROMEDRIVER = join(DIR_DRIVERS, "chromedriver")
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
# ---------------------------------------------------
# TODO [√]服务器日志配置
# ---------------------------------------------------
event_logger_format = (
    "<g>{time:YYYY-MM-DD HH:mm:ss}</g> | "
    "<lvl>{level}</lvl> - "
    # "<c><u>{name}</u></c> | "
    "{message}"
)
logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    level="DEBUG",
    format=event_logger_format,
    diagnose=False
)
logger.add(
    sink=join(DIR_LOG, "error.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
    diagnose=False
)
logger.add(
    sink=join(DIR_LOG, "runtime.log"),
    level="DEBUG",
    rotation="1 day",
    retention="20 days",
    encoding="utf8",
    diagnose=False
)

# ---------------------------------------------------
# 路径补全
# ---------------------------------------------------
for _pending in [
    DIR_DRIVERS, PROJECT_DATABASE,
    DIR_TEMP_CACHE, DIR_CACHE_IMAGE, DIR_CACHE_AUDIO,
    DIR_CACHE_MINING, DIR_CACHE_CLASSIFY,
    DIR_LOG,
]:
    if not exists(_pending):
        os.mkdir(_pending)

# ---------------------------------------------------
# 合并配置文件参数
# ---------------------------------------------------
from config import *

__all__ = [
    # ------------------------------
    # SETTINGS
    # ------------------------------
    "logger", "PATH_CHROMEDRIVER", "DIR_CACHE_IMAGE", "DIR_CACHE_AUDIO",
    "DIR_CACHE_MINING", "DIR_CACHE_CLASSIFY",
    # ------------------------------
    # CONFIG
    # ------------------------------
    "REDIS_NODE", "POOL_CAP", "TIME_ZONE_CN", "TIME_ZONE_NY",
    "SCHEDULER_SETTINGS", "ROUTER_API", "ROUTER_NAME", "ROUTER_HOST",
    "ROUTER_PORT"
]
