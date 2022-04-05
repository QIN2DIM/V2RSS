# -*- coding: utf-8 -*-
# Time       : 2021/12/22 9:04
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from typing import Optional, Sequence


class AntiEmailException(Exception):
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


class GetEmailTimeout(AntiEmailException):
    """获取临时邮箱账号超时"""


class GetEmailCodeTimeout(AntiEmailException):
    """获取验证码超时"""
