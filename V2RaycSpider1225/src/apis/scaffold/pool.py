# -*- coding: utf-8 -*-
# Time       : 2022/1/13 22:14
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from services.collector import decouple
from services.middleware.subscribe_io import SubscribeManager
from services.middleware.workers_io import EntropyHeap
from services.settings import logger
from services.utils import ToolBox

sm = SubscribeManager()
eh = EntropyHeap()


@logger.catch()
def status():
    pool_status = sm.get_pool_status()
    ToolBox.echo(str(pool_status) if pool_status else "无可用订阅", 1 if pool_status else 0)


@logger.catch()
def overdue():
    try:
        pool_len = sm.refresh()
        logger.debug(
            ToolBox.runtime_report(
                motive="OVERDUE",
                action_name="RemotePool | SpawnRhythm",
                message="pool_status[{}/{}]".format(pool_len, eh.get_unified_cap()),
            )
        )
    except ConnectionError:
        pass


@logger.catch()
def decouple_():
    logger.info(
        ToolBox.runtime_report(
            motive="DECOUPLE",
            action_name="ScaffoldDecoupler",
            message="Clearing invalid subscriptions...",
        )
    )
    decouple(debug=True)
