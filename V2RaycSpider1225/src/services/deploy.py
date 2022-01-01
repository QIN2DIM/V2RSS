# -*- coding: utf-8 -*-
# Time       : 2021/12/25 16:56
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import ast
import random
import time
import warnings
from datetime import datetime, timedelta

from apscheduler.events import (
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_MAX_INSTANCES,
    EVENT_JOB_ERROR,
)
from apscheduler.events import JobExecutionEvent
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from urllib3.exceptions import HTTPError

from services.cluster import __entropy__
from services.cluster import devil_king_armed
from services.cluster.mage import decouple
from services.middleware.subscribe_io import SubscribeManager
from services.middleware.workers_io import EntropyHeap, MessageQueue
from services.settings import logger, TIME_ZONE_CN, POOL_CAP
from services.utils import CoroutineSpeedup, Queue, ToolBox

warnings.simplefilter("ignore", category=UserWarning)


class CollectorScheduler(CoroutineSpeedup):
    def __init__(self, job_settings: dict = None):
        super(CollectorScheduler, self).__init__()

        job_settings = {} if job_settings is None else job_settings

        self.scheduler = BlockingScheduler()
        self._sm = SubscribeManager()
        self._eh = EntropyHeap()

        self.collector_name = "Cirilla[M]"
        self.checker_name = "Checker[M]"
        self.decoupler_name = "Decoupler[M]"

        self.scheduler_name = "CollectorScheduler[M]"

        self.job_settings = {
            "interval_collector": 120,
            "interval_decoupler": 600,
            # 任务队列源 within [remote local]
            "source": "remote"
        }
        self.job_settings.update(job_settings)
        self.interval_collector = self.job_settings["interval_collector"]
        self.interval_decoupler = self.job_settings["interval_decoupler"]
        self.task_source = self.job_settings["source"]

        self.running_jobs = {}

        # True: 不打印 monitor-log
        self.freeze_screen = False

    def deploy_jobs(self, available_collector=True, available_decoupler=True):
        if available_collector:
            self._deploy_collector()
            self.scheduler.add_listener(
                callback=self._monitor,
                mask=(EVENT_JOB_ERROR | EVENT_JOB_SUBMITTED | EVENT_JOB_MAX_INSTANCES)
            )
            logger.success(ToolBox.runtime_report(
                action_name=self.scheduler_name,
                motive="JOB",
                message="The Collector was created successfully."
            ))

        if available_decoupler:
            self._deploy_decoupler()
            logger.success(ToolBox.runtime_report(
                action_name=self.scheduler_name,
                motive="JOB",
                message="The Decoupler was created successfully."
            ))

        if any((available_decoupler, available_collector)):
            self.start()

    def start(self):
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            self.scheduler.shutdown()
            logger.debug(ToolBox.runtime_report(
                motive="EXITS",
                action_name=self.scheduler_name,
                message="Received keyboard interrupt signal."
            ))

    def _deploy_collector(self):
        self.scheduler.add_job(
            func=self.go,
            id=self.collector_name,
            trigger=IntervalTrigger(
                seconds=self.interval_collector,
                timezone="Asia/Shanghai",
                jitter=5
            ),
            max_instances=4
        )
        self.scheduler.add_job(
            func=self._sm.refresh,
            id=self.checker_name,
            trigger=IntervalTrigger(
                seconds=60,
                timezone="Asia/Shanghai",
                jitter=4
            ),
            max_instances=20,
            misfire_grace_time=20
        )

    def _deploy_decoupler(self):
        self.scheduler.add_job(
            func=decouple,
            id=self.decoupler_name,
            trigger=IntervalTrigger(
                seconds=self.interval_decoupler,
                timezone="Asia/Shanghai"
            ),
            max_instances=15,
        )

    def _monitor_logger(self, event: JobExecutionEvent):
        debug_log = {
            "event": event,
            "pending_jobs": self.worker.qsize(),
            "running_jobs": len(self.running_jobs),
            "message": "pending_jobs[{}] running_jobs[{}]".format(
                self.worker.qsize(), self.running_jobs.__len__(),
            ),
        }

        if not self.freeze_screen:
            pool_status = "pool_status[{}/{}]".format(
                self._eh.__len__(), POOL_CAP
            )
            message = "{} {}".format(
                debug_log.get("message"), pool_status
            )
            logger.debug(ToolBox.runtime_report(
                motive="HEARTBEAT",
                action_name=self.scheduler_name,
                message=message,
                job_id=event.job_id if event.code >= 2 ** 9 else "__init__",
                event=event
            ))

    def _monitor(self, event):
        self._monitor_logger(event)

        if self.running_jobs.__len__() == 0:
            return True

        # 识别并移除失活实例
        for session_id, instance in list(self.running_jobs.items()):
            is_timeout = (
                    instance["start-time"]
                    + timedelta(seconds=instance["running-limit"])
                    < datetime.now(TIME_ZONE_CN)
            )
            if not is_timeout:
                continue

            try:
                instance["service"].quit()
                self.running_jobs.pop(session_id)
                logger.error(ToolBox.runtime_report(
                    motive="KILL",
                    action_name=instance["name"],
                    inactivated_instance=session_id
                ))
            except (HTTPError, ConnectionError) as e:
                logger.critical(ToolBox.runtime_report(
                    motive="ERROR",
                    action_name=instance["name"],
                    by="CollectorSchedulerMonitor停用失活实例时出现未知异常",
                    error=e
                ))

        # 重置定时任务
        if (
                len(self.running_jobs) == 0
                and self.worker.qsize() == 0
        ):
            self.scheduler.remove_job(job_id=self.collector_name)
            self.scheduler.remove_job(job_id=self.checker_name)
            self._deploy_collector()

            logger.warning(ToolBox.runtime_report(
                motive="HEARTBEAT",
                action_name=self.scheduler_name,
                message="The echo-loop job of collector has been reset."
            ))

    def is_healthy(self):
        if not self._eh.ping():
            self._eh = EntropyHeap()
            return False
        if not self._sm.ping():
            self._sm = SubscribeManager()
            return False
        return True

    # ---------------------
    # Coroutine
    # ---------------------
    def preload(self):
        """

        :return:
        """

        # 检测心跳
        if not self.is_healthy():
            return []

        # 根据任务源选择本地/远程任务队列 默认使用远程队列
        pending_entropy = self._eh.sync() if self.task_source == "remote" else __entropy__.copy()

        # 弹回空任务，防止订阅溢出
        if self._eh.__len__() >= POOL_CAP or not pending_entropy:
            return []

        # 消减任务实例，控制订阅池容量
        mirror_entropy = pending_entropy.copy()
        qsize = pending_entropy.__len__()
        random.shuffle(mirror_entropy)

        while self._eh.__len__() + qsize > int(POOL_CAP * 0.8):
            if mirror_entropy.__len__() < 1:
                break
            mirror_entropy.pop()
            qsize -= 1

        return mirror_entropy

    def overload(self):
        mirror_entropy = self.preload()

        if not mirror_entropy:
            self.max_queue_size = 0
            return False

        for atomic in mirror_entropy:
            self.worker.put_nowait(atomic)

        self.max_queue_size = self.worker.qsize()

    def launcher(self, *args, **kwargs):
        while not self.worker.empty():
            atomic = self.worker.get_nowait()
            self.control_driver(atomic=atomic, sm=self._sm, *args, **kwargs)

    @logger.catch()
    def control_driver(self, atomic: dict, *args, **kwargs):
        """

        :param atomic:
        :return:
        """

        """
        TODO [√]参数调整
        -------------------
        """
        # 协同模式
        is_synergy = bool(atomic.get("synergy"))

        # 添加节拍集群节拍
        if not atomic.get("hyper_params"):
            atomic["hyper_params"] = {}
        atomic["hyper_params"]["beat_dance"] = 0.5 * (self.max_queue_size - self.worker.qsize() + 1)

        """
        TODO [√]实例生产
        -------------------
        """
        cirilla = devil_king_armed(atomic, silence=True)

        service = cirilla.set_chrome_options()
        cirilla_id = service.session_id

        # 标记运行实例
        self.running_jobs.update(
            {
                cirilla_id: {
                    "service": service,
                    "start-time": datetime.now(TIME_ZONE_CN),
                    "running-limit": cirilla.work_clock_max_wait,
                    "name": cirilla.action_name
                }
            }
        )
        """
        TODO [√]实例投放
        -------------------
        """
        try:
            cirilla.assault(service, synergy=is_synergy, sm=kwargs.get("sm"))
        # 滤除外部中断引起的一系列连接异常，这是意料之中的可控情况
        except (HTTPError, ConnectionError):
            pass
        finally:
            try:
                self.running_jobs.pop(cirilla_id)
            except KeyError:
                pass


