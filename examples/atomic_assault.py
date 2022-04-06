# -*- coding: utf-8 -*-
# Time       : 2021/12/22 18:48
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: The Elder Blood is about to be activated!
import sys

sys.path.append("src")
from gevent import monkey

monkey.patch_all()
from services.collector import actions
from apis.scaffold.runner import booster
from loguru import logger

# The Fighter
ATOMIC = actions.ActionHuoXingCloud

POWER = 4


@logger.catch()
def demo():
    booster(ATOMIC, silence=True, power=POWER)


if __name__ == "__main__":
    demo()
