from sys import platform
from os.path import join, dirname

import pytz
from environs import Env
from loguru import logger
from loguru import logger as logger_local

env = Env()
env.read_env()

"""
======================== ʕ•ﻌ•ʔ ========================
(·▽·)欢迎使用V2Ray云彩姬，请跟随提示合理配置项目启动参数
======================== ʕ•ﻌ•ʔ ========================
# TODO  2020/11/22
#  -- Modify
#       -- Panel -> UpdatedModule
#       -- Optimize -> Atomic operation
#  -- Expand -> action slaver


# TODO  v_1.0.2.11162350.11-beta
#  --请不要在<小带宽的国内云服务器>上部署此项目，推荐利用性能闲置的非大陆IP的VPS运行项目（非生产环境）
#  --若您的服务器配置 ~= `Linux 1xCPU 1GxRAM` 请勿在生产环境中开启coroutine_speed_up
#  --若您的服务器配置过于豪华或至少有 2xCPU 2GxRAM，请将所有加速特效拉满（脚本引入了一定的鲁棒均衡模组，可以保证稳定采集）
"""

# (√) 强制填写；(*)可选项
# ---------------------------------------------------
# TODO (√) Function Authority -- 功能权限
# ---------------------------------------------------
ENABLE_DEPLOY = env.bool("ENABLE_DEPLOY", True)  # 定时采集
ENABLE_SERVER = env.bool("ENABLE_SERVER", True)  # 部署API
ENABLE_COROUTINE = env.bool("ENABLE_COROUTINE", True)  # 协程加速
ENABLE_DEBUG = env.bool("ENABLE_DEBUG", not ENABLE_DEPLOY)  # Flask DEBUG

# ---------------------------------------------------
# TODO (√)BAND_BATCH -- 自闭时间：PC(链接获取)进程锁死的冷却时间
# Defaults type:float = 0.75 minute
# ---------------------------------------------------
BAND_BATCH = 0.75

# ---------------------------------------------------
# TODO (√)SINGLE_TASK_CAP -- 单类链接的队列容量极限
# 当某种链接的数量达到这个阈值则不会启动该类链接的采集任务
# <Performance limit of 1xCPU 1GRAM VPS KVM>
# Defaults type:int = 75
# ---------------------------------------------------
SINGLE_TASK_CAP: int = 200

# ---------------------------------------------------
# TODO (√)DEPLOY_CRONTAB -- schedule采集任务间隔
# 部署中每隔DEPLOY_CRONTAB分钟启动一次链接采集任务
# Defaults type:int = 60 minutes
# ---------------------------------------------------
DEPLOY_CRONTAB = 60

# ---------------------------------------------------
# TODO (√)Redis Cluster Configuration(SSH-BASE)
# 若您不知道如何配置Redis远程连接，请自行搜索或↓
# https://shimo.im/docs/5bqnroJYDbU4rGqy/
# ---------------------------------------------------

REDIS_GENERAL_DR = env.bool('REDIS_GENERAL_DR', True)
REDIS_GENERAL_DB = env.int('REDIS_GENERAL_DB', 0)

# TODO (√)Settings of the Master-Redis responsible for leading the workflow
REDIS_MASTER = env.dict(
    "REDIS_MASTER",
    {
        'host': '',
        'password': '',
        'port': 6379,
        'db': 0,
    }
)
# TODO (*)Setting of the Slave-Redis responsible for data disaster tolerance（DDT）
REDIS_SLAVER_DDT = env.dict(
    "REDIS_SLAVER_DDT",
    {
        # If you do not have extra servers, please use stand-alone backup
        'host': REDIS_MASTER['host'],
        'db': REDIS_MASTER['db'] + 1,
        'password': '',
        'port': 6379,
        # 'host': '',
        # 'db': 0,
    }
)

# ---------------------------------------------------
# TODO (√)API for Flask(SSH-BASE)
# ---------------------------------------------------
API_HOST = env.str('API_HOST', REDIS_MASTER['host'])
API_DEBUG = env.bool('API_DEBUG', ENABLE_DEBUG)
API_THREADED = env.bool("API_THREADED", True)
API_PORT = env.int('API_PORT', 6500)
OPEN_HOST = '127.0.0.1' if API_DEBUG or 'win' in platform else '0.0.0.0'

# ---------------------------------------------------
# TODO (*)SMTP_ACCOUNT -- 用于发送panic信息警报，默认发送给自己
# 推荐使用QQ邮箱，开启邮箱SMTP服务教程如下
# https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256
# ---------------------------------------------------
SMTP_ACCOUNT = {
    'email': '@qq.com',  # SMTP邮箱
    'sid': '',  # SMTP授权码
}

