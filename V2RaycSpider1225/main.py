# -*- coding: utf-8 -*-
# Time    : 2021/3/7 18:04
# Author  : QIN2DIM
# Github  : https://github.com/QIN2DIM
# Description: Welcome to use V2RayCloudSpider

from sys import argv

from src.BusinessCentralLayer.scaffold import scaffold

if __name__ == '__main__':
    scaffold.startup(driver_command_set=argv)
