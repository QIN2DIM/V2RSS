# -*- coding: utf-8 -*-
# Time       : 2021/12/22 18:48
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: Rouse the Cirilla.
import sys

sys.path.append("src")
from loguru import logger
from undetected_chromedriver.v2 import Chrome

from services.collector import actions, devil_king_armed
from services.settings import PATH_CHROMEDRIVER

# The Fighter
ATOMIC = actions.ActionFETVCloud

# 隐藏指纹（高级特性，牺牲敏捷性，减少被识别的几率）
INCOGNITO = False
SILENCE = True


@logger.catch()
def demo(api=None):
    cirilla = devil_king_armed(ATOMIC, silence=SILENCE)
    cirilla.assault(api=api, force=False)


if __name__ == '__main__':
    demo(Chrome(executable_path=PATH_CHROMEDRIVER) if INCOGNITO else None)
