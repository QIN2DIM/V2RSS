__all__ = ['Interface']
# FIXME：如果您是项目开发者，请在项目调试中注释掉以下的monkey插件

exec("from gevent import monkey\nmonkey.patch_all()")

import csv
import multiprocessing
import os

from BusinessCentralLayer.coroutine_engine import vsu, PuppetCore
from BusinessCentralLayer.middleware.subscribe_io import FlexibleDistribute
from BusinessCentralLayer.middleware.work_io import Middleware
from BusinessCentralLayer.sentinel.noticer import send_email
from BusinessLogicLayer.cluster.__task__ import loads_task
from BusinessLogicLayer.cluster.slavers import actions
from BusinessLogicLayer.deploy import GeventSchedule
from BusinessViewLayer.myapp.app import app
from config import *


class ConfigQuarantine(object):
    def __init__(self):

        self.root = [
            SERVER_DIR_CLIENT_DEPORT, SERVER_PATH_DEPOT_VCS,
            SERVER_DIR_DATABASE_CACHE, SERVER_DIR_CACHE_BGPIC
        ]
        self.flag = False

    def set_up_file_tree(self, root):
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

        # 检查默认下载地址是否残缺 深度优先初始化系统文件
        for child_ in root:
            if not os.path.exists(child_):
                self.flag = True
                # logger.error(f"系统文件缺失 {child_}")
                try:
                    # logger.debug(f"尝试链接系统文件 {child_}")
                    # 初始化文件夹
                    if os.path.isdir(child_) or not os.path.splitext(child_)[-1]:
                        os.mkdir(child_)
                        logger.success(f"系统文件链接成功->{child_}")
                    # 初始化文件
                    else:
                        if child_ == SERVER_PATH_DEPOT_VCS:
                            try:
                                with open(child_, 'w', encoding='utf-8', newline='') as f:
                                    csv.writer(f).writerow(['version', 'title'])
                                logger.success(f"系统文件链接成功->{child_}")
                            except Exception as e:
                                logger.exception(f"Exception{child_}{e}")
                except Exception as e:
                    logger.exception(e)

    @staticmethod
    def check_config():
        if not all(SMTP_ACCOUNT.values()):
            logger.warning('您未正确配置<通信邮箱>信息(SMTP_ACCOUNT)')
        if not SERVER_CHAN_SCKEY:
            logger.warning("您未正确配置<Server酱>的SCKEY")
        if not all([REDIS_SLAVER_DDT.get("host"), REDIS_SLAVER_DDT.get("password")]):
            logger.warning('您未正确配置<Redis-Slaver> 本项目的部分功能将毫无意义')
        if not all([REDIS_MASTER.get("host"), REDIS_MASTER.get("password")]):
            logger.error("您未正确配置<Redis-Master> 此配置为“云彩姬”的核心组件，请配置后重启项目！")
            exit()

    def run(self):
        try:
            if [cq for cq in reversed(self.root) if not os.path.exists(cq)]:
                logger.warning('系统文件残缺！')
                logger.debug("启动<工程重构>模块...")
                self.set_up_file_tree(self.root)
            self.check_config()

        finally:
            if self.flag:
                logger.success(">>> 运行环境链接完成，请重启项目")
                logger.warning(">>> 提醒您正确配置Chrome及对应版本的ChromeDriver")
                exec("if self.flag:\n\texit()")


ConfigQuarantine().run()


