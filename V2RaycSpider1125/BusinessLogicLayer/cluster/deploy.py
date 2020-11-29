__all__ = ['GeventSchedule']

import time
import schedule

from BusinessLogicLayer.cluster.slavers import __task__
from BusinessCentralLayer.sentinel import noticer
from BusinessCentralLayer.middleware.redis_io import *
from BusinessCentralLayer.coroutine_engine import *
import threading
from config import REDIS_SECRET_KEY, SINGLE_TASK_CAP, CRAWLER_SEQUENCE, ENABLE_COROUTINE, DEPLOY_CRONTAB, logger


class GeventSchedule(object):
    def __init__(self, go: bool = ENABLE_COROUTINE, deploy_cluster=CRAWLER_SEQUENCE, cap=SINGLE_TASK_CAP,
                 crontab=DEPLOY_CRONTAB):
        # 任务队列
        self.deploy_cluster = deploy_cluster

        # 协程加速
        self.go = go

        # 单机采集极限
        self.cap = cap

        # 任务间隔</min>
        self.crontab = crontab

        # 接入集群
        self.rc = RedisClient()

        self.rc_len = dict(zip(self.deploy_cluster, [1] * 3))

    def push_task(self, task_name: str) -> bool:
        """

        @param task_name:
        @return:
        """

        # 输入参数的数据类型错误
        if not isinstance(task_name, str):
            logger.error(f'The input type is wrong({task_name})')
            return False

        # 输入的参数不在模型的权限范围中
        if task_name not in self.deploy_cluster:
            logger.error(f'Spelling error in input({task_name}),Please choose from {self.deploy_cluster}')
            return False

        try:
            # 判断缓冲队列是否已达单机采集极限
            task_name = task_name.lower()
            self.rc_len[f'{task_name}'] = self.rc.__len__(REDIS_SECRET_KEY.format(f'{task_name}'))
            logger.info(f'[TEST] ||正在检查({task_name}) 任务队列...')

            # 若已达或超过单机采集极限，则休眠任务
            if self.rc_len[f"{task_name}"] >= self.cap:
                logger.debug(f'[SLEEP] || 任务队列已满 ({task_name}) ({self.rc_len[f"{task_name}"]}/{self.cap})')
                return True
        finally:
            # 无论队列是否已满，执行一次ddt
            self.ddt(class_=task_name)

        try:
            # 执行采集任务，通过self.go决定是否启动协程加速
            logger.info(f'[RUN] || ({task_name}) 采集任务启动')
            __task__.loads_task(task_name, self.go)

            # 判断任务是否完全失败，既单个类型链接的所有采集任务全部失败->Abnormal
            if self.rc.__len__(REDIS_SECRET_KEY.format(f'{task_name}')) < self.rc_len[f'{task_name}']:
                logger.error(f'[CRITICAL]Abnormal collection task({task_name})')
            else:
                return True
        except Exception as e:
            # 捕获未知错误
            logger.error(f'[ERROR]{self.__class__.__name__}({task_name}) crawler engine panic{e}')
        finally:
            # 单个类型的链接采集结束
            logger.success('[OVER] || 任务结束 {}({})'.format(self.__class__.__name__, task_name))

    @logger.catch()
    def run_check(self, class_: str) -> None:
        """
        启动任务：以非部署模式,传递参数
        @param class_:
            --传入的应是 config 中 crawler seq中的参数，如`v2ray`/`ssr`/`trojan`
            --确保操作的原子性，不要一次性传入多个参数，
                --正确的做法是通过<协程引擎>的消息队列形式驱动多任务
                --或使用for迭代work_seq顺序驱动多任务
        @return:
        """
        self.push_task(class_)

    def ddt(self, class_: str = None) -> None:
        """

        @param class_: subscribe type  `ssr` or `v2ray` or `trojan` ...
        @return:
        """
        if class_ is None:
            for item in self.deploy_cluster:
                threading.Thread(target=RedisDataDisasterTolerance().run,args=(item,)).start()
        elif isinstance(class_, str) and class_ in self.deploy_cluster:
            RedisDataDisasterTolerance().run(class_)
        else:
            logger.warning('{}.ddt() 输入参数错误，可能的原因为：类型错误/不在crawler_seq工作队列内'.format(self.__class__.__name__))

    @logger.catch()
    def run(self) -> None:
        # logger.warning('This is a development server. Do not use it in a production deployment.')

        try:
            for task_name in self.deploy_cluster:
                schedule.every(self.crontab).minutes.do(self.push_task, task_name=task_name)
                schedule.every(1).minute.do(self.rc.refresh, key_name=REDIS_SECRET_KEY.format(task_name))
                logger.info(f"start {task_name}/crontab:{self.crontab}minutes")

                self.crontab += 5

            while True:
                schedule.run_pending()
                time.sleep(1)

        except Exception as err:
            logger.exception('Exception occurred ||{}'.format(err))
            noticer.send_email(text_body='{}'.format(err), to='self')
        except KeyboardInterrupt as err:
            logger.stop('Forced stop ||{}'.format(err))


if __name__ == '__main__':
    GeventSchedule().run()
