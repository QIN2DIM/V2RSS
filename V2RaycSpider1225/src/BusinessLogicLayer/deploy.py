"""
采集服务的定时任务管理模块
"""
__all__ = ["TasksScheduler", "CollectorScheduler", "CollaboratorScheduler"]

import ast
import math
import os
import threading
import time
import warnings
from datetime import datetime, timedelta
from uuid import uuid4

import gevent
from apscheduler.events import (
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_MAX_INSTANCES,
    EVENT_JOB_ERROR,
)
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.triggers.interval import IntervalTrigger
from gevent import monkey
from gevent.queue import Queue

from BusinessCentralLayer.middleware.redis_io import MessageQueue
from BusinessCentralLayer.middleware.subscribe_io import FlexibleDistributeV2
from BusinessCentralLayer.setting import logger
from BusinessLogicLayer.cluster.cook import (
    devil_king_armed,
    reset_task,
    DevilKingArmed,
)

monkey.patch_all()
warnings.simplefilter("ignore", category=UserWarning)


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
        # 定時抖動，让定时任务“非准点”执行，上下浮动 jitter 秒
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
            logger.exception(f"<BlockingScheduler>||{err}")
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
            docker_name = (
                f"docker_{i}" if docker.get("name") is None else docker.get("name")
            )
            docker_interval = (
                60 if docker.get("interval") is None else docker.get("interval")
            )
            if not docker_api:
                continue
            # 添加任务
            self.scheduler.add_job(
                func=docker_api,
                trigger=IntervalTrigger(
                    seconds=docker_interval,
                    timezone="Asia/Shanghai"
                ),
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
    def __init__(self, power: int = None, group_name: str = None):
        super(CollectorScheduler, self).__init__()
        # ----------------------
        # setting of collector
        # ----------------------
        # 协程数
        self.power = os.cpu_count() if power is None else power
        # 任务容器：queue
        self.workers = Queue()
        # 超载队列
        self.overload = Queue()
        # 容载队列
        self.distributor = Queue(maxsize=100)
        # 任务队列满载时刻长度
        self.max_queue_size = 0
        # running state of instance
        self.running_jobs = {}

        self.is_running = None
        # ----------------------
        # setting of scheduler
        # ----------------------
        self.scheduler = GeventScheduler()
        self.echo_id = "echo-loop[M]"
        self.misfire_grace_time = None
        self.collector_id = "<CollectorScheduler-M>"
        self.synergy: bool = False
        self.log_trace = []
        self.freeze_screen = False
        self.max_instances = 2
        # 协同任务配置
        self.mq = MessageQueue(group_name)
        self.broadcast = FlexibleDistributeV2()
        self._runner = {"name": str(uuid4()), "hook": {}}

    # ------------------------------------
    # Scheduler API
    # ------------------------------------

    def mapping_config(self, job_config: dict):
        # 调整任务权限
        self.is_pending = job_config.get("permission")
        # 采集功率
        self.power = job_config.get("power")
        # 启动间隔
        self.sync_step: int = job_config.get("interval")
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
            self.scheduler.add_listener(
                self.monitor,
                EVENT_JOB_MAX_INSTANCES | EVENT_JOB_SUBMITTED | EVENT_JOB_ERROR,
            )
            logger.success(
                f"{self.collector_id} The echo-monitor was created successfully."
            )
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown(wait=True)
            logger.success("<Scheduler> The echo-loop running ends.")
        except Exception as err:
            logger.exception(f"<BlockingScheduler>||{err}")

    def echo(self):
        # run the echo-loop
        self.scheduler.add_job(
            # interface of vulcan-collector
            func=self.go,
            id=self.echo_id,
            trigger=IntervalTrigger(
                seconds=self.sync_step,
                timezone="Asia/Shanghai"
            ),
            max_instances=self.max_instances,
        )

    def monitor_logger(self, event):
        debug_log = {
            "event": event,
            "pending_jobs": self.workers.qsize(),
            "running_jobs": len(self.running_jobs),
            "is_running": self.is_running,
            "message": "queue_size[{}] running_jobs[{}] overheating_jobs[{}] is_running[{}]",
        }
        # logger.debug(f"<CollectorScheduler> {debug_log}")
        message_ = debug_log.get("message")
        log_message = (
            message_.format(
                self.workers.qsize(),
                len(self.running_jobs),
                self.distributor.qsize(),
                self.is_running,
            )
            if message_
            else ""
        )
        if self.freeze_screen:
            if len(self.log_trace) > 1:
                if log_message != self.log_trace[-1]:
                    logger.debug(f"{self.collector_id} {log_message}")
            else:
                logger.debug(f"{self.collector_id} {log_message}")
            self.log_trace.append(log_message)
        else:
            logger.debug(f"{self.collector_id} {log_message}")

    def monitor(self, event):
        """
        监控实体任务以及容器生成任务运行状态
         01.共享全局WebDriverObj，使用quit()方法退出 ChromeObject
         02.ChromeObject是否退出，与任务是否消解无关。需要获取任务标识，通过任务标识移除任务
         03.
        :return:
        """
        # Output runtime debug.
        self.monitor_logger(event)

        # ====================================================================
        # Remove the running instance of the suspended animation state.
        # ====================================================================
        if len(self.running_jobs) != 0:
            # logger.debug(
            #     f"{self.collector_id} The listener jobs of collector start to work."
            # )
            # 遍历执行队列
            runtime_state = list(self.running_jobs.items())
            for id_, instance_ in runtime_state:
                # 识别超时任务
                is_timeout = (
                        instance_["start-time"]
                        + timedelta(seconds=instance_["running-limit"])
                        < datetime.now()
                )
                if is_timeout:
                    try:
                        # 退出游离实例
                        instance_["api"].quit()
                        # 移除任务标签
                        self.running_jobs.pop(id_)
                        logger.debug(
                            f">> Kill <{instance_['name']}> --> unresponsive session_id:{id_}"
                        )
                    # 外部中断运行实体，拒绝实体内的自愈方案并主动捕获异常ConnectionRefusedError
                    except Exception as e:
                        logger.warning(f"ERROR <{instance_['name']}> --> {e}")
            if (
                    not self.is_running
                    and len(self.running_jobs) == 0
                    and self.workers.qsize() == 0
            ):
                self.scheduler.remove_job(job_id=self.echo_id)
                self.echo()
                logger.warning(
                    f"{self.collector_id} The echo-loop job of collector has been reset."
                )
                # self.dt_extension()
            # logger.debug(
            #     f"{self.collector_id} The listener jobs of collector goes to sleep."
            # )

    def dt_extension(self, cursor: int = None, log_=True):
        transfer_num = 0
        if not cursor:
            while not self.distributor.empty():
                self.workers.put_nowait(self.distributor.get())
                transfer_num += 1
        else:
            for _ in range(cursor):
                if self.distributor.empty():
                    break
                self.workers.put_nowait(self.distributor.get())
                transfer_num += 1

        if log_ and transfer_num != 0:
            logger.success(
                f"{self.collector_id} Disaster Tolerance Extension | "
                f"Distributor[{self.distributor.qsize()}] --({transfer_num})--> Workers[{self.workers.qsize()}]"
            )
        return transfer_num

    # ------------------------------------
    # Coroutine Job API
    # ------------------------------------

    def go(self, power: int = 8):
        # ===========================
        # 任务重载
        # ===========================
        if not self.synergy:
            # 重载消息队列
            instances = reset_task()
            if not instances:
                logger.debug(
                    f"{self.collector_id} The echo-loop collector goes to sleep."
                )
                return False
            # 重载任务队列
            self.is_running = self.offload_task(instances)
            if self.is_running is False:
                logger.debug(
                    f"{self.collector_id} The echo-loop collector goes to sleep."
                )
                return False
        elif (
                not self.is_running
                and len(self.running_jobs) == 0
                and self.workers.qsize() == 0
        ):
            # 迁移粘性任务，使用弹性协程生产实例
            if self.dt_extension() > 0:
                self.is_running = True
        # ===========================
        # 参数清洗
        # ===========================
        # 配置弹性采集功率
        power_ = self.power if self.power else power
        if self.max_queue_size != 0:
            power_ = self.max_queue_size if power_ > self.max_queue_size else power_
        self.power = power_
        # ===========================
        # 配置 launcher
        # ===========================
        task_list = []
        for _ in range(self.power):
            task = gevent.spawn(self.launcher)
            task_list.append(task)
        # ===========================
        # 启动 launcher
        # ===========================
        gevent.joinall(task_list)
        self.is_running = False

    def offload_task(self, instances: list) -> bool:
        # TODO 此处需要进行一轮收益计算，调整任务权重
        # 复制实体团
        pending_remote = instances.copy()
        # 无待解压实体（未分发任务）
        if len(pending_remote) == 0:
            return False
        # ======================================================
        # 读取实体特征加入协程工作队列
        # ======================================================

        # ------------------------------------------------------
        # 在非协同模式下正常导入任务
        # ------------------------------------------------------
        if not self.synergy:
            for atomic in pending_remote:
                self.workers.put_nowait(atomic)
        # ------------------------------------------------------
        # 在协同模式下使用均匀队列
        # ------------------------------------------------------
        else:
            # 实例超载算法，主观上认为核心数越大的基础设施应当优先级更低地执行 synergy 任务
            # 应当将 synergy 任务分发给核心数小但形成规模的虚拟切片运行
            limit = int((math.log2(os.cpu_count()) + 1) * 2)
            # 本机待执行队列数
            pending_local = self.workers.qsize() + self.running_jobs.__len__()
            # 若已超载，反射任务
            if pending_local >= limit:
                for atomic in pending_remote:
                    self.overload.put_nowait(atomic)
            else:
                # 可添加的数量
                limit -= pending_local
                if pending_remote.__len__() <= limit:
                    # 灌入摘要数据
                    for atomic in pending_remote:
                        self.workers.put_nowait(atomic)
                    # 容灾延拓
                    self.dt_extension(cursor=limit - pending_remote.__len__())
                else:
                    for atomic in pending_remote[:limit]:
                        self.workers.put_nowait(atomic)
                    for atomic in pending_remote[limit:]:
                        self.overload.put_nowait(atomic)
        # ======================================================
        # 更新执行任务数
        # ======================================================
        self.max_queue_size = self.workers.qsize()
        return True

    def launcher(self):
        while not self.workers.empty():
            atomic = self.workers.get_nowait()
            self.devil_king_armed(atomic)

    def devil_king_armed(self, atomic: dict):
        """
        一个映射了__entropy__站点源特征词典的SpawnEntity-Selenium运行实体
        :param atomic:
        :return:
        """
        # ================================================
        # [√] 调整运行实例的前置参数
        # ================================================
        # 任务模式切换 synergy | run
        is_synergy = bool(atomic.get("synergy"))
        _report_name = "Synergy" if is_synergy else "Instance"
        _hyper_params = atomic["hyper_params"]
        # 假假地停一下
        if is_synergy:
            _hyper_params["beat_dance"] = (self.running_jobs.__len__() + 1) * 1.7
        # ================================================
        # [√] 生产运行实例 更新系统运行状态
        # ================================================
        # 魔王武装
        alice = devil_king_armed(atomic, assault=True, silence=True)

        # 初始化运行实例配置
        api = alice.set_spider_option()

        # 内部异常捕获，延迟反射均摊运行风险
        # 已知可反射的异常有：`chromedriver` PermissionException;
        if not api:
            self.overload.put_nowait(atomic)
        # 标记运行实例
        alice_id = api.session_id
        alice_name = alice.action_name
        start_time = datetime.now()
        running_limit = int(sum([alice.work_clock_max_wait, self.echo_limit]) / 2)
        # ------------------------------------------------
        self.running_jobs.update(
            {
                alice_id: {
                    "api": api,
                    "start-time": start_time,
                    "running-limit": running_limit,
                    "name": alice_name,
                }
            }
        )
        # ================================================
        # [√] 实例投放
        # ================================================
        # (o゜▽゜)o☆
        try:
            if is_synergy:
                # HTTP状态码异常
                if not alice.check_heartbeat():
                    raise RuntimeError
                alice.synergy(api)
            else:
                alice.run(api)
        except RuntimeError:
            self.broadcast.to_runner(atomic)
            logger.warning(f">> {_report_name}ResetException <{alice_name}> "
                           f"protocol=overload session_id={alice_id} error=StatusException")
        except (ConnectionError, TimeoutError) as e:
            self.broadcast.to_runner(atomic)
            logger.warning(
                f">> {_report_name}ResetException <{alice_name}> "
                f"protocol=overload session_id={alice_id} error={e}"
            )
        # (￣ε(#￣) CTRL+C / strong anti-spider engine / is being DDOS
        except Exception as e:
            logger.error(f">> {_report_name}UnknownException <{alice_name}> "
                         f"error={e}")
        finally:
            # (/≧▽≦)/
            try:
                self.running_jobs.pop(alice_id)
                logger.debug(f">> Detach <{alice_name}> session_id={alice_id}")
            except (KeyError,):
                pass


class CollaboratorScheduler(CollectorScheduler):
    def __init__(self, synergy_workers: int = None):
        """
        采集器工作模式 影响到任务的读取以及执行规则。
            - run 载入本地任务队列，根据任务容载极限进行任务剪枝，最后执行正常的采集流程。
            - synergy 载入本地队列并剪枝后，拉取“云端”消息队列中的缓存实例，并入协程工作队列，最后执行分流的工作流程。
            也即根据具体的 atomic 运行上下文决定运行模式。
        """
        super(CollaboratorScheduler, self).__init__()

        self.power = min(synergy_workers, os.cpu_count()) if isinstance(synergy_workers, int) else os.cpu_count()

        # 采集器配置
        self.echo_limit: int = 300
        self.collector_id: str = "<CollaboratorHeartBeat-C>"
        self.echo_id: str = "echo-loop[C]"
        self.sync_step: int = 5
        self.is_pending: bool = True
        self.synergy: bool = True
        self.freeze_screen = True
        self.max_instances = 100

    def hosting(self):
        logger.success(f"{self.collector_id} 协同者加入聊天室！")

        # 初始化上下文容器
        context = {}

        # --> 处理线程 / heartbeat
        threading.Thread(target=self.deploy_jobs).start()

        for message in self.mq.listen(count=1):
            # 暂无可读任务
            if not message:
                continue

            # 读取待处理任务
            id_, task = message[0][0], message[0][-1]

            # 识别由采集器发出的控制指令
            try:
                # 获取待解压任务
                if task.get("pending"):
                    context: dict = ast.literal_eval(task.get("pending"))

                    # 任务在忙
                    if self.workers.qsize() > self.power:
                        self.broadcast.to_inviter(context)
                        logger.warning(
                            f"{self.collector_id} The local WorkerQueue is busy, "
                            f"and the pending tasks have been rejected."
                        )
                        time.sleep(10)
                        continue

                    # 任务分流
                    logger.success(
                        f"{self.collector_id} Load the remote message to be processed."
                    )
                    gevent.joinall([gevent.spawn(self._adaptor, context)])

                # 获取过热任务
                elif task.get("overload"):
                    context: dict = ast.literal_eval(task.get("overload"))
                    if self.distributor.qsize() > self.power:
                        try:
                            self.broadcast.to_runner(context)
                        except ConnectionResetError:
                            pass
                        logger.warning(
                            f"{self.collector_id} The local WorkerQueue is busy, "
                            f"and the pending tasks have been rejected."
                        )
                        time.sleep(60)
                    else:
                        logger.debug(
                            f"{self.collector_id} [{self.distributor.qsize() + 1}/100]"
                            f"Loading overheating task."
                            f" | action={context['name']}"
                        )
                        gevent.joinall([gevent.spawn(self._distribute, context)])
            # KeyboardInterrupt 回滚异常异常终端的消息
            except (KeyboardInterrupt,):
                try:
                    if context.get("atomic"):
                        self.broadcast.to_inviter(context=context)
                    else:
                        self.broadcast.to_runner(context=context)
                except Exception as e:
                    logger.error(f"{self.collector_id} Queue task rollback exception. {e}")
            except Exception as e:
                logger.exception(e)
            # 任务结束后必须去除 PEL
            # 可在异常捕获中以新消息的形式广播或转移运行失败的实例上下文摘要信息
            finally:
                self.mq.offload_task(id_)

    def _adaptor(self, context: dict):
        # 恢复现场
        hostname: str = context.get("hostname")
        cookie: str = context.get("cookie")

        # 标记协同任务
        tracer = "_runner"
        if not context.get(tracer):
            context[tracer] = self._runner["name"]
        if not self._runner["hook"].get(cookie):
            self._runner["hook"].update({cookie: 0, "hostname": hostname})

        # 重定向 register-url
        try:
            invite_link = DevilKingArmed.get_invite_link(cookie, hostname)
        # TODO AttributeError 元素获取异常，移交作业控制权
        except AttributeError:
            # 任务反射
            max_trace_num = 5
            self._runner["hook"][cookie] += 1
            if self._runner["hook"][cookie] < 5:
                self.broadcast.to_inviter(context=context)
                logger.warning(
                    f"{self.collector_id} Reflex abnormal task."
                    f" | hostname=`{hostname}`"
                    f" | {tracer}={context[tracer]}[{self._runner['hook'][cookie]}/{max_trace_num}]"
                )
            # 溯源消解
            else:
                logger.error(
                    f"{self.collector_id} Remove anomalous tasks and coordination roots."
                    f" | hostname=`{hostname}`"
                )
                # 将已加入 pool 的订阅移除
                # self.mq.remove_bad_code(
                #     context.get("_type", ""), context.get("_hook", "")
                # )
            return False

        # 接续任务：重置任务id
        context["atomic"]["register_url"] = invite_link
        context["atomic"]["synergy"] = True
        gain = context["gain"]
        atomic = context["atomic"]

        # 回滚任务
        pending_tasks = [atomic] * gain
        while not self.distributor.empty():
            pending_tasks.append(self.distributor.get())

        # 分发任务：广播 NewContext 或者重载本地任务队列
        self.is_running = self.offload_task(pending_tasks)
        while not self.overload.empty():
            overload_task: dict = self.overload.get_nowait()
            self.broadcast.to_runner(overload_task)

    def _distribute(self, atomic: dict):
        self.distributor.put_nowait(atomic)
