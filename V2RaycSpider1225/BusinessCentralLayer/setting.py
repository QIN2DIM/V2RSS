from os.path import join, dirname

from loguru import logger

from config import *

# TODO 服务器后端配置
# ---------------------------------------------------
# 服务器工程目录,基于linux
# RootDir:/qinse/V2RaycSpider{verNum}
# ---------------------------------------------------
"""
--/qinse/V2RaycSpider{verNum}
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
"""
# Chromedriver 路径
if "win" in platform:
    CHROMEDRIVER_PATH = dirname(dirname(__file__)) + "/BusinessCentralLayer/chromedriver.exe"
    SERVER_DIR_PROJECT = dirname(dirname(__file__))
else:
    CHROMEDRIVER_PATH = dirname(dirname(__file__)) + "/BusinessCentralLayer/chromedriver"
    SERVER_DIR_PROJECT = f"/qinse/V2RaycSpider{project_num}"

# 配置文件默认路径（.yaml）
SERVER_PATH_YAML_CONFIG = join(SERVER_DIR_PROJECT, 'config.yaml')
SERVER_PATH_YAML_CONFIG_SAMPLE = join(SERVER_DIR_PROJECT, 'config-sample.yaml')

# 文件型数据库路径
SERVER_DIR_DATABASE = join(SERVER_DIR_PROJECT, "Database")

# TODO (√)SQLITE3 -- 文件数据库配置
SQLITE3_CONFIG = {
    'db': join(SERVER_DIR_DATABASE, 'v2raycs.db'),
    'table': 'v2raycs',
    'header': ','.join(['domain', 'subs', 'class_', 'end_life', 'res_time', 'passable',
                        'username', 'password', 'email', 'uuid PRIMARY KEY']),
}

# 历史客户端仓库
SERVER_DIR_CLIENT_DEPORT = join(SERVER_DIR_DATABASE, "client_depot")

# 版本管理文件
SERVER_PATH_DEPOT_VCS = join(SERVER_DIR_CLIENT_DEPORT, "vcs.csv")

# 服务器日志文件路径<业务层>
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

# 缓存文件夹路径
SERVER_DIR_DATABASE_CACHE = join(SERVER_DIR_DATABASE, "temp_cache")

# 滑动验证缓存
SERVER_DIR_CACHE_BGPIC = join(SERVER_DIR_DATABASE_CACHE, 'bg_cache')

# 链接获取历史
SERVER_PATH_DATABASE_FETCH = join(SERVER_DIR_DATABASE, "CrawlFetchHistory.txt")

# FAKE_HEADER
SERVER_PATH_DATABASE_HEADERS = join(SERVER_DIR_DATABASE, "fake_useragent_0.1.11.json")

# BusinessLogicLayer
SERVER_DIR_LOGIC = join(SERVER_DIR_PROJECT, "BusinessLogicLayer")

SERVER_DIR_LOGIC_CLUSTER = join(SERVER_DIR_LOGIC, "cluster")

SERVER_DIR_CLUSTER_SLAVER = join(SERVER_DIR_LOGIC_CLUSTER, "slavers")

# Nginx映射路径
if "linux" in platform:
    NGINX_SUBSCRIBE = "/usr/share/nginx/html/subscribe/{}.txt"

else:
    NGINX_SUBSCRIBE = join(SERVER_DIR_DATABASE_CACHE, "{}.txt")