# ---------------------------------------------------
# TODO (√)CHROMEDRIVER_PATH -- ChromeDriver的路径
# 1.本项目内置的ChromeDriver可能与您的Chrome版本不适配。若您发现内置的ChromeDriver不能驱动项目，请根据下方提供的链接下载对应版本的文件
# 推荐`driver随chrome`，既根据现用的Chrome版本找对应的driver而不是对Chrome随意地升降版本(特别是linux环境)
# >> http://npm.taobao.org/mirrors/chromedriver/

# 2.本项目内置了Linux版本和Windows版本的ChromeDriver；显然您需要根据具体的部署环境下载相应的ChromeDriver
# 并将下载好的文件替换掉`./BusinessCentralLayer/` 下的`chromedriver.exe`或`chromedriver`

# 3.本项目基于Windows环境开发，Linux环境测试，可正常运行
# 若您的系统基于MacOS或其他，~可能~无法正常运行本项目
# ---------------------------------------------------

"""
========================== ʕ•ﻌ•ʔ ==========================
如果您并非<V2RayCloudSpider>项目开发者 请勿修改以下变量的默认参数
========================== ʕ•ﻌ•ʔ ==========================

                                  Enjoy it -> ♂main.py
"""

# ---------------------------------------------------
# (*)Redis BusinessLogicLayer Server Configuration(SSH-Advanced)
# ---------------------------------------------------
# (*) Core settings of the Master's secret key.Do not modify!
REDIS_SECRET_KEY = env.str("REDIS_SECRET_KEY", 'v2rayc_spider:{}')

# (*) If you have a BusinessLogicLayer server, please configure here
# ...

# ---------------------------------------------------
# (x) API -- 用于部署弹性伸缩中间件的引流接口
# (若没有集群服务器不建议设置)
# ---------------------------------------------------
ESS_API_HOST: str
ESS_API_PORT: int

# ---------------------------------------------------
# 云彩姬版本号,版本号必须与工程版本(文件名)号一致 请勿改动!
# ---------------------------------------------------
verNum = '1125'
version = '1.0.2.11162350.11'
"""********************************* 服务器后端配置 *********************************"""

# ---------------------------------------------------
# 服务器工程目录,基于linux
# RootDir:/qinse/V2RaycSpider{verNum}
# ---------------------------------------------------

# Chromedriver 路径,暂不支持Mac环境的云服务器
# Linux Google Chrome v85.0.4183.102
if 'win' in platform:
    CHROMEDRIVER_PATH = dirname(__file__) + '/BusinessCentralLayer/chromedriver.exe'
    SERVER_DIR_PROJECT = env.path("SERVER_DIR_PROJECT", dirname(__file__))
else:
    CHROMEDRIVER_PATH = dirname(__file__) + '/BusinessCentralLayer/chromedriver'
    SERVER_DIR_PROJECT = env.path('SERVER_DIR_PROJECT', f'/qinse/V2RaycSpider{verNum}')

# 文件型数据库路径
SERVER_DIR_DATABASE = env.path('SERVER_DIR_DATABASE', join(SERVER_DIR_PROJECT, 'Database'))

# 历史客户端仓库
SERVER_DIR_CLIENT_DEPORT = env.path('SERVER_DIR_CLIENT_DEPORT', join(SERVER_DIR_DATABASE, 'client_depot'))

# 版本管理文件
SERVER_PATH_DEPOT_VCS = env.path('SERVER_PATH_DEPOT_VCS', join(SERVER_DIR_CLIENT_DEPORT, 'vcs.csv'))

# 服务器日志文件路径<业务层>
SERVER_DIR_DATABASE_LOG = env.path("SERVER_DIR_DATABASE_LOG", join(SERVER_DIR_DATABASE, "logs"))
logger.add(env.str('LOG_RUNTIME_FILE', join(SERVER_DIR_DATABASE_LOG, 'runtime.log')), level='DEBUG', rotation='1 week',
           retention='20 days', encoding='utf8')
logger.add(env.str('LOG_ERROR_FILE', join(SERVER_DIR_DATABASE_LOG, 'error.log')), level='ERROR', rotation='1 week',
           encoding='utf8')

# 缓存文件夹路径
SERVER_DIR_DATABASE_CACHE = env.path('SERVER_DIR_DATABASE_CACHE', join(SERVER_DIR_DATABASE, 'temp_cache'))
# 链接获取历史
SERVER_PATH_DATABASE_FETCH = env.path("SERVER_PATH_DATABASE_FETCH", join(SERVER_DIR_DATABASE, "CrawlFetchHistory.txt"))
# FAKE_HEADER
SERVER_PATH_DATABASE_HEADERS = env.path("SERVER_PATH_DATABASE_HEADERS",
                                        join(SERVER_DIR_DATABASE, 'fake_useragent_0.1.11.json'))

