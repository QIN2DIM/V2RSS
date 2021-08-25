"""
读取yaml配置文件，生成全局静态变量。
"""
__all__ = ['SINGLE_DEPLOYMENT', 'ENABLE_DEPLOY', 'ENABLE_KERNEL', 'ENABLE_SERVER',
           'ENABLE_DEBUG', 'ENABLE_REBOUND', 'SINGLE_TASK_CAP', 'LAUNCH_INTERVAL', 'REDIS_MASTER', 'REDIS_SLAVER_DDT',
           'MYSQL_CONFIG', 'API_HOST', 'API_DEBUG', 'API_THREADED', 'API_PORT', 'OPEN_HOST', 'GARDENER_HOST',
           'ROUTE_API', 'SEQ_TEST', 'CRAWLER_SEQUENCE', 'SMTP_ACCOUNT', 'SERVERCHAN_SCKEY', 'REDIS_SECRET_KEY',
           'PROJECT_NUM', 'VERSION', 'TIME_ZONE_CN', 'TIME_ZONE_NY', 'DEFAULT_POWER', 'Fore', 'terminal_echo']

import os
import shutil
import sys
from datetime import datetime

import colorama
import pytz
import yaml

# 开启调试台彩色输出模式
colorama.init(autoreset=True)
Fore = colorama.Fore


def terminal_echo(msg: str, level: int):
    print(f"[{str(datetime.now()).split('.')[0]}]", end=' ')
    if level == 1:
        print(colorama.Fore.GREEN + "[✓]", end=' ')
    elif level == 0:
        print(colorama.Fore.RED + "[×]", end=' ')
    # 阻塞任务
    elif level == 2:
        print(colorama.Fore.BLUE + "[...]", end=' ')
    # debug
    elif level == 3:
        print(colorama.Fore.CYAN + "[*]", end=' ')
    print(msg)
    return ">"


# ---------------------------------------------------
# TODO 配置文件索引
# 默认的单机配置文件为 config.yaml
# ---------------------------------------------------

# 若在单机上开启多个进程的任务，既每个进程应对应一个启动配置文件（.yaml）则需改动此处user_指向的文件名，如：
# config_1.yaml   user_= os.path.join(os.path.dirname(__file__), 'config_1.yaml')
# config_master.yaml   user_= os.path.join(os.path.dirname(__file__), 'config_master.yaml')
user_ = os.path.join(os.path.dirname(__file__), 'config.yaml')

# 配置模板的文件名 无特殊需求请不要改动
sample_ = os.path.join(os.path.dirname(__file__), 'config-sample.yaml')

try:
    if not os.path.exists(sample_):
        terminal_echo("系统配置模板文件(config-sample.yaml)缺失", 0)
        print(">>> 请不要删除系统生成的配置模板config-sample.yaml，确保它位于工程根目录下")
        raise FileNotFoundError

    if os.path.exists(sample_) and not os.path.exists(user_):
        terminal_echo("系统配置文件(config.yaml)缺失", 0)
        shutil.copy(sample_, user_)
        terminal_echo("生成配置文件-->./src/config.yaml", 1)
        print(">>> 请根据docs配置启动参数 https://github.com/QIN2DIM/V2RayCloudSpider")
        sys.exit()

    if os.path.exists(sample_) and os.path.exists(user_):
        # 读取yaml配置变量
        with open(user_, 'r', encoding='utf8') as stream:
            config_ = yaml.safe_load(stream.read())
            if __name__ == '__main__':
                terminal_echo("读取配置文件-->./src/config.yaml", 1)
                print(config_)
except FileNotFoundError:
    try:
        import requests
        from requests import exceptions as res_error

        res_ = requests.get("https://curly-shape-d178.qinse.workers.dev/https://raw.githubusercontent.com/"
                            "QIN2DIM/V2RayCloudSpider/master/V2RaycSpider1225/src/config-sample.yaml")
        with open(sample_, 'wb') as fp:
            fp.write(res_.content)
        terminal_echo("配置模板拉取成功,请重启项目", 1)
    except (res_error.ConnectionError, res_error.HTTPError, res_error.RequestException) as e_:
        terminal_echo("配置模板自动拉取失败，请检查本地网络", 0)
        print(f">>> error:{e_}")
    finally:
        sys.exit()

