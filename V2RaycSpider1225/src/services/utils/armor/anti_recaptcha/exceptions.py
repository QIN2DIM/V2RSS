# -*- coding: utf-8 -*-
# Time       : 2022/1/4 13:15
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from typing import Optional, Sequence


class AntiReCaptchaException(Exception):
    def __init__(
        self, msg: Optional[str] = None, stacktrace: Optional[Sequence[str]] = None
    ) -> None:
        self.msg = msg
        self.stacktrace = stacktrace
        super().__init__()

    def __str__(self) -> str:
        exception_msg = "Message: {}\n".format(self.msg)
        if self.stacktrace:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += "Stacktrace:\n{}".format(stacktrace)
        return exception_msg


class RiskControlSystemArmor(AntiReCaptchaException):
    """出现不可抗力的风控拦截"""


class AntiBreakOffWarning(AntiReCaptchaException):
    """切换到声纹验证异常时抛出，此时在激活checkbox时就已经通过了验证，无需进行声纹识别"""


class ElementLocationException(AntiReCaptchaException):
    """多语种问题导致的强定位方法失效"""