# BusinessLogicLayer
SERVER_DIR_LOGIC = env.path(
    "SERVER_DIR_LOGIC", join(SERVER_DIR_PROJECT, 'BusinessLogicLayer'))
SERVER_DIR_LOGIC_CLUSTER = env.path(
    "SERVER_DIR_LOGIC_CLUSTER", join(SERVER_DIR_LOGIC, 'cluster'))
SERVER_DIR_CLUSTER_SLAVER = env.path(
    "SERVER_DIR_CLUSTER_SLAVER", join(SERVER_DIR_LOGIC_CLUSTER, 'slavers'))

# Nginx映射路径
if 'linux' in platform:
    NGINX_SUBSCRIBE = env.str('NGINX_SUBSCRIBE', '/usr/share/nginx/html/subscribe/{}.txt')
else:
    NGINX_SUBSCRIBE = env.str('NGINX_SUBSCRIBE', join(SERVER_DIR_DATABASE_CACHE, "{}.txt"))

# ---------------------------------------------------
# 路由接口
# ---------------------------------------------------
ROUTE_API = env.dict(
    "ROUTE_API", {
        'capture_subscribe': '/v2raycs/api/capture_subscribe',
        'version_manager': '/v2raycs/api/version_manager',
    }
)
# ---------------------------------------------------
# 任务队列
# ---------------------------------------------------
SEQ_TEST = env.dict(
    "SEQ_TEST", {
        'v2ray': True,
        'ssr': True,
        'trojan': False,
    }
)

CRAWLER_SEQUENCE = env.list("CRAWLER_SEQUENCE", [i[0] for i in SEQ_TEST.items() if i[-1]])
"""********************************* 客户端桌面前端配置 *********************************"""
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
ROOT_DIR_PROJECT = env.path("ROOT_PROJECT_PATH", 'C:\\V2RaySpider') if 'win' in platform else env.str(
    "ROOT_PROJECT_PATH", dirname(__file__))

# 软件本地日志目录
LOCAL_DIR_LOG = env.path("LOCAL_DIR_LOG", join(ROOT_DIR_PROJECT, "logs"))

# 本地运行日志
logger_local.add(env.str('LOG_RUNTIME_FILE', join(LOCAL_DIR_LOG, 'runtime.log'), level='DEBUG', rotation='1 week',
                         retention='20 days', encoding='utf8'))

logger_local.add(env.str('LOG_ERROR_FILE', join(LOCAL_DIR_LOG, 'error.log')), level='ERROR', rotation='1 week',
                 encoding='utf8')

# 软件本地数据仓库
LOCAL_DIR_DATABASE = env.path("LOCAL_DIR_FETCH", join(ROOT_DIR_PROJECT, 'Database'))

# 软件本地请求历史
LOCAL_PATH_DATABASE_FH = env.path("LOCAL_PATH_DATABASE_FH", join(LOCAL_DIR_DATABASE, 'FetchRequestsHistory.txt'))

# 软件查看机场生态的缓存文件
LOCAL_PATH_AIRPORT_INFO = env.path("LOCAL_PATH_AIRPORT_INFO", join(LOCAL_DIR_DATABASE, 'FetchAirEcologyInfo.csv'))

# 软件本地的客户端配置文件
LOCAL_PATH_DATABASE_YAML = env.path("LOCAL_PATH_DATABASE_YAML", join(LOCAL_DIR_DATABASE, 'user.yaml'))

# 软件本地的客户端配置信息
USER_YAML = env.dict("USER_YAML", {'path': '', 'version': f'{version}'})

# 软件默认下载仓库
LOCAL_DIR_DEPOT = env.path("LOCAL_DIR_DEPOT", join(ROOT_DIR_PROJECT, "depot"))

# 软件更新模组
PLUGIN_UPDATED_MODULE = env.path("PLUGIN_UPDATED_MODULE", join(LOCAL_DIR_DEPOT, 'updated.exe'))

# 各版本v2raycs默认下载路径
LOCAL_DIR_DEPOT_CLIENT = env.path("LOCAL_DIR_DEPOT_CLIENT", join(LOCAL_DIR_DEPOT, "client"))

"""********************************* 通用全局参数 ********************************"""

# 我就是云彩姬!
TITLE = env.str("TITLE", 'V2Ray云彩姬')

# 时区
TIME_ZONE_CN = pytz.timezone('Asia/Shanghai')
TIME_ZONE_NY = pytz.timezone('America/New_York')
