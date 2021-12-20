"""v2rss-service 脚手架入口"""
__all__ = ["Scaffold"]

from gevent import monkey

monkey.patch_all()
import time
import requests
import csv
import os
import sys
from BusinessCentralLayer.middleware.interface_io import SystemInterface
from BusinessCentralLayer.middleware.subscribe_io import select_subs_to_admin
from BusinessCentralLayer.middleware.redis_io import EntropyHeap
from BusinessLogicLayer.plugins.accelerator import (
    SubscribesCleaner,
    SubscribeParser,
)
from BusinessLogicLayer.utils import build
from BusinessLogicLayer.apis import (
    mining,
    entropy,
    runner,
    clear,
    ash,
)
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
    COMMAND_EXECUTOR,
    DynamicEnvironment,
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
        or: python main.py parse [<URL>]
        or: python main.py parse "[<URL>]"       当链接存在 & 符号时用引号将链接框起来
        or: python main.py parse [<URL>] --decode        启动 BASE64 自动解码程序，返回节点明文数据，默认开启。

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
    def mining(
            env: str = "development",
            silence: bool = True,
            power: int = 16,
            collector: bool = False,
            classifier: bool = False,
            source: str = "local",
            batch: int = 1,
    ):
        """
        运行 Collector 以及 Classifier 采集并过滤基层数据

        Usage: python main.py mining --env=production                       |在 GitHub Actions 中构建生产环境
        or: python main.py mining --silence=False                           |显式启动，在 linux 中运行时无效
        or: python main.py mining --power=4                                 |指定分类器运行功率
        or: python main.py mining --classifier --source=local               |启动分类器，指定数据源为本地缓存
        or: python main.py mining --classifier --source=remote --batch=1    |启动分类器，指定远程数据源
        or: python main.py mining --collector                               |启动采集器

        :param source: within [local remote] 指定数据源，仅对分类器生效
            - local：使用本地 Collector 采集的数据进行分类
            - remote：使用 SSPanel-Mining 母仓库数据进行分类（需要下载数据集）
        :param batch: batch 应是自然数，仅在 source==remote 时生效，用于指定拉取的数据范围。
            - batch=1 表示拉取昨天的数据（默认），batch=2 表示拉取昨天+前天的数据，以此类推往前堆叠
            - 显然，当设置的 batch 大于母仓库存储量时会自动调整运行了逻辑，防止溢出。
        :param env: within [development production]
        :param silence: 采集器是否静默启动，默认静默。
        :param power: 分类器运行功率。
        :param collector: 采集器开启权限，默认关闭。
        :param classifier: 分类器控制权限，默认关闭。
        :return:
        """
        if collector:
            mining.run_collector(env=env, silence=silence)

        if classifier:
            mining.run_classifier(power=power, source=source, batch=batch)

    @staticmethod
    def entropy(update: bool = False, remote: bool = False, check: bool = False):
        """
        采集队列的命令行管理工具。

        Usage: python main.py entropy   输出本机采集队列信息
        or: python main.py entropy --remote 输出``远程队列``的摘要信息
        or: python main.py entropy --upload 将``本机采集队列``辐射至远端，替换最新共享队列数据

        :param check: 检查本地执行队列的健康状态
        :param remote: 输出``远程队列``的摘要信息
        :param update: 将本地 action.py entropy 同步至共享任务队列
        :return:
        """
        if not check:
            entropy.preview(remote=remote)
        if update:
            entropy.update()
        if check:
            entropy.check(power=16)

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
    def spawn(
            silence: bool = True,
            power: int = None,
            join: bool = False,
            remote: bool = False,
    ):
        """
        并发执行本机所有采集器任务，每个采集器实体启动一次，并发数取决于本机硬件条件。

        Usage: python main.py spawn                 |启动本地 non-synergy 实例
        or: python main.py spawn --join             |启动本地所有可执行实例
        or: python main.py spawn --silence=False    |显式启动。这在 linux 系统被中禁止使用
        or: python main.py spawn --power=4          |指定并发数
        or: python main.py spawn --remote           |读取远程队列的运行实例
        :param silence:
        :param power:
        :param join:
        :param remote:
        :return:
        """
        # 检查运行配置
        _ConfigQuarantine(force=bool(COMMAND_EXECUTOR)).check_config(call_driver=not bool(COMMAND_EXECUTOR))

        logger.info("<ScaffoldGuider> Spawn || MainCollector")

        runner.spawn(
            silence=silence,
            power=power,
            join=join,
            remote=remote,
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

    @staticmethod
    def decouple(env: str = "development"):
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
        if env == "development":
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
        return clear.clear()

    @staticmethod
    def clean():
        return Scaffold.clear()

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
        or: python main.py server --debug    以 debug 模式启动 flask
        or: python main.py server --host=6500 --port="localhost"   指定运行端口启动服务

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
    def deploy(timer: bool = True, synergy: bool = True, dance: bool = True, collector: bool = False):
        """
        部署 V2RSS 后端服务。

        - 本接口仅提供定时任务和协同任务的权限，若想部署对外接口服务，需要使用 scaffold.router()
        - 部署多机后端服务推荐使用 python main.py deploy --synergy=False 解耦服务，也既使用该指令部署采集器，
        使用其他物理机部署 synergy 协同任务，除非服务器性能卓越，否则不推荐将 synergy 和 collector 放在同一个物理机上运行

        Usage: python main.py deploy                部署服务，默认开启 运行协同 和 定时采集
        or: python main.py deploy --synergy=False   禁用协同，不受理协同任务
        or: python main.py deploy --timer=False     禁用定时任务

        :param dance: 节拍同步。影响 collector 的 reset_task 逻辑。IF True 使用共享队列，ELSE 使用本地队列。
        :param timer: 定时任务权限，默认开启。
        :param collector: 采集器权限，默认关闭
        :param synergy: 破冰船协同任务权限，默认开启
        :return:
        """

        # The collector runs as a timing task,so `collector` is True, `timer` must be True.
        if collector is True:
            timer = True

        # Use `DynamicEnvironment` to radiate `beat_sync` startup parameters.
        if dance:
            os.environ["beat_dance"] = "remote"
            eh = EntropyHeap()
            # When you start `beat_sync` deploy for the first time (the remote queue is empty),
            # the local queue is used as the initial value of the remote queue.
            if eh.is_empty():
                logger.warning("<ScaffoldGuider> The remote tasks queue is empty. - "
                               f"name={eh.entropy_name}")
                Scaffold.entropy(update=True)

        # Check runtime settings.
        _ConfigQuarantine(force=True).run()

        # Startup process.
        SystemInterface.run(
            deploy_=True,
            enable_flask=False,
            enable_timed_task=timer,
            enable_synergy=synergy
        )

    @staticmethod
    def synergy(remote: str = None, workers: int = None):
        """
        部署 V2RSS 协同任务

        - 本接口运行的服务仅执行 synergy 任务
        - 也即运行此任务的物理机无需更新 action.py 配置队列，任务上下文信息由上游 deploy-collector 对象动态分发

        Usage: python main.py synergy 启动协同任务
        or: python main.py synergy --remote=https://selenium-hub:4444 使用 RemoteDriver 启动协同任务
        or: python main.py synergy --workers=2 设置并行任务数为 2

        :param workers: 并行任务数，正整数。默认为None，功率全开，手动指定时，workers 受限于弹性携程功率 power。
        :param remote: such as http://selenium-hub:4444
        :return:
        """
        # > docker-compose selenium_hub 访问地址
        #   - 如 http://selenium-hub:4444 传参优先级更高
        #   - IF docker-compose.yaml 中写明了环境变量此处无需声明。
        # > 若不指定 RemoteDriver 则使用 src/BusinessCentralLayer/chromedriver
        if remote:
            DynamicEnvironment.selenium_hub_executor = remote
        if isinstance(workers, int):
            workers = 1 if workers < 1 else workers

        _ConfigQuarantine(force=True).run()
        SystemInterface.run(
            deploy_=True,
            enable_flask=False,
            enable_timed_task=False,
            enable_synergy=True,
            workers=workers
        )

    @staticmethod
    def router(host="127.0.0.1", port=6500):
        """
        部署 V2RSS 接口服务

        - 运行 V2RSS 对外接口服务，使用 http 通信。推荐使用其他外部服务（如 nginx，bot）从 `127.0.0.1` 转发信息流。

        :param host:
        :param port:
        :return:
        """
        _ConfigQuarantine(force=True).run()
        SystemInterface.run(
            deploy_=True,
            enable_flask=True,
            enable_timed_task=False,
            enable_synergy=False,
            host=host,
            port=port
        )

    # TODO 以下配置在开源项目中隐去，请勿同步
    # ----------------------------------
    # Front-end debugging interface
    # ----------------------------------
    @staticmethod
    def panel():
        """
        打开 panel 调试面板。

        Usage: python main.py panel

        :return:
        """
        from BusinessViewLayer.panel.panel import startup_from_platform

        startup_from_platform()

    @staticmethod
    def ash():
        """
        一键拉取、合并、自动更新 Clash for Windows 订阅文件。

        1. 仅可在 Windows 操作系统上运行。
        2. 清洗订阅池，并将所有类型的节点分享链接合并转写为 Clash.yaml配置文件，
        借由 URL Scheme 自动打开 Clash 并下载更新配置文件。

        Usage: python main.py ash

        :return:
        """
        logger.info("<ScaffoldGuider> ash | Clash订阅堆一键生成脚本")

        # --------------------------------------------------
        # 参数清洗
        # --------------------------------------------------
        # if 'win' not in sys.platform:
        #     return

        # --------------------------------------------------
        # 运行脚本
        # --------------------------------------------------
        return ash(debug=True, decouple=True)
