# __all__ = ['apis_version_manager']

import csv

from BusinessCentralLayer.middleware.subscribe_io import to_admin
from config import *


def apis_capture_subscribe(style: dict) -> dict:
    """

    @param style:
    @return:
    """
    response = {"msg": "failed", "info": ""}
    try:
        # 提取subs class
        if style.get('type') in CRAWLER_SEQUENCE:

            # 读取缓存文件
            try:
                with open(NGINX_SUBSCRIBE.format(style.get('type')), 'r', encoding='utf-8') as f:
                    response.update(
                        {'info': f.read(), 'msg': 'success'})
            # error 文件路径有误或文件缺失
            except FileNotFoundError:
                response.update(
                    {'info': 'Server denied access'})
        # 接口错误引用，type-value is None
        else:
            response.update(
                {'info': 'Request parameter error'})
    finally:
        return response


def apis_version_manager(vcs_path: str, usr_version: str = None, encoding='utf8', header=True) -> dict:
    """
    默认使用csv文件存储版本数据，视最后一行数据为最新版本,而client使用 ！= 判断版本新旧。
    @param vcs_path: 传入vcs版本管理文件的地址
    @param usr_version: 用户本地客户端的版本号
    @param encoding: 文件编码类型
    @param header: 是否有表头
    @return: 返回最新软件的版本号以及下载地址
    """
    response = {'msg': 'success', 'version-server': '',
                'version-usr': usr_version, 'url': '', 'need_update': False}
    try:
        # TODO 1.打开回溯文件
        with open(vcs_path, 'r', encoding=encoding, ) as f:
            data = [i for i in csv.reader(f) if i]

        # TODO 2.获取服务器文件版本号以及下载地址
        if header:
            response.update(
                {'version-server': data[1:][-1][0], 'url': data[1:][-1][1]})
        else:
            response.update(
                {'version-server': data[-1][0], 'url': data[-1][1]})

        # TODO 3.比对版本号 -> if need to update
        if usr_version and response['version-server'] != usr_version:
            response.update({'need_update': True})
        elif not usr_version:
            response = {'latestVersion': response['version-server']}
    # FIXME 回溯文件缺失 or 传参错误
    except FileNotFoundError:
        response = {'msg': 'failed'}
    finally:
        return response


def apis_refresh_broadcast(show_path: str = NGINX_SUBSCRIBE, hyper_params: dict = None):
    response = {"msg": "failed", "info": ""}
    hyper_admin = hyper_params.get('admin')
    new_subs = hyper_params.get("subs")
    if not hyper_admin != 'zeus':
        return {"msg": "failed", 'info': 'You are not an administrator！'}

    try:
        with open(show_path, 'w', encoding='utf8') as f:
            f.write(new_subs)
            response.update({'msg': 'success', 'info': f'upload new subs: {new_subs}'})
    except FileNotFoundError:
        response.update({"info": 'Traceback file is missing'})
    finally:
        return response


def apis_admin_pop(command_: str):
    if command_ in CRAWLER_SEQUENCE:
        return to_admin(command_)
