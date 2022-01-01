# -*- coding: utf-8 -*-
# Time       : 2021/12/25 16:56
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

from gevent import monkey

monkey.patch_all()
from apis.scaffold import (
    entropy,
    runner,
    services,
    mining
)
from services.middleware.subscribe_io import SubscribeManager
from services.settings import (
    logger, POOL_CAP, ROUTER_HOST, ROUTER_PORT
)
from services.utils import ToolBox, build
from services.cluster import decouple


class Scaffold:
    def __init__(self):
        pass

    @staticmethod
    def build(force: bool = None):
        """
        在 Ubuntu 白环境下拉取 chromedriver 、google-chrome 并将 chromedriver 放到规定路径下

        :param force: 若环境中已存在 google-chrome 则卸载重装最新稳定版
        :return:
        """
        build(force=force)

    @staticmethod
    def ping():
        """
        测试 RedisNode 连接

        :return:
        """
        response = SubscribeManager().ping()
        logger.info(ToolBox.runtime_report(
            motive="PING",
            action_name="ScaffoldPing",
            message="欢迎使用 - V2RSS云彩姬 - " if response else "网络连接异常"
        ))

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
    @logger.catch()
    def decouple():
        """
        清除无效订阅

        :return:
        """
        logger.info(ToolBox.runtime_report(
            motive="DECOUPLE",
            action_name="ScaffoldDecoupler",
            message="Clearing invalid subscriptions..."
        ))
        decouple(debug=True)

    @staticmethod
    @logger.catch()
    def overdue():
        """
        清除过期订阅

        :return:
        """
        try:
            pool_len = SubscribeManager().refresh()
            logger.debug(ToolBox.runtime_report(
                motive="OVERDUE",
                action_name="RemotePool | SpawnRhythm",
                message="pool_status[{}/{}]".format(pool_len, POOL_CAP)
            ))
        except ConnectionError:
            pass

    @staticmethod
    def entropy(
            update: bool = False,
            remote: bool = False,
            check: bool = False
    ):
        """
        采集队列的命令行管理工具。

        Usage: python main.py entropy
        ______________________________________________________________________
        or: python main.py entropy --remote 输出 ``远程执行队列`` 的摘要信息
        or: python main.py entropy --update 将 ``本地执行队列`` 辐射至远端
        or: python main.py entropy --check 检查 ``本地执行队列`` 的健康状态

        :param check:
        :param remote:
        :param update:
        :return:
        """
        if not check:
            entropy.preview(remote=remote)
        if update:
            entropy.update()
        if check:
            entropy.check()

    @staticmethod
    @logger.catch()
    def pool():
        """
        获取订阅的活跃状态

        :return:
        """
        pool_status = SubscribeManager().get_pool_status()
        ToolBox.echo(str(pool_status) if pool_status else "无可用订阅", 1 if pool_status else 0)

    @staticmethod
    @logger.catch()
    def spawn(
            silence: bool = True,
            power: int = None,
            remote: bool = False,
            safe: bool = False,
    ):
        """
        并发执行本机所有采集器任务，每个采集器实体启动一次，并发数取决于本机硬件条件。

        Usage: python main.py nest
        ______________________________________________________________________
        or: python main.py nest --power=4          |指定并发数
        or: python main.py nest --remote           |读取远程队列的运行实例
        or: python main.py nest --safe             |安全启动，过滤掉需要人机验证的任务

        :param safe: 安全启动，过滤掉需要人机验证的实例
        :param silence:静默启动
        :param power:指定并发数
        :param remote:将订阅源标记为 ``远程队列``
        :return:
        """
        runner.spawn(
            silence=silence,
            power=power,
            join=False,
            remote=remote,
            safe=safe
        )

    @staticmethod
    def deploy(collector: bool = None, decoupler: bool = None):
        """
        部署定时任务

        Usage: python main.py deploy
        ______________________________________________________________________
        or: python main.py deploy --collector=False         |强制关闭采集器
        or: python main.py deploy --collector               |强制开启采集器
        or: python main.py deploy --collector --decoupler   |强制开启采集器和订阅解耦器

        >> 默认不使用命令行参数，但若使用参数启动项目，命令行参数的优先级高于配置文件
        >> 初次部署需要先运行 ``python main.py entropy --update`` 初始化远程队列

        :param collector:强制开启/关闭采集器
        :param decoupler:强制开启/关闭订阅解耦器
        :return:
        """
        services.SystemService(
            enable_scheduler=True,
            collector=collector,
            decoupler=decoupler
        ).startup()

    @staticmethod
    def synergy():
        """
        部署协同工作节点

        :return:
        """
        services.SystemService(
            enable_synergy=True,
        ).startup()

    @staticmethod
    def router(debug=False, access_log=True):
        """
        部署接口服务器

        Usage: python main.py router
        ______________________________________________________________________
        or: python main.py router --access_log=False        |禁用访问日志
        or: python main.py router --debug=True              |切换到开发环境

        >>为了在生产环境下获得最佳性能，建议在禁用 ``debug`` 和 ``access_log`` 的情况下运行 Sanic

        :param debug: 当 Sanic 作为子模块使用时，禁用 debug 就可用于生产环境
        :param access_log: 如果您的确需要请求访问日志，又想获得更好的性能，可以考虑使用 Nginx
        作为代理，让 Nginx 来处理您的访问日志。这种方式要比用 Python 处理快得多得多。
        :return:
        """
        from services.app.server.router import app
        app.run(
            host=ROUTER_HOST,
            port=ROUTER_PORT,
            debug=debug,
            access_log=access_log,
        )
