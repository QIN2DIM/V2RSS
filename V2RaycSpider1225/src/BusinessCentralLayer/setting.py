"""TODO 服务器后端配置"""

from os.path import join, dirname, exists

import colorama
from loguru import logger

from src.config import *

# ---------------------------------------------------
# TODO Server doc tree base on linux
# ROOT_PROJECT:/qinse/V2RaycSpider{version}
# ---------------------------------------------------
"""
--/
--/qinse/V2RaycSpider{version}
    --BCL
    --BLL
    --BVL
    --Database
        --client_depot
            --vcs.csv
        --logs
            --*error.log
            --*runtime.log
        --temp_cache
            --*AnyTempCacheFile...
        --*CrawlFetchHistory.txt
        --fake_useragent_0.1.11.json
    --*tests
    --*setup.py
    --interface(main.py)
    --config(.yaml/.py/.env)
"""
# ---------------------------------------------------
# TODO 工程根目录定位
# 若此setting.py文件位于根目录下 SERVER_DIR_PROJECT = dirname(__file__)
# 若位于次级目录下则 SERVER_DIR_PROJECT = dirname(__file__) 例如位于任一`Layer`下
# 位于孙级目录下以此类推，一般建议最多到次级。
# ---------------------------------------------------
if "win" in platform:
    CHROMEDRIVER_PATH = dirname(dirname(__file__)) + "/BusinessCentralLayer/chromedriver.exe"
    SERVER_DIR_PROJECT = dirname(dirname(__file__))
else:
    CHROMEDRIVER_PATH = dirname(dirname(__file__)) + "/BusinessCentralLayer/chromedriver"
    SERVER_DIR_PROJECT = f"/qinse/V2RaycSpider{project_num}"
# 若不存在CHROMEDRIVER_PATH指定的路径则尝试从环境变量中查找chromedriver文件
if not exists(CHROMEDRIVER_PATH):
    CHROMEDRIVER_PATH = "chromedriver"
# ---------------------------------------------------
# TODO 配置文件默认路径（.yaml）
# 默认位于根目录下
# ---------------------------------------------------

# 配置文件，系统读取的是这个文件
SERVER_PATH_YAML_CONFIG = join(SERVER_DIR_PROJECT, 'config.yaml')
# 配置文件模板，无用但必须存在
SERVER_PATH_YAML_CONFIG_SAMPLE = join(SERVER_DIR_PROJECT, 'config-sample.yaml')

# ---------------------------------------------------
# TODO 服务器数据库目录
# ---------------------------------------------------
SERVER_DIR_DATABASE = join(SERVER_DIR_PROJECT, "Database")

# SQLite3 文件数据库配置
SQLITE3_CONFIG = {
    'db': join(SERVER_DIR_DATABASE, 'v2raycs.db'),
    'table': 'v2raycs',
    'header': ','.join(['domain', 'subs', 'class_', 'end_life', 'res_time', 'passable',
                        'username', 'password', 'email', 'uuid PRIMARY KEY']),
}

# 历史客户端仓库。用于存放打包好的panel可执行文件
SERVER_DIR_CLIENT_DEPORT = join(SERVER_DIR_DATABASE, "client_depot")

# 版本管理文件。用于存放各个版本的panel版本号级对应的下载地址
SERVER_PATH_DEPOT_VCS = join(SERVER_DIR_CLIENT_DEPORT, "vcs.csv")

# 缓存文件夹路径
SERVER_DIR_DATABASE_CACHE = join(SERVER_DIR_DATABASE, "temp_cache")

# 滑动验证缓存
SERVER_DIR_CACHE_BGPIC = join(SERVER_DIR_DATABASE_CACHE, 'bg_cache')

# 链接获取历史
SERVER_PATH_DATABASE_FETCH = join(SERVER_DIR_DATABASE, "CrawlFetchHistory.txt")

# ---------------------------------------------------
# TODO 服务器日志文件路径
# ---------------------------------------------------
SERVER_DIR_DATABASE_LOG = join(SERVER_DIR_DATABASE, "logs")

logger.add(
    join(SERVER_DIR_DATABASE_LOG, "runtime.log"),
    level="DEBUG",
    rotation="1 day",
    retention="20 days",
    encoding="utf8",
)
logger.add(
    join(SERVER_DIR_DATABASE_LOG, "error.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
)
# 开启调试台彩色输出模式
colorama.init()
Fore = colorama.Fore
# ---------------------------------------------------
# TODO Nginx映射路径
# ---------------------------------------------------
if "linux" in platform:
    NGINX_SUBSCRIBE = "/usr/share/nginx/html/subscribe/{}.txt"
else:
    NGINX_SUBSCRIBE = join(SERVER_DIR_DATABASE_CACHE, "{}.txt")
