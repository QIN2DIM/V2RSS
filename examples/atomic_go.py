# -*- coding: utf-8 -*-
# Time       : 2021/12/22 18:48
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: Rouse the Cirilla.
import sys

sys.path.append("src")
from loguru import logger

from services.collector import actions, devil_king_armed
from undetected_chromedriver import Chrome

# The Fighter
ATOMIC = actions.ActionLillianCloud

# 隐藏指纹（高级特性，牺牲敏捷性，减少被识别的几率）
INCOGNITO = False
SILENCE = True


@logger.catch()
def demo():
    cirilla = devil_king_armed(ATOMIC, silence=SILENCE)
    cirilla.assault(ctx=None if not INCOGNITO else Chrome(headless=SILENCE), force=False)


if __name__ == "__main__":
    demo()
