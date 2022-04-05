# -*- coding: utf-8 -*-
# Time       : 2022/2/10 22:16
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import sys
import webbrowser

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import get_browser_version_from_os

from services.settings import logger
from services.utils import ToolBox

ACTION_NAME = "ScaffoldInstaller"


def _download_driver():
    """自动拉取 Chrome 以及 ChromeDriver"""
    logger.debug("适配 ChromeDriver...")

    browser_version = get_browser_version_from_os("google-chrome")
    if browser_version != "UNKNOWN":
        return ChromeDriverManager(version="latest").install()

    logger.critical("当前环境变量缺少 `google-chrome`，请为你的设备手动安装 Chrome 浏览器。")
    logger.info(
        "Ubuntu: https://linuxize.com/post/how-to-install-google-chrome-web-browser-on-ubuntu-20-04/"
    )
    logger.info(
        "CentOS 7/8: https://linuxize.com/post/how-to-install-google-chrome-web-browser-on-centos-7/"
    )
    if "linux" not in sys.platform:
        webbrowser.open("https://www.google.com/chrome/")
    logger.info("安装完毕后重新执行 `install` 脚手架指令。")


def run():
    """下载项目运行所需的各项依赖"""
    logger.debug(
        ToolBox.runtime_report(
            motive="BUILD", action_name=ACTION_NAME, message="正在下载系统依赖"
        )
    )

    _download_driver()

    logger.success(
        ToolBox.runtime_report(motive="GET", action_name=ACTION_NAME, message="系统依赖下载完毕")
    )
