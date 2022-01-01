# -*- coding: utf-8 -*-
# Time       : 2021/12/22 18:48
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: Rouse the Cirilla.
from loguru import logger
from undetected_chromedriver.v2 import Chrome

from services.cluster import actions, devil_king_armed

# The Fighter
ATOMIC = actions.ActionZZCloud

# 隐藏指纹（高级特性，牺牲敏捷性，减少被识别的几率）
INCOGNITO = True
SILENCE = False


@logger.catch()
def demo(api=None):
    cirilla = devil_king_armed(ATOMIC, silence=SILENCE)
    cirilla.assault(api=api, force=True)


if __name__ == '__main__':
    demo(Chrome() if INCOGNITO else None)
