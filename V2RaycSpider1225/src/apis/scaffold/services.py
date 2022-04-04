# -*- coding: utf-8 -*-
# Time       : 2021/12/23 19:43
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from services.deploy import CollectorScheduler
from services.settings import SCHEDULER_SETTINGS, logger
from services.utils import ToolBox

__all__ = ["SystemCrontab"]


class SystemCrontab:
    """部署定时任务"""

    def __init__(self, **optional):
        self.ACTION_NAME = "SystemService"

        self.scheduler_settings = self.calibrate(**optional)

    def calibrate(self, **optional):
        scheduler_settings: dict = SCHEDULER_SETTINGS
        task_stack = ["collector", "decoupler"]

        for lok in task_stack:
            if not scheduler_settings.get(lok):
                scheduler_settings[lok] = {}
            if optional.get(lok) is not None:
                scheduler_settings[lok]["enable"] = optional.get(lok)

        scheduler_settings["collector"]["interval"] = max(
            120, scheduler_settings["collector"].get("interval", 120)
        )
        scheduler_settings["decoupler"]["interval"] = max(
            600, scheduler_settings["decoupler"].get("interval", 600)
        )

        for lok in task_stack:
            interval = scheduler_settings[lok]["interval"]
            logger.info(
                ToolBox.runtime_report(
                    motive="JOB",
                    action_name=f"{self.ACTION_NAME}|Configuration",
                    message="Interval--({})--{}s".format(lok, interval),
                )
            )

        return scheduler_settings

    def service_scheduler(self):
        """部署系统定时任务"""
        # 实例化子模块任务
        collector = CollectorScheduler(
            job_settings={
                "interval_collector": self.scheduler_settings["collector"]["interval"],
                "interval_decoupler": self.scheduler_settings["decoupler"]["interval"],
            }
        )

        # 自适应部署子模块任务
        collector.deploy_jobs(
            available_collector=self.scheduler_settings["collector"]["enable"],
            available_decoupler=self.scheduler_settings["decoupler"]["enable"],
        )
