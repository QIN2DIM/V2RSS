# -*- coding: utf-8 -*-
# Time       : 2021/10/6 18:38
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import shlex

import requests
from bs4 import BeautifulSoup


def shell_echo(cmd: str, mode="default"):
    """
    为输出安全做的协调函数
    :param cmd:
    :param mode:
    :return:
    """
    if mode == "default":
        return os.system(cmd)
    if mode == "safe":
        return os.system(shlex.quote(cmd))


THIS_WALK = "."
CHROMEDRIVER_UNZIP_PATH = "src/BusinessCentralLayer/chromedriver"


def set_ubuntu_dev():
    shell_echo("apt-get update && apt-get install -y gcc wget unzip")


def set_google_chrome():
    # Google-chrome already exists in the current environment
    if shell_echo("google-chrome --version") == 0:
        # uninstall command
        # os.system("sudo rpm -e google-chrome-stable")
        return True

    # installing Google Chrome on Ubuntu
    shell_echo(
        "wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb >/dev/null"
    )
    shell_echo(
        "apt install ./google-chrome-stable_current_amd64.deb -y >/dev/null"
    )


def set_chromedriver(unzip_path=None):
    # chromedriver 的解压安装目录
    unzip_path = "/usr/bin/chromedriver" if unzip_path is None else unzip_path

    # 读取 google-chrome 的发行版本 Such as 89.0.4389.23
    chrome_version = (
        "".join(os.popen("google-chrome --version").readlines()).strip().split(" ")[-1]
    )

    # 访问 chromedriver 镜像
    res = requests.get("http://npm.taobao.org/mirrors/chromedriver")
    soup = BeautifulSoup(res.text, "html.parser")

    # 通过文件名清洗定位到所需版本文件的下载地址
    options = [
        i.split("/")[0]
        for i in soup.text.split("\n")
        if i.startswith(chrome_version[:5])
    ]
    if len(options) == 1:
        chromedriver_version = options[0]
    else:
        chromedriver_version = max(options)

    # 拉取 chromedriver
    shell_echo(
        f"wget http://npm.taobao.org/mirrors/chromedriver/{chromedriver_version}"
        "/chromedriver_linux64.zip >/dev/null"
    )

    # 解压 chromedriver
    shell_echo("unzip chromedriver_linux64.zip >/dev/null")

    # 死循环等待解压完成
    while True:
        if "chromedriver" not in list(os.walk(THIS_WALK))[0][-1]:
            pass
        else:
            break

    # 给予 chromedriver 运行运行权限
    shell_echo("chmod +x chromedriver >/dev/null")

    # 将 chromedriver 移动到预设的解压安装目录
    shell_echo(f"mv -f chromedriver {unzip_path} >/dev/null")


def init_project():
    print("---> Remove irrelevant information")
    shell_echo("rm -rf chromedriver_linux64.zip")
    shell_echo("rm -rf google-chrome-stable_current_x86_64.rpm")
    shell_echo("clear")


def run():
    set_ubuntu_dev()
    set_google_chrome()
    set_chromedriver(CHROMEDRIVER_UNZIP_PATH)
    # 清理运行缓存
    init_project()


if __name__ == "__main__":
    run()
