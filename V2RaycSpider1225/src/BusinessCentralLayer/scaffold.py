"""v2rss-service 脚手架入口"""
__all__ = ["Scaffold"]

from gevent import monkey

monkey.patch_all()
import time
import requests
import csv
import os
import shutil
import sys

from BusinessCentralLayer.middleware.interface_io import SystemInterface
from BusinessCentralLayer.middleware.subscribe_io import select_subs_to_admin
from BusinessLogicLayer.apis.staff_mining import staff_api
from BusinessLogicLayer.cluster.slavers import __entropy__
from BusinessLogicLayer.plugins.accelerator import (
    booster,
    SubscribesCleaner,
    SubscribeParser,
)
from BusinessLogicLayer.utils import build
from BusinessCentralLayer.setting import (
    logger,
    DEFAULT_POWER,
    CHROMEDRIVER_PATH,
    REDIS_MASTER,
    SERVER_DIR_DATABASE_CACHE,
    SERVER_DIR_CLIENT_DEPORT,
    SERVER_PATH_DEPOT_VCS,
    SERVER_DIR_CACHE_BGPIC,
    REDIS_SLAVER_DDT,
    terminal_echo,
    SERVER_DIR_DATABASE_LOG,
    SERVER_DIR_SSPANEL_MINING,
    COMMAND_EXECUTOR,
)


class _ConfigQuarantine:
    """系统环境诊断工具"""

    def __init__(self, force: bool = False):
        self.root = [
            SERVER_DIR_CLIENT_DEPORT,
            SERVER_PATH_DEPOT_VCS,
            SERVER_DIR_DATABASE_CACHE,
            SERVER_DIR_CACHE_BGPIC,
        ]
        self.flag = False
        self.force = force

    def set_up_file_tree(self, root):
        """
        初始化 database 文件系统，创建各种可能用到的系统文件
        :param root:
        :return:
        """
        # 深度优先初始化系统文件
        for child_ in root:
            if not os.path.exists(child_):
                self.flag = True
                try:
                    # 初始化文件夹
                    if os.path.isdir(child_) or not os.path.splitext(child_)[-1]:
                        os.mkdir(child_)
                        logger.success(f"系统文件链接成功->{child_}")
                    # 初始化文件
                    else:
                        if child_ == SERVER_PATH_DEPOT_VCS:
                            try:
                                with open(
                                        child_, "w", encoding="utf-8", newline=""
                                ) as fpx:
                                    csv.writer(fpx).writerow(["version", "title"])
                                logger.success(f"系统文件链接成功->{child_}")
                            except Exception as ep:
                                logger.exception(f"Exception{child_}{ep}")
                except Exception as ep:
                    logger.exception(ep)

    def pending_selenium_hub(self, timeout: int = 120):
        start_ = time.time()
        while time.time() - start_ < timeout:
            try:
                session = requests.session()
                response = session.get(COMMAND_EXECUTOR)
                if response.status_code == 200:
                    logger.success(f"<ConfigQuarantine> Status of Selenium Hub:OK"
                                   f" | url={COMMAND_EXECUTOR}")
                    return True
                logger.warning(f"<ConfigQuarantine> Status of Selenium Hub:Pending"
                               f" | status_code={response.status_code} url={COMMAND_EXECUTOR}")
            except requests.exceptions.ConnectionError:
                logger.debug(f"<ConfigQuarantine> Waiting for Selenium Hub deployment...")
            except requests.exceptions.RequestException as e:
                logger.error(f"<ConfigQuarantine> Attempt to reconnect Selenium Hub"
                             f" | error={e}")
            time.sleep(5)

        logger.critical(f"<ConfigQuarantine> Invalid Selenium Hub operation object,"
                        f"and the V2RSS process was refused to run."
                        f" | url={COMMAND_EXECUTOR}")
        self._exit()

    def check_config(self, call_driver: bool = False):
        """
        检查用户配置是否残缺
        :param call_driver: 针对 ChromeDriver 配置情况的检查
        :return:
        """
        chromedriver_not_found_error = (
            "<ScaffoldGuider> ForceRun || ChromedriverNotFound ||"
            "未查找到chromedriver驱动，请根据技术文档正确配置\n"
            ">>> https://github.com/QIN2DIM/V2RayCloudSpider"
        )

        # if not all(SMTP_ACCOUNT.values()):
        #     logger.warning('您未正确配置<通信邮箱>信息(SMTP_ACCOUNT)')
        # if not SERVERCHAN_SCKEY:
        #     logger.warning("您未正确配置<Server酱>的SCKEY")
        if not all([REDIS_SLAVER_DDT.get("host"), REDIS_SLAVER_DDT.get("password")]):
            logger.warning("您未正确配置<Redis-Slave> 本项目资源拷贝功能无法使用，但不影响系统正常运行。")
        if not all([REDIS_MASTER.get("host"), REDIS_MASTER.get("password")]):
            logger.error("您未正确配置<Redis-Master> 此配置为“云彩姬”的核心组件，请配置后重启项目！")
            self._exit()

        # 当需要调用的接口涉及到driver操作时抛出
        if (
                call_driver
                and not os.path.exists(CHROMEDRIVER_PATH)
                and not COMMAND_EXECUTOR
        ):
            logger.error(chromedriver_not_found_error)
            self._exit()

        # 检查 docker-compose/swarm 中关于 selenium-hub 的接口心跳
        # 若 `status-code != 200`，则不允许程序运行
        if COMMAND_EXECUTOR:
            self.pending_selenium_hub()

    def run(self):
        """
        外部接口，用于便捷启动多种检测模式
        :return:
        """
        try:
            if [cq for cq in reversed(self.root) if not os.path.exists(cq)]:
                logger.warning("系统文件残缺！")
                logger.debug("启动<工程重构>模块...")
                self.set_up_file_tree(self.root)
            self.check_config()

        finally:
            if self.flag:
                logger.success(">>> 运行环境链接完成，请重启项目")
                logger.warning(">>> 提醒您正确配置Chrome及对应版本的ChromeDriver")
                self._exit()

    def _exit(self):
        if not self.force:
            sys.exit()


