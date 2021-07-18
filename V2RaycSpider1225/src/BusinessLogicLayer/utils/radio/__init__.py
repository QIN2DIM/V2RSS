"""
各种人机通信措施 ，如邮件通知，server酱
"""
from .common.exceptions import *
from .support.email import send_email
from .support.sercerchan import server_chan

__version__ = 'v0.1.1'

__all__ = ['send_email', 'server_chan']
