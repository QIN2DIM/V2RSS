__all__ = ['SystemInterface']

import multiprocessing
import sys

from redis.exceptions import ConnectionError

from src.BusinessCentralLayer.setting import REDIS_SECRET_KEY, CRAWLER_SEQUENCE, SINGLE_TASK_CAP, \
    API_DEBUG, API_PORT, API_THREADED, ENABLE_DEPLOY, ENABLE_SERVER, OPEN_HOST, logger, LAUNCH_INTERVAL, terminal_echo
from src.BusinessLogicLayer.cluster import sailor, slavers
from src.BusinessLogicLayer.deploy import TasksScheduler, CollectorScheduler
from src.BusinessLogicLayer.plugins.accelerator import SubscribesCleaner
from src.BusinessViewLayer.myapp.app import app
from .redis_io import RedisClient

# ----------------------------------------
# 越权参数重置
# ----------------------------------------

ACTIONS_IO = [f'{[j[0] for j in i.get("hyper_params").items() if j[-1]]}{i.get("name")}' for i in slavers.__entropy__]


# ----------------------------------------
# 容器接口液化
# ----------------------------------------
class _ContainerDegradation:
    def __init__(self):
        """config配置参数一次性读取之后系统不再响应配置变动，修改参数需要手动重启项目"""
        # 热加载配置文件 载入越权锁
        self.deploy_cluster, self.cap = CRAWLER_SEQUENCE, SINGLE_TASK_CAP

    @staticmethod
    def sync_launch_interval() -> dict:
        # 读取配置文件
        launch_interval = LAUNCH_INTERVAL
        # 检查配置并返回修正过后的任务配置
        for task_name, task_interval in launch_interval.items():
            # 未填写或填写异常数字
            if (not task_interval) or (task_interval <= 1):
                logger.critical(f"<launch_interval>--{task_name}设置出现致命错误，即将熔断线程。间隔为空或小于1")
                raise Exception
            # 填写浮点数
            if not isinstance(task_interval, int):
                logger.warning(f"<launch_interval>--{task_name}任务间隔应为整型int，参数已拟合")
                # 尝试类型转换若不中则赋一个默认值 60s
                try:
                    launch_interval.update({task_name: int(task_interval)})
                except TypeError:
                    launch_interval.update({task_name: 60})
            # 填写过小的任务间隔数，既设定的发动频次过高，主动拦截并修正为最低容错 60s/run
            if task_interval < 60:
                logger.warning(f"<launch_interval>--{task_name}任务频次过高，应不少于60/次,参数已拟合")
                launch_interval.update({task_name: 60})

        return launch_interval

    @staticmethod
    def startup_ddt_decouple(debug: bool = False, power: int = 12):
        SubscribesCleaner(debug=debug).interface(power=power)

    def startup_ddt_overdue(self, task_name: str = None):
        if task_name is None:
            for new_task in self.deploy_cluster:
                RedisClient().refresh(key_name=REDIS_SECRET_KEY.format(new_task), cross_threshold=3)
        else:
            RedisClient().refresh(key_name=REDIS_SECRET_KEY.format(task_name), cross_threshold=3)

    def startup_collector(self):
        """
        @FIXME 修复缓存堆积问题，并将本机任务队列推向分布式消息队列
        @return:
        """
        # --------------------------------------------------------------
        # TODO v5.4.r 版本更新
        # 将“采集器指令发起”定时任务改为无阻塞发动，尝试解决定时器任务“赶不上趟”的问题
        # --------------------------------------------------------------
        # task_queue = []
        # for task_name in self.deploy_cluster:
        #     task = gevent.spawn(sailor.manage_task, class_=task_name)
        #     task_queue.append(task)
        # gevent.joinall(task_queue)
        for task_name in self.deploy_cluster:
            sailor.manage_task(class_=task_name)


_cd = _ContainerDegradation()


