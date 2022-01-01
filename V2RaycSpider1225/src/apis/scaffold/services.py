# -*- coding: utf-8 -*-
# Time       : 2021/12/23 19:43
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import multiprocessing

from services.deploy import CollectorScheduler, SynergyScheduler
from services.settings import SCHEDULER_SETTINGS, logger
from services.utils import ToolBox

__all__ = ["SystemService"]


class SystemService:
    """部署前后端服务"""

    def __init__(
            self,
            enable_scheduler: bool = False,
            enable_synergy: bool = False,
            enable_flask: bool = False,
            **optional
    ):
        self.ACTION_NAME = "SystemService"

        self.enable_scheduler = enable_scheduler
        self.enable_synergy = enable_synergy
        self.enable_flask = enable_flask

        if enable_scheduler:
            self.scheduler_settings = self.calibrate(**optional)

    def calibrate(self, **optional):
        scheduler_settings = SCHEDULER_SETTINGS
        task_stack = ["collector", "decoupler"]

        for lok in task_stack:
            if not scheduler_settings.get(lok):
                scheduler_settings[lok] = {}
            if optional.get(lok) is not None:
                scheduler_settings[lok]["enable"] = optional.get(lok)

        scheduler_settings["collector"]["interval"] = max(120, scheduler_settings["collector"].get("interval", 120))
        scheduler_settings["decoupler"]["interval"] = max(600, scheduler_settings["decoupler"].get("interval", 600))

        for lok in task_stack:
            interval = scheduler_settings[lok]["interval"]
            logger.info(ToolBox.runtime_report(
                motive="JOB",
                action_name=f"{self.ACTION_NAME}|Configuration",
                message="Interval--({})--{}s".format(lok, interval)
            ))

        return scheduler_settings

    def service_scheduler(self):

        # 实例化子模块任务
        collector = CollectorScheduler(job_settings={
            "interval_collector": self.scheduler_settings["collector"]["interval"],
            "interval_decoupler": self.scheduler_settings["decoupler"]["interval"],
        })

        # 自适应部署子模块任务
        collector.deploy_jobs(
            available_collector=self.scheduler_settings["collector"]["enable"],
            available_decoupler=self.scheduler_settings["decoupler"]["enable"]
        )

    @staticmethod
    def service_synergy():
        synergy = SynergyScheduler()
        synergy.deploy()
        synergy.start()

    def startup(self):
        process_list = []
        try:

            if self.enable_scheduler:
                process_list.append(
                    multiprocessing.Process(
                        target=self.service_scheduler,
                        name=f"{self.ACTION_NAME}|Scheduler"
                    )
                )

            if self.enable_synergy:
                process_list.append(
                    multiprocessing.Process(
                        target=self.service_synergy,
                        name=f"{self.ACTION_NAME}|Synergy"
                    )
                )

            for process in process_list:
                process.start()
                logger.success(ToolBox.runtime_report(
                    motive="STARTUP",
                    action_name=process.name,
                    message="Activate child process."
                ))
            for process in process_list:
                process.join()
        except (KeyboardInterrupt, SystemExit):
            logger.debug(ToolBox.runtime_report(
                motive="EXITS",
                action_name=self.ACTION_NAME,
                message="Received keyboard interrupt signal."
            ))
            for process_ in process_list:
                process_.terminate()
        finally:
            logger.success(ToolBox.runtime_report(
                motive="EXITS",
                action_name=self.ACTION_NAME,
                message="V2RSS server exits completely."
            ))
