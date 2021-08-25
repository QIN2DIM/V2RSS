"""
采集服务的定时任务管理模块
"""
__all__ = ['TasksScheduler', 'CollectorScheduler']

from datetime import datetime, timedelta

import gevent
from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.triggers.interval import IntervalTrigger
from gevent import monkey
from gevent.queue import Queue

from src.BusinessCentralLayer.setting import logger
from src.BusinessLogicLayer.cluster.cook import devil_king_armed, reset_task
from src.BusinessLogicLayer.cluster.prism import Prism

monkey.patch_all()


class TasksScheduler:
    def __init__(self):
        # 任务容器 存储全局任务标识及标识指向的业务模块
        self.dockers: list = []
        # 定时器同步时间
        self.sync_step = None
        # 超时容忍能力 越高则容忍超时的心态越好 threshold ∈[0, 1.0]
        self.threshold = 0.85
        # 容许的任务游离时间，超时销毁
        self.echo_limit = None
        # 任务开关，必须映射配置后才能启动调度器
        self.is_pending = None
        # ----------------------
        # setting of scheduler
        # ----------------------
        # 实例化调度器
        self.scheduler = BlockingScheduler()
        # 定時抖動
        self.jitter = 5
        # 定任务设置最大实例并行数
        self.max_instances = 4
        # 时间（以秒为单位）该作业的执行允许延迟多少（None 表示“允许作业运行，无论多晚”）
        self.coalesce = True
        # 把多个排队执行的同一个哑弹任务变成一个
        self.misfire_grace_time = 10

    def add_job(self, docker: dict):
        """
        dockers: {"name":job name,"api":job func}
        :param docker:
        :return:
        """
        if docker.get("permission"):
            self.dockers.append(docker)
            self.is_pending = True

    def mapping_config(self, job_config: dict):
        """
        采集器参数映射/转换
        :param job_config:
        :return:
        """

    def deploy_jobs(self):
        # 任务未映射
        if not self.is_pending:
            return False
        try:
            self.echo()
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown(wait=True)
        except Exception as err:
            logger.exception(f'<BlockingScheduler>||{err}')
        finally:
            logger.success("<Scheduler> The echo-loop running ends.")

    def echo(self):
        """
        do your day job
        :return:
        """
        for i, docker in enumerate(self.dockers):
            # 清洗参数
            docker_api = False if docker.get("api") is None else docker.get("api")
            docker_name = f"docker_{i}" if docker.get("name") is None else docker.get("name")
            docker_interval = 60 if docker.get("interval") is None else docker.get("interval")
            if not docker_api:
                continue
            # 添加任务
            self.scheduler.add_job(
                func=docker_api,
                trigger=IntervalTrigger(seconds=docker_interval),
                id=docker_name,
                # 定時抖動
                jitter=self.jitter,
                # 定任务设置最大实例并行数
                max_instances=self.max_instances,
                # 时间（以秒为单位）该作业的执行允许延迟多少（None 表示“允许作业运行，无论多晚”）
                misfire_grace_time=self.misfire_grace_time,
                # 把多个排队执行的同一个哑弹任务变成一个
                coalesce=True,
            )


