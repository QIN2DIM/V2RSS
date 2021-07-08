# TODO 请在运行程序前确保已正确配置config.py运行参数
from sys import argv

from src.BusinessCentralLayer.scaffold import scaffold

"""欢迎使用V2Ray云彩姬"""
if __name__ == '__main__':
    scaffold.startup(driver_command_set=argv)