"""
================================================ ʕ•ﻌ•ʔ ================================================
                            (·▽·)欢迎使用V2Ray云彩姬，请跟随提示合理配置项目启动参数
================================================ ʕ•ﻌ•ʔ ================================================
# TODO  2020/11/22
#  -- Modify
#       -- Panel -> UpdatedModule
#       -- Optimize -> Atomic operation
#  -- Expand -> action slaver


# TODO  v_1.0.2.11162350.11-beta
#  --请不要在<小带宽的国内云服务器>上部署此项目，推荐利用性能闲置的非大陆IP的VPS运行项目（非生产环境）
#  --若您的服务器配置 ~= `Linux 1xCPU 1GxRAM` 请勿在生产环境中开启coroutine_speed_up
#  --若您的服务器配置过于豪华或至少有 2xCPU 2GxRAM，请将所有加速特效拉满（脚本引入了一定的鲁棒均衡模组，可以保证稳定采集）

# TODO  v_5.0.3-beta
# -- 尝试引入6进程多哨兵模式

"""

# TODO (√) 强制填写；(*)可选项
# ---------------------------------------------------
# TODO (√) Function Authority -- 功能权限
# ---------------------------------------------------

# SINGLE_DEPLOYMENT 部署模式，单机部署True(默认)，分布式False
SINGLE_DEPLOYMENT = config_['SINGLE_DEPLOYMENT']

# ENABLE_DEPLOY 单节点部署定时任务开关
ENABLE_DEPLOY: dict = config_['ENABLE_DEPLOY']

# ENABLE_DEPLOY 服务器内核开关
ENABLE_KERNEL: dict = config_['ENABLE_KERNEL']

# ENABLE_SERVER 部署Flask
ENABLE_SERVER: bool = config_['ENABLE_SERVER']

# ENABLE_COROUTINE 协程加速
# ENABLE_COROUTINE: bool = config_['ENABLE_COROUTINE']

# ENABLE_DEBUG Flask DEBUG
ENABLE_DEBUG: bool = not ENABLE_DEPLOY

# ENABLE_REBOUND 数据回弹
# 当master server宕机后，将slave中的订阅清洗后传回。
# 该选项会反转主从关系，仅在主机数据丢失情况下手动开启。
# 在完成数据覆盖后应立即将ENABLE_REBOUND置False后重启项目。
ENABLE_REBOUND: bool = config_['ENABLE_REBOUND']

# ---------------------------------------------------
# TODO (√)SINGLE_TASK_CAP -- 单类订阅的队列容载极限
# 当某种链接的数量达到这个阈值则不会启动该类链接的采集任务
# <Performance limit of 1xCPU 1GRAM VPS KVM>
# Defaults type:int = 25
# 个人使用 推荐SINGLE_TASK_CAP不超过3
# ---------------------------------------------------
SINGLE_TASK_CAP: int = config_['SINGLE_TASK_CAP']

# ---------------------------------------------------
# TODO (√)DEPLOY_INTERVAL -- schedule任务间隔,单位秒（s）
# 定时任务中采集任务频次： 1轮/INTERVAL_ACTION
# Defaults type:int = 5 * 60 s 既30分钟
#
# 定时任务中数据备份/过期移除频次： 1轮/INTERVAL_REFRESH
# Defaults type:int = 60 * 60 s 既1小时

# 定时任务中数据解耦/检查频次： 1轮/INTERVAL_REFRESH
# Defaults type:int = 1 * 60 s 既1分钟

# 为保证系统高可用性，请不要让任务巡回频次低于以上预设值
# ---------------------------------------------------
LAUNCH_INTERVAL: dict = config_['LAUNCH_INTERVAL']

# ---------------------------------------------------
# TODO (√)Redis Cluster Configuration(SSH-BASE)
# 若您不知道如何配置Redis远程连接，请自行搜索或↓
# https://shimo.im/docs/5bqnroJYDbU4rGqy/
# ---------------------------------------------------

# TODO (√)Settings of the Master-Redis responsible for leading the workflow
REDIS_MASTER: dict = config_['REDIS_MASTER']

# TODO (*)Setting of the Slave-Redis responsible for data disaster tolerance（DDT）
REDIS_SLAVER_DDT: dict = config_['REDIS_SLAVER_DDT']

# TODO (x)This configuration is not applicable in the current version
MYSQL_CONFIG: dict = config_['MYSQL_CONFIG']

