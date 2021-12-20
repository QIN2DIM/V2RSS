# -*- coding: utf-8 -*-
# Time       : 2021/7/21 20:56
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from .support.anti_email.core import (
    EmailRelay,
    apis_get_email_context,
    apis_get_verification_code
)
from .support.anti_recaptcha.core import (
    activate_recaptcha,
    handle_audio,
    parse_audio,
    submit_recaptcha
)
from .support.anti_slider.adaptive import GeeTestAdapter
from .support.anti_slider.geetest_v2 import GeeTest2
from .support.anti_slider.geetest_v3 import GeeTest3

__version__ = "0.1.1"

__all__ = ["GeeTest2", "GeeTest3", "GeeTestAdapter", "EmailRelay",
           "apis_get_email_context", "apis_get_verification_code",
           "activate_recaptcha", "handle_audio", "parse_audio", "submit_recaptcha"]
