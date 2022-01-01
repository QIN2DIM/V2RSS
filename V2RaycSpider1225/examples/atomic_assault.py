# -*- coding: utf-8 -*-
# Time       : 2021/12/22 18:48
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: The Elder Blood is about to be activated!
from gevent import monkey

monkey.patch_all()
from services.cluster import actions
from apis.scaffold.runner import booster
from loguru import logger

# The Fighter
ATOMIC = actions.ActionFETVCloud

POWER = 1


@logger.catch()
def demo():
    booster(ATOMIC, silence=True, power=POWER)


if __name__ == '__main__':
    demo()