class SystemEngine(object):

    def __init__(self, **kwargs) -> None:
        logger.info(f'<系统初始化>:SystemEngine -> {platform}')

        # 读取配置序列
        self.check_seq = CRAWLER_SEQUENCE
        logger.info(f'<定位配置>:check_sequence:{self.check_seq}')

        # 默认linux下自动部署
        self.enable_deploy = ENABLE_DEPLOY if kwargs.get(
            'enable_deploy') is None else kwargs.get('enable_deploy')
        logger.info('<部署设置>:enable_deploy:{}'.format(self.enable_deploy))

        # 单机协程加速配置
        self.speed_up = ENABLE_COROUTINE if kwargs.get(
            'speed_up') is None else kwargs.get('speed_up')
        logger.info("<协程加速>:speed_up:{}".format(self.speed_up))

        # 初始化进程
        self.server_process, self.deploy_process = None, None
        logger.info('<初始化进程>:deploy_process:server_process')
        logger.info(f'<加载队列>:IndexQueue:{actions.__all__}')

        logger.success('<Gevent>工程核心准备就绪 任务即将开始')

    @staticmethod
    def run_server() -> None:
        """
        部署接口
        @return:
        """
        app.run(host=OPEN_HOST, port=API_PORT, debug=API_DEBUG, threaded=API_THREADED)

    def run_deploy(self) -> None:
        """
        定时采集
        @return:
        """
        GeventSchedule(go=self.speed_up).run()

    def run_check(self, at_once=True) -> None:
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
        # 加载任务队列(广度优先)
        for task in self.check_seq:
            loads_task(task, startup=False, at_once=at_once)

        # 任务启动 并发执行
        vsu(core=PuppetCore(), docker=Middleware.poseidon).run(self.speed_up)

        # print('Easter eggs')
        # fixme 数据存储 节拍同步
        if not at_once:
            FlexibleDistribute().start()

        # 任务结束
        logger.success('<Gevent>任务结束')

        # 执行一次数据迁移
        GeventSchedule().ddt()

    def run(self) -> None:

        try:
            if self.enable_deploy:
                self.deploy_process = multiprocessing.Process(
                    target=self.run_deploy, name='定时采集')
                logger.info(f'starting {self.deploy_process.name}')
                self.deploy_process.start()
            if ENABLE_SERVER:
                self.server_process = multiprocessing.Process(
                    target=self.run_server, name='程序接口')
                logger.info(f'starting {self.server_process.name}')
                self.server_process.start()

            self.deploy_process.join()
            self.server_process.join()
        except TypeError or AttributeError as e:
            logger.exception(e)
            send_email("[程序异常终止]{}".format(str(e)), to_='self')
        except KeyboardInterrupt:
            logger.debug('received keyboard interrupt signal')
            self.server_process.terminate()
            self.deploy_process.terminate()
        finally:
            self.deploy_process.join()
            self.server_process.join()
            logger.info(
                f'{self.deploy_process.name} is {"alive" if self.deploy_process.is_alive() else "dead"}')
            logger.info(
                f'{self.server_process.name} is {"alive" if self.server_process.is_alive() else "dead"}')

            logger.success('<Gevent>任务结束')


class Interface(object):

    @staticmethod
    def __window__() -> None:
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
    def run(sys_command=None, deploy_: bool = None, coroutine_speed_up: bool = False, at_once=True) -> None:
        """
        主程序入口
        @param at_once:
        @param sys_command: sys.argv
        @param deploy_:
            1. ‘check’:单机运行<wins or mac 默认>  ‘deploy’:服务器部署<linux下默认>
            2. 若在服务器上运行请使用’deploy‘模式--部署定时任务
        @param coroutine_speed_up:协程加速控件，在任何情况下默认启动
        @return:
        """
        # 优先读取命令行指令
        if sys_command:
            deploy_ = True if 'deploy' in sys_command else False
            coroutine_speed_up = True if 'speed_up' in sys_command else False

        if deploy_ is None:
            deploy_ = True if 'linux' in platform else False

        if deploy_:
            SystemEngine(speed_up=coroutine_speed_up,
                         enable_deploy=deploy_).run()
        else:
            SystemEngine(speed_up=coroutine_speed_up,
                         enable_deploy=deploy_).run_check(at_once)

    @staticmethod
    def ddt(task_name=None):
        GeventSchedule().ddt(task_name)

    @staticmethod
    def subs_ddt(debug=True, power=12):
        from BusinessLogicLayer.plugins.ddt_subs import SubscribesCleaner
        SubscribesCleaner(debug=debug).interface(power=power)