# ---------------------------------------------------
# TODO (√)API for Flask(SSH-BASE)
# ---------------------------------------------------
API_HOST: str = REDIS_MASTER["host"]
API_DEBUG: bool = ENABLE_DEBUG
API_THREADED: bool = True
API_PORT: int = config_['API_PORT']
"""
Audit: Binding to all interfaces detected with hardcoded values

 Binding to all network interfaces can potentially open up a
 service to traffic on unintended interfaces, that may not be 
 properly documented or secured. This can be prevented by 
 changing the code so it explicitly only allows access from localhost.

 When binding to `0.0.0.0`, you accept incoming 
 connections from anywhere. During development, an 
 application may have security vulnerabilities making it 
 susceptible to SQL injections and other attacks. Therefore 
 when the application is not ready for production, accepting 
 connections from anywhere can be dangerous.

 It is recommended to use `127.0.0.1` or local host during 
 development phase. This prevents others from targeting 
 your application and executing SQL injections against your project.
"""
OPEN_HOST: str = "127.0.0.1" if API_DEBUG or "win" in sys.platform else "0.0.0.0"
# ---------------------------------------------------
# TODO (√)The domain name used to deploy the gardener
# 园丁系统部署域名，当启动该项功能时，必须配置如: www.bbq.club
# 由于性能受限，该域名必须为当前主机的域名
# ---------------------------------------------------
GARDENER_HOST: str = config_['GARDENER_HOST']
# ---------------------------------------------------
# 路由接口（公开）
# ---------------------------------------------------
ROUTE_API = {
    "capture_subscribe": "/v2raycs/api/capture_subscribe",
    "version_manager": "/v2raycs/api/version_manager",
    "get_subs_num": "/v2raycs/api/get_sbus_num"
}
# ---------------------------------------------------
# 任务队列
# ---------------------------------------------------
SEQ_TEST = {
    "v2ray": True,
    "ssr": True,
    "trojan": False,
}
CRAWLER_SEQUENCE = [i[0].lower() for i in SEQ_TEST.items() if i[-1]]
# ---------------------------------------------------
# TODO (*)Noticer -- 用于发送panic信息警报，默认发送给自己
# 1. 当只需要发送给自己时推荐使用SERVER酱，两种通讯方式SERVER酱优先级更高
# 2. 此项非必要填写，若为空则不会发送警告信息
# ---------------------------------------------------
# ---------------------------------------------------
# TODO > 使用Email推送-推荐使用QQ邮箱，开启邮箱SMTP服务教程如下
# https://service.mail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1001256
# ---------------------------------------------------
SMTP_ACCOUNT: dict = config_['SMTP_ACCOUNT']

# ---------------------------------------------------
# TODO > 使用<SERVER酱>推送，请在SERVER_CHAN_SCKEY填写自己的Key
# http://sc.ftqq.com/3.version
# ---------------------------------------------------
SERVERCHAN_SCKEY: str = config_['SERVERCHAN_SCKEY']

# ---------------------------------------------------
# TODO (√)CHROMEDRIVER_PATH -- ChromeDriver的路径
#  本项目依赖google-chrome驱动插件，请确保您的开发环境中已经安装chrome以及对应版本的chromedriver

# 1. 配置google-chrome开发环境
# 1.1 安装Chrome
# 若无特殊需求请直接拉取最近版程序
# >> Windows -> https://www.google.cn/chrome/index.html
# >> Linux -> https://shimo.im/docs/5bqnroJYDbU4rGqy/

# 1.2 安装chromedriver
# 查看chrome版本并安装对应版本的匹配操作系统的chromedriver。
# >> http://npm.taobao.org/mirrors/chromedriver/

# 1.3 配置环境变量
# （1）将下载好的对应版本的chromedriver放到工程`./BusinessCentralLayer/`目录下
# （2）配置Chrome环境变量，Windows编辑系统环境变量Path，定位到Application文件夹为止，示例如下：
#      C:\Program Files\Google\Chrome\Application

# 2. 注意事项
#   -- 本项目基于Windows环境开发测试，Linux环境部署运行，若您的系统基于MacOS或其他，请根据报错提示微调启动参数。
#   -- 若您的Chrome安装路径与上文所述不一致，请适当调整。
#   -- 若您不知如何查看Chrome版本或在参考blog后仍遇到预料之外的问题请在issue中留言或通过检索解决。
#       >> Project：https://github.com/QIN2DIM/V2RayCloudSpider
# ---------------------------------------------------

"""
================================================== ʕ•ﻌ•ʔ ==================================================
                        如果您并非<V2RayCloudSpider>项目开发者 请勿修改以下变量的默认参数
================================================== ʕ•ﻌ•ʔ ==================================================

                                            Enjoy it -> ♂ main.py
"""
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
PROJECT_NUM = "1225"
VERSION = "5.1.0"
# ---------------------------------------------------
# 时区
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")
TIME_ZONE_NY = pytz.timezone("America/New_York")

# 采集器默认并发数
DEFAULT_POWER = os.cpu_count()

# 任务开关
if not ENABLE_DEPLOY['global']:
    for reset_ in ENABLE_DEPLOY['tasks'].items():
        ENABLE_DEPLOY['tasks'][reset_[0]] = False

# 主从反转
if ENABLE_REBOUND:
    REDIS_MASTER, REDIS_SLAVER_DDT = REDIS_SLAVER_DDT, REDIS_MASTER
