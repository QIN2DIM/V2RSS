# -*- coding: utf-8 -*-
# Time       : 2021/12/22 9:00
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 催化剂
from typing import Dict, Any, Optional

from .exceptions import UnknownNestTypeException
from .nest import (
    LionCubOfCintra,
    LaraDorren,
    LunarPrincessRani,
    StarscourgeRadahn,
    MohgLordOfBlood,
    MimicTear,
)


def devil_king_armed(
    atomic: Dict[str, Any], silence: Optional[bool] = True, mirror: Optional[bool] = False
):
    """Production line for running instances"""
    # fmt:off
    machine = {
        "v2board": LaraDorren,
        "sspanel": LionCubOfCintra,
        "material": LunarPrincessRani,
        "cool": StarscourgeRadahn,
        "metron": MohgLordOfBlood,
        "super-generics": MimicTear,
    }
    # fmt:on

    # 剔除异常构造机器
    blood = atomic.get("nest", "")
    if not blood or not machine.get(blood):
        raise UnknownNestTypeException

    # 生产上古之血
    cirilla = machine[blood](atomic=atomic, silence=silence)
    return cirilla if mirror is False else cirilla.assault
