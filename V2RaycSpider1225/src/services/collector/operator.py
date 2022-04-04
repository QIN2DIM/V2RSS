# -*- coding: utf-8 -*-
# Time       : 2021/12/22 9:00
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 催化剂
from typing import Dict, Any, Optional

from .exceptions import UnknownNestTypeException
from .nest import LionCubOfCintra, LaraDorren


def devil_king_armed(
    atomic: Dict[str, Any], silence: Optional[bool] = True, mirror: Optional[bool] = False
):
    """
    Production line for running instances

    :param atomic:
    :param silence:
    :param mirror:
    :return:
    """
    # fmt:off
    the_tarnished = {
        "sspanel": LionCubOfCintra,
        "v2board": LaraDorren
    }
    # fmt:on

    # 剔除异常构造机器
    blood = atomic.get("nest", "")
    if not blood or not the_tarnished.get(blood):
        raise UnknownNestTypeException

    # 生产上古之血
    cirilla = the_tarnished[blood](atomic=atomic, silence=silence)
    return cirilla if mirror is False else cirilla.assault
