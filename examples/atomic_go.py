# -*- coding: utf-8 -*-
# Time       : 2021/12/22 18:48
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: Rouse the Cirilla.
import sys

sys.path.append("src")
from loguru import logger

from services.collector import actions, devil_king_armed

ATOMIC = actions.ActionGroundhogCloud

SILENCE = True


@logger.catch()
def demo():
    devil_king_armed(ATOMIC, silence=SILENCE).assault()


if __name__ == "__main__":
    demo()
