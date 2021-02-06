__all__ = ['GeventSchedule']

import time

import schedule
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from BusinessCentralLayer.setting import logger, LAUNCH_INTERVAL


# FIXME
#  本方案刻意限制了部署性能，请服务器资源阔绰的玩家自行使用APSchedule模块兼容协程部署任务
#  资源阔绰定义：4xCPU，4G RAM
#  加速版本的调度器将在未来版本开源
class GeventSchedule(object):
    def __init__(self, dockers=None):
        """

        @param dockers: {"name":job name,"api":job func} job_name及其interval必须在config中定义并书相应的执行函数job func
        """

        # 同步定时间隔参数
        self.interval_ = self._sync_launch_interval()

        # 实例化调度器
        self.scheduler_ = BlockingScheduler()

        self.dockers = dockers

        self._deploy_jobs()

    def _deploy_jobs(self):
        """

        @return:
        """

        try:
            for docker in self.dockers:
                # 添加任务
                self.scheduler_.add_job(
                    func=docker['api'],
                    trigger=IntervalTrigger(seconds=self.interval_[docker['name']]),
                    id=docker['name'],
                    jitter=5
                )
                # 打印日志
                logger.info(
                    f'<BlockingScheduler> Add job -- <{docker["name"]}>'
                    f' IntervalTrigger: {self.interval_[docker["name"]]}s'
                )
            # 启动任务
            self.scheduler_.start()
        except KeyboardInterrupt as err:
            logger.stop('Forced stop ||{}'.format(err))
        except Exception as err:
            logger.exception(f'<BlockingScheduler>||{err}')

    @staticmethod
    def _sync_launch_interval() -> dict:
        # 热读取配置文件
        launch_interval = LAUNCH_INTERVAL
        for check in launch_interval.items():
            if not check[-1] or check[-1] <= 1:
                logger.critical(f"<launch_interval>--{check[0]}设置出现致命错误，即将熔断线程。间隔为空或小于1")
                raise Exception
            if not isinstance(check[-1], int):
                logger.warning(f"<launch_interval>--{check[0]}任务间隔应为整型int，参数已拟合")
                launch_interval.update({check[0]: round(check[-1])})
            if check[-1] < 60:
                logger.warning(f"<launch_interval>--{check[0]}任务频次过高，应不少于60/次,参数已拟合")
                launch_interval.update({check[0]: 60})
        else:
            return launch_interval


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