def within_error(flag_name: str, key_name: str, within_list: list):
    """

    :param flag_name:
    :param key_name:
    :param within_list:
    :return:
    """
    if key_name not in within_list:
        logger.error(
            f"<ScaffoldBuild> Wrong input parameter: "
            f"--{flag_name}=`{key_name}` @ "
            f"This parameter must be within {within_list}."
        )
        return False
    return True


class Scaffold:
    """
    v2rss-service 脚手架
        - 集成了各种后端服务常用的调试指令，并牵引了更加便捷的部署接口。
    """

    def __init__(self, env: str = "development"):
        self.cq = _ConfigQuarantine()

        if not within_error("env", env, ["development", "production"]):
            sys.exit()

        os.environ["V2RSS_ENVIRONMENT"] = env
        self.env = env

    def build(self):
        """
        [实验功能] 为 Ubuntu 操作系统用户自动下载 v2rss server 运行所需组件。



        :return:
        """
        # 配置工作环境
        build.run()
        # 初始化工作目录
        self.cq.run()

    # ----------------------------------
    # Tools for dev
    # ----------------------------------

    @staticmethod
    def parse(subscribe: str, decode: bool = True):
        """
        解析订阅链接/节点分享链接。

        返回订阅链接所映射的可用节点数及详细订阅信息。

        Usage: python main.py parse --url=[<URL>]
        Usage: python main.py parse [<URL>]
        Usage: python main.py parse '[<URL>]'       当链接存在 & 符号时用引号将链接框起来
        Usage: python main.py parse [<URL>] --decode        启动 BASE64 自动解码程序，返回节点明文数据
        :param decode: 解析订阅时进行自动 BASE64 解码
        :param subscribe: 需要解析的订阅链接
        :return:
        """
        terminal_echo(f"Parse {subscribe}", 1)

        # 检测缓存路径完整性
        if not os.path.exists(SERVER_DIR_DATABASE_CACHE):
            os.mkdir(SERVER_DIR_DATABASE_CACHE)

        # 调取API解析链接
        result = SubscribeParser(subscribe).parse_out(auto_base64=decode)
        body = result.get("body")
        if result.get("is_subscribe"):
            info = {}
            if not body:
                return False
            nodes = body["nodes"]

            # 节点数量 减去无效的注释项
            node_num = nodes.__len__() - 2 if nodes.__len__() - 2 >= 0 else 0
            info.update({"available nodes": node_num})

            # 缓存数据
            cache_path = os.path.join(SERVER_DIR_DATABASE_CACHE, "sub2node.txt")
            with open(cache_path, "w", encoding="utf8") as f:
                for node in nodes:
                    f.write(f"{node}\n")

            # 打印转义后的节点信息
            for node in reversed(nodes):
                terminal_echo(node, 1)
            terminal_echo("Detail:{}".format(info), 1)
        else:
            node = body["msg"]
            terminal_echo(node, 1)

    @staticmethod
    def remain():
        """
        获取订阅池状态。

        Usage: python main.py remain

        :return:
        """
        tracer = [
            f"{tag[0]}\n采集类型：{info_[0]}\n存活数量：{tag[-1]}"
            for info_ in select_subs_to_admin(select_netloc=None, _debug=False)[
                "info"
            ].items()
            for tag in info_[-1].items()
        ]
        for i, tag in enumerate(tracer):
            print(f">>> [{i + 1}/{tracer.__len__()}]{tag}")

    @staticmethod
    def mining():
        """
        启动一次对 SSPanel-Uim 站点的检索与分类。

        该项任务需要为国内IP开启系统代理。

        Usage: python main.py mining

        :return:
        """
        use_collector = staff_api.is_first_run()
        classify_dir, staff_info = staff_api.go(
            debug=False,
            silence=True,
            power=os.cpu_count() * 2,
            identity_recaptcha=False,
            use_collector=use_collector,
            use_checker=True,
            use_generator=False,
        )
        staff_api.refresh_cache(mode="de-dup")
        print(f"\n\nSTAFF INFO\n{'_' * 32}")
        for element in staff_info.items():
            for i, tag in enumerate(element[-1]):
                print(f">>> [{i + 1}/{len(element[-1])}]{element[0]}: {tag}")
        print(f">>> 文件导出目录: {classify_dir}")

    @staticmethod
    def entropy():
        """
        在控制台输出本机采集队列信息。

        Usage: python main.py entropy

        :return:
        """
        for i, host_ in enumerate(__entropy__):
            print(f">>> [{i + 1}/{__entropy__.__len__()}]{host_['name']}")
            print(f"注册链接: {host_['register_url']}")
            print(f"存活周期: {host_['life_cycle']}天")
            print(
                f"采集类型: {'&'.join([f'{j[0].lower()}' for j in host_['hyper_params'].items() if j[-1]])}\n"
            )

    @staticmethod
    def ping():
        """
        测试数据库连接。

        Usage: python main.py ping

        :return:
        """
        from BusinessCentralLayer.middleware.redis_io import RedisClient
        logger.info(f"<ScaffoldGuider> Ping || {RedisClient().test()}")

    @staticmethod
    def spawn(join: bool = False):
        """
        并发执行本机所有采集器任务，每个采集器实体启动一次，并发数取决于本机硬件条件。

        Usage: python main.py spawn 启动常规实例
        or: python main.py spawn --join 启动 常规实例 + synergy 运行实例

        :param join:
        :return:
        """
        _docker = (
            __entropy__
            if join
            else [i for i in __entropy__ if not i["hyper_params"].get("co-invite")]
        )
        _ConfigQuarantine(force=bool(COMMAND_EXECUTOR)).check_config(call_driver=not bool(COMMAND_EXECUTOR))
        logger.info("<ScaffoldGuider> Spawn || MainCollector")
        # 剔除运行在 co-invite 模式的实例
        booster(
            docker=_docker,
            silence=False,
            power=DEFAULT_POWER,
            assault=True,
        )

    @staticmethod
    def overdue():
        """
        对指向的订阅池执行一次过时链接的清洗任务。

        Usage: python main.py overdue

        :return:
        """
        logger.info("<ScaffoldGuider> Overdue || Redis DDT")
        SystemInterface.ddt()

    def decouple(self):
        """
        扫描所指订阅池，清除无效订阅。

        无效订阅规则：
            - 解析异常，订阅映射站点瘫痪；
            - 订阅过期，使用 pre-clean 机制进行欲清除；
            - 订阅耦合，被客户端成功获取但未被正常删除的订阅；
        Usage: python main.py decouple

        :return:
        """
        logger.info("<ScaffoldGuider> Decouple || General startup")
        if self.env == "development":
            SubscribesCleaner(debug=True).interface(power=DEFAULT_POWER)
        else:
            SubscribesCleaner(debug=False).interface(power=DEFAULT_POWER)
            logger.success("<ScaffoldGuider> Decouple || General startup")

    @staticmethod
    def clear():
        """
        清理系统运行缓存。

        清理项包括过期运行日志,以及由 mining 指令产生的采集输出

        Usage: python main.py clear

        :return:
        """
        _permission = {
            "logs": input(terminal_echo("是否清除所有运行日志[y]?", 2)),
            "cache": input(terminal_echo("是否清除所有运行缓存[y]?", 2)),
        }

        # 清除日志 ~/database/logs
        if os.path.exists(SERVER_DIR_DATABASE_LOG) and _permission["logs"].startswith(
                "y"
        ):
            history_logs = os.listdir(SERVER_DIR_DATABASE_LOG)
            for _log_file in history_logs:
                if len(_log_file.split(".")) > 2:
                    _log_path = os.path.join(SERVER_DIR_DATABASE_LOG, _log_file)
                    os.remove(_log_path)
                    terminal_echo(f"清除运行日志-->{_log_path}", 3)

        # 清除运行缓存 ~/database/
        if _permission["cache"].startswith("y"):
            cache_blocks = {
                # ~/database/temp_cache/
                SERVER_DIR_DATABASE_CACHE,
                # ~/database/staff_hosts/
                SERVER_DIR_SSPANEL_MINING,
            }

            for block in cache_blocks:
                # 扫描文件
                if os.path.exists(block):
                    _files = [os.path.join(block, i) for i in os.listdir(block)]
                    # 清除文件
                    for _file in _files:
                        if os.path.isfile(_file):
                            os.remove(_file)
                        else:
                            shutil.rmtree(_file)
                            os.mkdir(_file)
                        terminal_echo(f"清除运行缓存-->{_file}", 3)
            terminal_echo("系统缓存文件清理完毕", 1)

    # ----------------------------------
    # Backend service interface
    # ----------------------------------
    @staticmethod
    def server(port: int = None, host: str = None, debug: bool = False):
        """
        启动 V2RSS 后端服务。

        当不指定参数时，v2rss server 自动读取 config.yaml 中关于服务运行的配置：
            - ENABLE_SERVER     是否开启 flask
            - LAUNCH_INTERVAL   定时任务的执行间隔
            - ENABLE_DEPLOY     各种定时任务的开关

        Usage: python main.py server    以系统默认配置启动服务
        Usage: python main.py server --debug    以 debug 模式启动 flask
        Usage: python main.py server --host=6500 --port="localhost"   指定运行端口启动服务

        :param debug: 以 debug 模式启动 flask。注意，若配置文件中的 ENABLE_SERVER: False，此配置项无效。
        :param port: v2rss server 后端服务 (Flask) 的部署端口，默认 port=API_PORT(6500)
        :param host:
        v2rss server 后端服务 (Flask) hostname ，默认 host=OPEN_HOST 策略。

        在 Windows 操作系统上调试或 debug=True 时，默认 hostname="localhost"。
        在其他操作系统上运行且 debug=False 时，默认 hostname="0.0.0.0"。

        :return:
        """
        _ConfigQuarantine().run()
        SystemInterface.run(deploy_=True, port=port, host=host, debug=debug)

    @staticmethod
    def deploy(timer: bool = True, synergy: bool = True, collector: bool = False):
        """
        部署 V2RSS 后端服务。

        本接口仅提供定时任务和协同任务的权限，若想部署对外接口服务，需要使用 scaffold.router()

        Usage: python main.py deploy                部署服务，与 server 指令完全一致
        or: python main.py deploy --synergy=False   禁用协同，不受理协同任务
        or: python main.py deploy --timer=False     禁用定时任务

        :param timer: 定时任务权限，默认开启。
        :param collector: 采集器权限，默认关闭
        :param synergy: 破冰船协同任务权限，默认开启
        :return:
        """
        if collector is True:
            timer = True
        _ConfigQuarantine(force=True).run()
        SystemInterface.run(
            deploy_=True,
            enable_flask=False,
            enable_timed_task=timer,
            enable_synergy=synergy
        )

    @staticmethod
    def synergy():
        _ConfigQuarantine(force=True).run()
        SystemInterface.run(
            deploy_=True,
            enable_flask=False,
            enable_timed_task=False,
            enable_synergy=True
        )

    @staticmethod
    def router(host="127.0.0.1", port=6500):
        _ConfigQuarantine(force=True).run()
        SystemInterface.run(
            deploy_=True,
            enable_flask=True,
            enable_timed_task=False,
            enable_synergy=False,
            host=host,
            port=port
        )