class SynergyScheduler(CollectorScheduler):
    def __init__(self):
        super(SynergyScheduler, self).__init__()

        self.scheduler_name = "SynergyScheduler[M]"
        self.scheduler = BlockingScheduler()

        self._mq = MessageQueue()
        self.pending = Queue(maxsize=4)
        self.worker = Queue(maxsize=4)

    def deploy(self):
        """

        :return:
        """
        # 同步远程协同指令
        self.scheduler.add_job(
            func=self.sync_context,
            id="sync_remote_tasks",
            trigger=DateTrigger(
                timezone="Asia/Shanghai"
            ),
        )

        # 处理协同任务
        self.scheduler.add_job(
            func=self.go,
            id=self.scheduler_name,
            trigger=IntervalTrigger(
                seconds=5,
                timezone="Asia/Shanghai",
            ),
            max_instances=4,
            misfire_grace_time=2000
        )

    def is_overheating(self):
        return True if self.pending.full() and (not self.worker.empty()) else False

    def is_healthy(self):
        if not self._mq.ping():
            self._mq = MessageQueue()
            return False
        return True

    def sync_context(self):
        """

        IF not pending.empty():
            pending --(N)--> worker
        ELIF worker.qsize() < threshold:
            worker.put(remote-tasks)
        ELIF pending.qsize() < threshold:
            pending.put(remote-tasks)
            # 将本地代办任务的上下文摘要数据拷贝一份至远程队列
            local-task --(N)--> RemoteMessageQueue[RedisList]

        # 当本地缓存队列以及工作队列都处于闲时状态 且远程待办队列非空时 下载任务
        IF pending.empty() and worker.empty():
            IF RemoteMessageQueue[RedisList] != []:
                RemoteMessageQueue[RedisList] --(N)--> worker

        :return:
        """

        logger.success(ToolBox.runtime_report(
            motive="JOB",
            action_name=self.scheduler_name,
            message="协同者加入聊天室！"
        ))

        for message in self._mq.listen(count=1):

            if not message:
                continue

            message_id, synergy_context = message[0][0], message[0][-1]
            context = {}
            try:
                context: dict = ast.literal_eval(synergy_context.get(self._mq.SYNERGY_PROTOCOL, ""))

                # 异常的上下文数据
                if not context:
                    raise ValueError
                # 过滤不影响运行的空对象，避免无意义的CPU空转
                if not context.get("atomic"):
                    raise ValueError

                # 检查系统负载
                if self.is_overheating():
                    self._mq.broadcast_synergy_context(context)
                    logger.warning(ToolBox.runtime_report(
                        motive="SKIP",
                        action_name=self.scheduler_name,
                        message="节点过热，不接收新的协同任务",
                        sleep="60s"
                    ))
                    time.sleep(60)
                    continue

            except (ValueError, SyntaxError, AttributeError):
                logger.warning(ToolBox.runtime_report(
                    motive="SKIP",
                    action_name=self.scheduler_name,
                    message="捕获到上下文协议异常的脏数据，协同任务已跳过"
                ))
            except KeyboardInterrupt:
                if context:
                    self._mq.broadcast_synergy_context(context)
            else:
                self._adaptor(context)
            finally:
                self._mq.ack(message_id)
                time.sleep(0.5)

    def _adaptor(self, context: dict):
        atomic = context["atomic"]
        self.pending.put(atomic)

    def preload(self):
        mirror_entropy = []
        while not self.worker.full() and not self.pending.empty() and self.running_jobs.__len__() < 4:
            synergy_context = self.pending.get_nowait()
            mirror_entropy.append(synergy_context)

        return mirror_entropy
