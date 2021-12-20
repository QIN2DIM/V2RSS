# -*- coding: utf-8 -*-
# Time       : 2021/12/20 16:25
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import shutil

from BusinessCentralLayer.setting import (
    SERVER_DIR_DATABASE_LOG,
    SERVER_DIR_DATABASE_CACHE,
    SERVER_DIR_STORE_COLLECTOR
)
from config import terminal_echo


def clear():
    _permission = {
        "logs": input(terminal_echo("是否清除所有运行日志[y]?", 2)),
        "cache": input(terminal_echo("是否清除所有运行缓存[y]?", 2)),
    }

    # 清除日志 ~/database/logs
    if os.path.exists(SERVER_DIR_DATABASE_LOG) and _permission["logs"].startswith(
            "y"
    ):
        history_logs = os.listdir(SERVER_DIR_DATABASE_LOG)
        for _log_file in history_logs:
            if len(_log_file.split(".")) > 2:
                _log_path = os.path.join(SERVER_DIR_DATABASE_LOG, _log_file)
                os.remove(_log_path)
                terminal_echo(f"清除运行日志-->{_log_path}", 3)

    # 清除运行缓存 ~/database/
    if _permission["cache"].startswith("y"):
        cache_blocks = {
            # ~/database/temp_cache/
            SERVER_DIR_DATABASE_CACHE,
            # ~/database/sspanel_hosts/
            SERVER_DIR_STORE_COLLECTOR,
        }

        for block in cache_blocks:
            # 扫描文件
            if os.path.exists(block):
                _files = [os.path.join(block, i) for i in os.listdir(block)]
                # 清除文件
                for _file in _files:
                    if os.path.isfile(_file):
                        os.remove(_file)
                    else:
                        shutil.rmtree(_file)
                        os.mkdir(_file)
                    terminal_echo(f"清除运行缓存-->{_file}", 3)
        terminal_echo("系统缓存文件清理完毕", 1)
