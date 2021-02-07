__all__ = ['SystemInterface']

import multiprocessing

from BusinessCentralLayer.middleware.redis_io import RedisClient
from BusinessCentralLayer.sentinel.noticer import send_email
from BusinessCentralLayer.setting import ENABLE_COROUTINE, REDIS_SECRET_KEY, CRAWLER_SEQUENCE, SINGLE_TASK_CAP, \
    API_DEBUG, API_PORT, API_THREADED, ENABLE_DEPLOY, ENABLE_SERVER, OPEN_HOST, logger, platform
from BusinessLogicLayer.cluster import sailor
from BusinessLogicLayer.cluster.slavers import actions
from BusinessLogicLayer.deploy import GeventSchedule
from BusinessLogicLayer.plugins.ddt_subs import SubscribesCleaner
from BusinessViewLayer.myapp.app import app

# ----------------------------------------
# 越权参数重置
# ----------------------------------------
enable_coroutine = ENABLE_COROUTINE


# ----------------------------------------
# 容器接口液化
# ----------------------------------------
class _ContainerDegradation(object):
    def __init__(self):
        """config配置参数一次性读取之后系统不再响应配置变动，修改参数需要手动重启项目"""
        # 热加载配置文件 载入越权锁
        self.deploy_cluster, self.cap = CRAWLER_SEQUENCE, SINGLE_TASK_CAP
        self.go = enable_coroutine

    @staticmethod
    def startup_ddt_decouple(debug: bool = False, power: int = 12):
        SubscribesCleaner(debug=debug).interface(power=power)

    def startup_ddt_overdue(self, task_name: str = None):
        if task_name is None:
            for task_name in self.deploy_cluster:
                RedisClient().refresh(key_name=REDIS_SECRET_KEY.format(task_name), cross_threshold=3)
        else:
            RedisClient().refresh(key_name=REDIS_SECRET_KEY.format(task_name), cross_threshold=3)

    def startup_collector(self):
        """
        @FIXME 修复缓存堆积问题，并将本机任务队列推向分布式消息队列
        @return:
        """
        for task_name in self.deploy_cluster:
            sailor.manage_task(class_=task_name, speedup=self.go)


_cd = _ContainerDegradation()


class _SystemEngine(object):

    def __init__(self) -> None:
        logger.info(f'<系统初始化> SystemEngine -> {platform}')

        # 读取配置序列
        logger.info(f'<定位配置> check_sequence:{CRAWLER_SEQUENCE}')

        # 默认linux下自动部署
        logger.info(f'<部署设置> enable_deploy:{ENABLE_DEPLOY}')

        # 协程加速配置
        logger.info(f"<协程加速> Coroutine:{enable_coroutine}")

        # 解压接口容器
        logger.info("<解压容器> DockerEngineInterface")

        # 初始化进程
        logger.info(f'<加载队列> IndexQueue:{actions.__all__}')

        logger.success('<Gevent> 工程核心准备就绪 任务即将开始')

    @staticmethod
    def run_server() -> None:
        """
        部署接口
        @return:
        """
        app.run(host=OPEN_HOST, port=API_PORT, debug=API_DEBUG, threaded=API_THREADED)

    @staticmethod
    def run_deploy() -> None:
        """
        定时任务,建议使用if而非for构造任务线程池
        @return:
        """
        try:
            # 初始化任务对象
            dockers = []

            # 载入定时任务权限配置
            tasks = ENABLE_DEPLOY['tasks']
            for docker_name, permission in tasks.items():
                if permission:
                    dockers.append({"name": docker_name, "api": eval(f"_cd.startup_{docker_name}")})
            # 无论有无权限都要装载采集器
            if not tasks['collector']:
                dockers.append({"name": 'collector', "api": _cd.startup_collector})
            # 启动定时任务
            GeventSchedule(dockers=dockers)
        except KeyError:
            logger.critical('config中枢层配置被篡改，ENABLE_DEPLOY 配置中无”tasks“键值对')
            exit()
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
            from BusinessCentralLayer.middleware.subscribe_io import FlexibleDistribute
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
        except TypeError or AttributeError as e:
            logger.exception(e)
            send_email(f"[程序异常终止]{str(e)}", to_='self')
        except KeyboardInterrupt:
            # FIXME 确保进程间不产生通信的情况下终止
            logger.debug('<SystemProcess> Received keyboard interrupt signal')
            for process_ in process_list:
                process_.terminate()
        finally:
            logger.success('<SystemProcess> End the V2RayCloudSpider')


# ----------------------------------------
# 外部接口
# ----------------------------------------
class SystemInterface(object):

    @staticmethod
    def system_panel() -> None:
        """
        该接口用于开启panel桌面前端
        @return:
        """
        from BusinessViewLayer.panel.panel import V2RaycSpiderMasterPanel
        v2raycs = V2RaycSpiderMasterPanel()
        try:
            v2raycs.home_menu()
        except Exception as e:
            v2raycs.debug(e)
        finally:
            v2raycs.kill()

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
            coroutine_speed_up: bool = None,
            beat_sync: bool = True,
            force_run: bool = None
    ) -> None:
        """
        主程序入口
        @param force_run:以debug身份强制运行采集器
        @param beat_sync:节拍同步
        @param deploy_: 部署 定时任务+flask web API
        @param coroutine_speed_up:协程加速控件，在任何情况下默认启动
        @return:
        """
        global enable_coroutine

        # 手动传参优先级更高，修改系统权限
        enable_coroutine = coroutine_speed_up if coroutine_speed_up else ENABLE_COROUTINE

        # 部署定时任务
        if deploy_:
            _SystemEngine().startup()

        # 立刻执行任务(debug)
        else:
            _SystemEngine().run(beat_sync=beat_sync, force_run=force_run)
