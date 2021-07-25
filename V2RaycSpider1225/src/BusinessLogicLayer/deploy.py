"""
采集服务的定时任务管理模块
"""
__all__ = ['GeventSchedule']

import logging
import time

import schedule
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.BusinessCentralLayer.setting import logger, LAUNCH_INTERVAL

logging.getLogger('apscheduler').setLevel(logging.DEBUG)


# FIXME
#  本方案刻意限制了部署性能，请服务器资源阔绰的玩家自行使用APSchedule模块兼容协程部署任务
#  加速版本的调度器将在未来版本开源
class GeventSchedule(object):
    def __init__(self, dockers=None):
        """

        @param dockers: {"name":job name,"api":job func} job_name及其interval必须在config中定义并书相应的执行函数job func
        """

        # 同步定时间隔参数
        self.interval_ = self.sync_launch_interval()
        # 实例化调度器
        self.scheduler_ = BlockingScheduler()
        # 任务容器 存储全局任务标识及标识指向的业务模块
        self.dockers = dockers
        self.jobs = []
        # 自动初始化 任务解包->读取->部署
        self.deploy_jobs()

    def deploy_jobs(self):
        try:
            for docker in self.dockers:
                # 添加任务
                job = self.scheduler_.add_job(
                    func=docker['api'],
                    trigger=IntervalTrigger(seconds=self.interval_[docker['name']]),
                    id=docker['name'],
                    # 定時抖動
                    jitter=5,
                    # 定任务设置最大实例并行数
                    max_instances=16,
                    # 把多个排队执行的同一个哑弹任务变成一个
                    coalesce=True,
                )
                self.jobs.append(job)
                # 打印日志
                logger.info(
                    f'<BlockingScheduler> Add job -- <{docker["name"]}>'
                    f' IntervalTrigger: {self.interval_[docker["name"]]}s'
                )
            # 启动任务
            self.scheduler_.start()
        except KeyboardInterrupt:
            self.scheduler_.shutdown(wait=False)
            logger.warning("<BlockingScheduler> The admin forcibly terminated the scheduled task")
        except Exception as err:
            logger.exception(f'<BlockingScheduler>||{err}')

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
        else:
            return launch_interval


class SpawnBoosterScheduler(GeventSchedule):
    def __init__(self, dockers):
        super(SpawnBoosterScheduler, self).__init__(dockers=dockers)


def quick_deploy_(docker=GeventSchedule, interface: str = 'interface', crontab_seconds: int = 100):
    """

    @param crontab_seconds: 每间隔多少秒执行一次任务
    @param interface: 接口函数名
    @param docker: Python 类对象指针,如 SubscribesCleaner，而不是SubscribesCleaner()
    @return:
    """

    logger.success(f'<GeventSchedule>启动成功 -- {docker.__name__}')

    def release_docker():
        """
        由接口解压容器主线功能
        @return:
        """
        logger.info(f'<GeventSchedule> Release docker || Do {docker.__name__}')
        exec(f'docker().{interface}()')

    schedule.every(crontab_seconds).seconds.do(release_docker)

    while True:
        schedule.run_pending()
        time.sleep(1)
