# -*- coding: utf-8 -*-
# Time       : 2021/12/25 16:56
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from gevent import monkey

monkey.patch_all()
import os
from services.deploy import SynergyScheduler
from apis.scaffold import entropy, runner, services, mining, pool, install
from services.middleware.subscribe_io import SubscribeManager
from services.settings import logger, ROUTER_HOST, ROUTER_PORT, DETACH_SUBSCRIPTIONS
from services.utils import ToolBox


class Scaffold:

    # ----------------
    # 基础指令
    # ----------------
    @staticmethod
    def build():
        """[DEPRECATED]"""
        logger.info(
            ToolBox.runtime_report(
                motive="SKIP",
                action_name="ScaffoldInstall",
                message="请使用 `install` 指令初始化项目依赖，`build` 已弃用",
            )
        )

    @staticmethod
    def install():
        """拉取项目依赖"""
        install.run()

    @staticmethod
    def ping():
        """测试 RedisNode 连接"""
        response = SubscribeManager().ping()
        logger.info(
            ToolBox.runtime_report(
                motive="PING",
                action_name="ScaffoldPing",
                message="欢迎使用 - V2RSS云彩姬 - " if response else "网络连接异常",
            )
        )

    # ----------------
    # 订阅管理
    # ----------------
    @staticmethod
    def pool(overdue: bool = False, decouple: bool = False, status: bool = True):
        """
        订阅池管理

        :param status: 输出订阅池状态（不指定执行参数时默认输出）
        :param decouple: 清除失效订阅（decouple 与 overdue 仅能同时执行一项）
        :param overdue: 清除过期订阅（decouple 与 overdue 仅能同时执行一项）
        :return:
        """
        if overdue:
            return pool.overdue()
        if decouple:
            return pool.decouple()
        if status:
            return pool.status()

    # ----------------
    # 系统任务
    # ----------------
    @staticmethod
    def deploy(collector: bool = None, decoupler: bool = None):
        """
        部署定时任务

        Usage: python main.py deploy
        ______________________________________________________________________
        or: python main.py deploy --collector=False         |强制关闭采集器
        or: python main.py deploy --collector               |强制开启采集器
        or: python main.py deploy --collector --decoupler   |强制开启采集器和订阅解耦器
        ______________________________________________________________________
        >> 默认不使用命令行参数，但若使用参数启动项目，命令行参数的优先级高于配置文件
        >> 初次部署需要先运行 ``python main.py entropy --update`` 初始化远程队列

        :param collector:强制开启/关闭采集器
        :param decoupler:强制开启/关闭订阅解耦器
        :return:
        """
        services.SystemCrontab(
            collector=collector, decoupler=decoupler
        ).service_scheduler()

    @staticmethod
    def synergy():
        """部署协同工作节点"""
        synergy = SynergyScheduler()
        synergy.deploy()
        synergy.start()

    @staticmethod
    def server(host: str = None, port: int = None, detach: bool = None):
        """
        ``PRODUCTION`` 接口服务器（仅在linux部署时生效）

        Usage: python main.py server
        ______________________________________________________________________
        or: python main.py server --host=127.0.0.1 --port=22332   |指定端口运行
        or: python main.py server --detach=False                  |订阅耦合
        ______________________________________________________________________

        ## 额外声明

        >> 为了在生产环境下获得最佳性能，默认禁用 ``debug`` 和 ``access_log``。

        >> Sanic 可指定 workers 充分利用多核性能，也可直接指定 --fast 参数直接拉满，子进程间可以负载均衡。
        而云彩姬服务端口仅供个人使用，不存在高并发的应用场景，也即 workers=1 既可（默认），无需更改指定，徒增功耗。

        >> 若要运行开发环境调试代码，请手动运行 ``examples/server_dev.py`` 或 ``src/services/app/server``

        :param detach: 分离订阅（默认 True）。此项为True时，通过接口层申请的订阅才会被系统删除。
        意味着在接口调试时，指定 ``detach=False`` 被请求的链接不会被删除。
        :param port:
        :param host:

        :return:
        """
        _host = ROUTER_HOST if host is None else host
        _p = ROUTER_PORT if port is None else port
        if detach is not False:
            os.environ[DETACH_SUBSCRIPTIONS] = "True"

        _command = (
            "sanic services.app.server.app.app "
            f"{'--host ' + _host if _host in ['127.0.0.1', '0.0.0.0'] else ''} "
            f"{'-p ' + str(_p) if 1024 <= _p <= 65535 else ''}"
        )

        # 假设不会被注入
        logger.info(f"{_command} | detach={bool(os.getenv(DETACH_SUBSCRIPTIONS))}")
        os.system(_command)

    @staticmethod
    def entropy(
        update: bool = False, remote: bool = False, check: bool = False, cap: int = None
    ):
        """
        采集队列的命令行管理工具。

        Usage: python main.py entropy
        ______________________________________________________________________
        or: python main.py entropy --remote |输出 ``远程执行队列`` 的摘要信息
        or: python main.py entropy --update |将 ``本地执行队列`` 辐射至远端
        or: python main.py entropy --check  |检查 ``本地执行队列`` 的健康状态
        or: python main.py entropy --cap    |将 ``POOL_CAP`` 队列容量映射到远端
        or: python main.py entropy --cap=8  |手动修改远程队列容量
        ______________________________________________________________________

        ## Remote EntropyHeap

        在 v6.0.1-alpha 之后，采集器默认使用<远程共享队列>同步待办任务。意味着采集节点不再关心
        当前物理服务器中的 ``action.py`` 的 entropy 列表，而是 Remote EntropyHeap 对象。

        Remote EntropyHeap Object 存储着若干个采集实例的上下文摘要信息，采集器读取这些数据后，
        根据一系列的生产逻辑，生成符合特征的实例，进而启动采集任务。

        手动修改 Remote EntropyHeap 需要执行 ``python main.py entropy --update`` 更新
        远程共享队列，此时所有采集器节点都会使用新的任务队列。这种切换是立即执行的，将在采集器
        下一次任务加载时生效。

        项目初始化时 Remote EntropyHeap 并不存在，直接执行脚手架 deploy 指令部署采集器后必然
        会保持空转，也即需要在项目初始化后执行一次 ``python main.py entropy --update`` 用以
        创建 Remote EntropyHeap，这样采集器才会读取到待办任务。

        ``--update`` 的逻辑是将本地的 entropy 辐射到远端，一般在管理员服务器上使用（比如你的笔记本）。
        在后期运维中，管理员发现新的可执行实例时，可以手动编写上下文摘要信息，录入 entropy，再使用此指令
        同步任务队列。

        ## Unified Pool Capacity

        在 v6.0.2-alpha 之后，可以通过脚手架指令 `entropy --cap` 手动指定远程队列容量，同步操作是立即完成的，
        将在采集器下次任务发起时的 ``preload`` 预加载阶段生效。

        此指令不会覆盖本地 ``POOL_CAP`` 全局变量的值，也不会覆写任一节点的配置文件，而是创建或更新一个指定的 Redis-Key。

        :param cap:
        :param check:
        :param remote:
        :param update:
        :return:
        """
        if cap:
            return entropy.cap(cap)
        if not check:
            entropy.preview(remote=remote)
        if update:
            entropy.update()
        if check:
            entropy.check()

    # ----------------
    # 高级指令
    # ----------------
    @staticmethod
    @logger.catch()
    def spawn(
        silence: bool = True, power: int = None, remote: bool = False, safe: bool = False
    ):
        """
        并发执行本机所有采集器任务，每个采集器实体启动一次，并发数取决于本机硬件条件。

        Usage: python main.py nest
        ______________________________________________________________________
        or: python main.py nest --power=4          |指定并发数
        or: python main.py nest --remote           |读取远程队列的运行实例
        or: python main.py nest --safe             |安全启动，过滤掉需要人机验证的任务
        ______________________________________________________________________

        :param safe: 安全启动，过滤掉需要人机验证的实例
        :param silence:静默启动
        :param power:指定并发数
        :param remote:将订阅源标记为 ``远程队列``
        :return:
        """
        runner.spawn(silence=silence, power=power, join=False, remote=remote, safe=safe)

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

        Usage: python main.py mining
        ______________________________________________________________________
        or: python main.py mining --env=production                |在 GitHub Actions 中构建生产环境
        or: python main.py mining --silence=False                 |显式启动，在 linux 中运行时无效
        or: python main.py mining --power=4                       |指定分类器运行功率
        or: python main.py mining --classifier --source=local     |启动分类器，指定数据源为本地缓存
        or: python main.py mining --classifier --source=remote    |启动分类器，指定远程数据源
        or: python main.py mining --collector                     |启动采集器
        ______________________________________________________________________

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