class _SystemEngine:

    def __init__(self) -> None:
        terminal_echo(f"[SystemEngineIO] CONFIG_COLLECTOR_PERMISSION:{CRAWLER_SEQUENCE}", 1)
        terminal_echo(f"[SystemEngineIO] CONFIG_ENABLE_DEPLOY:{ENABLE_DEPLOY}", 1)
        terminal_echo("[SystemEngineIO] CONFIG_COROUTINE:True", 1)
        for action_image in ACTIONS_IO:
            terminal_echo(f"[SystemEngineIO] CONFIG_ACTIONS:{action_image}", 1)

        logger.success("<SystemEngineIO> System core initialized successfully.")

    @staticmethod
    def run_server() -> None:
        """
        部署接口
        @return:
        """
        app.run(host=OPEN_HOST, port=API_PORT, debug=API_DEBUG, threaded=API_THREADED)

    @staticmethod
    @logger.catch()
    def run_deploy() -> None:
        """
        定时任务,建议使用if而非for构造任务线程池
        @return:
        """
        # 载入定时任务权限配置
        tasks = ENABLE_DEPLOY['tasks']
        task2function = {
            'ddt_decouple': _cd.startup_ddt_decouple,
            'ddt_overdue': _cd.startup_ddt_overdue,
        }
        try:

            # 初始化调度器
            docker_of_based_scheduler = TasksScheduler()
            docker_of_collector_scheduler = CollectorScheduler()
            # 清洗配置 使调度间隔更加合理
            interval = _cd.sync_launch_interval()
            # 添加任务
            for docker_name, permission in tasks.items():
                logger.info(f"[Job] {docker_name} -- interval: {interval[docker_name]}s -- run: {permission}")
                # 若开启采集器则使用CollectorScheduler映射任务
                # 使用久策略将此分流判断注释既可
                if docker_name == "collector":
                    docker_of_collector_scheduler.mapping_config({
                        'interval': interval[docker_name],
                        'permission': permission,
                    })
                    continue
                if permission:
                    docker_of_based_scheduler.add_job({
                        "name": docker_name,
                        "api": task2function[docker_name],
                        'interval': interval[docker_name],
                        'permission': True
                    })
            # 启动定时任务 要求执行采集任务时必须至少携带另一种其他部署任务
            docker_of_collector_scheduler.deploy_jobs()
            docker_of_based_scheduler.deploy_jobs()
        except ConnectionError:
            logger.warning("<RedisIO> Network communication failure, please check the network connection.")
        except KeyError:
            logger.critical(f'config中枢层配置被篡改，ENABLE_DEPLOY 配置中无对应键值对{tasks}')
            sys.exit()
        except NameError:
            logger.critical('eval()或exec()语法异常，检测变量名是否不一致。')

    @staticmethod
    def run(beat_sync=True, force_run=None) -> None:
        """
        本地运行--检查队列残缺
        # 所有类型任务的节点行为的同时发起 or 所有类型任务的节点行为按序执行,node任务之间互不影响

            --v2rayChain
                --vNode_1
                --vNode_2
                --....
            --ssrChain
                --sNode_1
                --sNode_2
                --...
            --..
                                    -----> runtime v2rayChain
        IF USE vsu -> runtime allTask =====> runtime ...
                                    -----> runtime ssrChain

            ELSE -> runtime allTask -> Chain_1 -> Chain_2 -> ...

                                    -----> runtime node_1
        IF USE go -> runtime allNode =====> runtime ...
                                    -----> runtime node_N

            ELSE -> runtime allNode-> the_node_1 -> the_node_2 -> ...

        @return:
        """
        # 同步任务队列(广度优先)
        # 这是一次越权执行，无论本机是否具备collector权限都将执行一轮协程空间的创建任务
        for class_ in CRAWLER_SEQUENCE:
            sailor.manage_task(class_=class_, beat_sync=beat_sync, force_run=force_run)

        # FIXME 节拍同步
        if not beat_sync:
            from src.BusinessCentralLayer.middleware.subscribe_io import FlexibleDistribute
            FlexibleDistribute().start()

        # 执行一次数据迁移
        # TODO 将集群接入多哨兵模式，减轻原生数据拷贝的额外CPU资源开销
        _cd.startup_ddt_overdue()

        # 任务结束
        logger.success('<Gevent>任务结束')

    @staticmethod
    def startup() -> None:
        process_list = []
        try:
            # 部署<单进程多线程>定时任务
            if ENABLE_DEPLOY['global']:
                process_list.append(
                    multiprocessing.Process(target=_SystemEngine.run_deploy, name='deploymentTimingTask'))

            # 部署flask
            if ENABLE_SERVER:
                process_list.append(multiprocessing.Process(target=_SystemEngine.run_server, name='deploymentFlaskAPI'))

            # 执行多进程任务
            for process_ in process_list:
                logger.success(f'<SystemProcess> Startup -- {process_.name}')
                process_.start()

            # 添加阻塞
            for process_ in process_list:
                process_.join()
        except (TypeError, AttributeError):
            pass
        except (KeyboardInterrupt, SystemExit):
            # FIXME 确保进程间不产生通信的情况下终止
            logger.debug('<SystemProcess> Received keyboard interrupt signal.')
            for process_ in process_list:
                process_.terminate()
        finally:
            logger.success('<SystemProcess> The system exits completely.')


# ----------------------------------------
# 外部接口
# ----------------------------------------
class SystemInterface:
    @staticmethod
    def system_panel() -> None:
        """
        该接口用于开启panel桌面前端
        @return:
        """
        from src.BusinessViewLayer.panel.panel import PaneInterfaceIO
        v2raycs = PaneInterfaceIO()
        v2raycs.home_menu()

    @staticmethod
    def ddt(task_name: str = None):
        if not task_name:
            _cd.startup_ddt_overdue()
        elif not (isinstance(task_name, str) and task_name in CRAWLER_SEQUENCE):
            logger.warning("<Interface>传入的参数（task_name）不合法，任务类型必须被指定在CRAWLER_SEQUENCE之中")
        else:
            _cd.startup_ddt_overdue(task_name)

    @staticmethod
    def subs_ddt(debug: bool = True, power: int = 12):
        _cd.startup_ddt_decouple(debug=debug, power=power)

    @staticmethod
    def run(
            deploy_: bool = None,
            beat_sync: bool = True,
            force_run: bool = None
    ) -> None:
        """
        主程序入口
        @param force_run:以debug身份强制运行采集器
        @param beat_sync:节拍同步
        @param deploy_: 部署 定时任务+flask web API
        @return:
        """

        # 部署定时任务
        if deploy_:
            _SystemEngine().startup()

        # 立刻执行任务(debug)
        else:
            _SystemEngine().run(beat_sync=beat_sync, force_run=force_run)