class CollectorScheduler(TasksScheduler):
    def __init__(self):
        super(CollectorScheduler, self).__init__()
        # ----------------------
        # setting of collector
        # ----------------------
        # 协程数
        self.power = 2
        # 任务容器：queue
        self.work_q = Queue()
        # 任务队列满载时刻长度
        self.max_queue_size = 0
        # running state of instance
        self.running_jobs = {}

        self.is_running = None
        # ----------------------
        # setting of scheduler
        # ----------------------
        self.scheduler = GeventScheduler()
        self.echo_id = 'echo-loop'
        self.misfire_grace_time = None

    # ------------------------------------
    # Scheduler API
    # ------------------------------------

    def mapping_config(self, job_config: dict):
        # 调整任务权限
        self.is_pending = job_config.get('permission')
        # 采集功率
        self.power = job_config.get('power')
        # 启动间隔
        self.sync_step: int = job_config.get('interval')
        # 运行时长
        self.echo_limit = int(self.sync_step * (1 + self.threshold))
        # 游离极限
        self.misfire_grace_time = self.echo_limit - self.sync_step

    def deploy_jobs(self):
        # 任务未映射
        if not self.is_pending:
            return False
        try:
            self.echo()
            self.scheduler.add_listener(self.monitor, EVENT_JOB_MAX_INSTANCES | EVENT_JOB_SUBMITTED | EVENT_JOB_ERROR)
            logger.success("<CollectorScheduler> The echo-monitor was created successfully.")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown(wait=True)
            logger.success("<Scheduler> The echo-loop running ends.")
        except Exception as err:
            logger.exception(f'<BlockingScheduler>||{err}')

    def echo(self):
        # run the echo-loop
        self.scheduler.add_job(
            # interface of vulcan-collector
            func=self.go,
            id=self.echo_id,
            trigger=IntervalTrigger(seconds=self.sync_step),
        )

    def monitor(self, event):
        """
        监控实体任务以及容器生成任务运行状态
         01.共享全局WebDriverObj，使用quit()方法退出 ChromeObject
         02.ChromeObject是否退出，与任务是否消解无关。需要获取任务标识，通过任务标识移除任务
         03.
        :return:
        """
        debug_log = {
            "event": event,
            "queue_size": self.work_q.qsize(),
            "running_jobs": len(self.running_jobs),
            "is_running": self.is_running,
            "message": "queue_size[{}] running_jobs[{}] is_running[{}]"
        }
        # logger.debug(f"<CollectorScheduler> {debug_log}")
        log_message = debug_log.get('message').format(self.work_q.qsize(), len(self.running_jobs), self.is_running)
        logger.debug(f"<CollectorScheduler> {log_message}")
        if len(self.running_jobs) != 0:
            logger.debug("<CollectorScheduler> The listener jobs of collector start to work.")
            # 遍历执行队列
            runtime_state = list(self.running_jobs.items())
            for id_, instance_ in runtime_state:
                # 识别超时任务
                is_timeout = instance_['start-time'] + timedelta(
                    seconds=instance_['running-limit']) < datetime.now()
                if is_timeout:
                    try:
                        # 退出游离实例
                        instance_['api'].quit()
                        # 移除任务标签
                        self.running_jobs.pop(id_)
                        logger.debug(f">> Kill <{instance_['name']}> --> unresponsive session_id:{id_}")
                    # 外部中断运行实体，拒绝实体内的自愈方案并主动捕获异常ConnectionRefusedError
                    except Exception as e:
                        logger.warning(f"ERROR <{instance_['name']}> --> {e}")
            if (not self.is_running) and (len(self.running_jobs) == 0) and (self.work_q.qsize() == 0):
                self.scheduler.remove_job(job_id=self.echo_id)
                self.echo()
                logger.warning("<CollectorScheduler> The echo-loop job of collector has been reset.")
            logger.debug("<CollectorScheduler> The listener jobs of collector goes to sleep.")

    # ------------------------------------
    # Coroutine Job API
    # ------------------------------------

    def go(self, power: int = 8):
        # ===========================
        # 参数清洗
        # ===========================
        # 配置弹性采集功率
        power_ = self.power if self.power else power
        if self.max_queue_size != 0:
            power_ = self.max_queue_size if power_ > self.max_queue_size else power_
        self.power = power_
        # ===========================
        # 任务重载
        # ===========================
        # 重载任务队列 with weight
        instances = reset_task()
        if not instances:
            logger.debug("<CollectorScheduler> The echo-loop collector goes to sleep.")
            return False
        # 重载协程队列
        self.is_running = self.offload_task(instances)
        if self.is_running is False:
            logger.debug("<CollectorScheduler> The echo-loop collector goes to sleep.")
            return False
        # ===========================
        # 配置launcher
        # ===========================
        task_list = []
        for _ in range(power_):
            task = gevent.spawn(self.launch)
            task_list.append(task)
        # ===========================
        # 启动launcher
        # ===========================
        gevent.joinall(task_list)
        self.is_running = False

    def offload_task(self, instances: list) -> bool:
        # TODO 此处需要进行一轮收益计算，调整任务权重
        # 复制实体团
        pending_tasks = instances.copy()
        # 无待解压实体（未分发任务）
        if len(pending_tasks) == 0:
            return False
        # 读取实体特征加入协程工作队列
        for atomic in pending_tasks:
            self.work_q.put_nowait(atomic)
        # 更新执行任务数
        self.max_queue_size = self.work_q.qsize()
        return True

    def launch(self):
        while not self.work_q.empty():
            atomic = self.work_q.get_nowait()
            self.devil_king_armed(atomic)

    def devil_king_armed(self, atomic: dict):
        """
        一个映射了__entropy__站点源特征词典的SpawnEntity-Selenium运行实体
        :param atomic:
        :return:
        """
        # 根据特征选择不同的解决方案
        if atomic.get("feature") == 'prism':
            alice = Prism(atomic, assault=True, silence=True)
        else:
            alice = devil_king_armed(atomic, assault=True, silence=True)
        # 创建运行实体配置
        api = alice.set_spider_option()
        # 标记运行实体
        alice_id = api.session_id
        alice_name = alice.action_name
        start_time = datetime.now()
        # running_limit = alice.work_clock_max_wait + self.echo_limit
        running_limit = int(sum([alice.work_clock_max_wait, self.echo_limit]) / 2)
        # 更新运行状态
        self.running_jobs.update(
            {
                alice_id: {
                    "api": api,
                    "start-time": start_time,
                    "running-limit": running_limit,
                    "name": alice_name
                }
            }
        )
        try:
            # :)清理桌面
            alice.run(api)
        # CTRL+C / strong anti-spider engine / is being DDOS
        except Exception as e:
            logger.error(f">> ERROR <{alice_name}> --> {e}")
        finally:
            try:
                # :)签退下班
                self.running_jobs.pop(alice_id)
                logger.debug(f">> Detach <{alice_name}> --> [session_id] {alice_id}")
            except (KeyError,):
                pass
