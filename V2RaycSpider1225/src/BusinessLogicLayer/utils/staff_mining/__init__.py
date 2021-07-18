"""
    - 集爬取、清洗、分类与测试为一体的STAFF采集队列自动化更新组件
    - 需要本机启动系统全局代理，或使用“国外”服务器部署
"""
from .common import exceptions
from .support.staff_checker import StaffChecker, IdentifyRecaptcha, StaffEntropyGenerator
from .support.staff_collector import StaffCollector

__version__ = 'v0.1.1'

__all__ = ['StaffCollector', 'IdentifyRecaptcha', 'StaffEntropyGenerator', 'StaffChecker', 'exceptions']
