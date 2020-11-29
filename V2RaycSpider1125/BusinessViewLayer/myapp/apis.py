# __all__ = ['apis_version_manager']

import csv


def apis_capture_subscribe(style: dict):
    """

    @param style:
    @return:
    """
    from config import CRAWLER_SEQUENCE,NGINX_SUBSCRIBE
    response = {}
    try:
        if style.get('type') in CRAWLER_SEQUENCE:
            try:
                with open(NGINX_SUBSCRIBE.format(style.get('type')), 'r', encoding='utf-8') as f:
                    response.update(
                        {'info': f.read(), 'text_body': 'success', 'remark': 'Cache link'})
            except FileNotFoundError:
                response.update(
                    {'info': 'Server denied access', 'text_body': 'failed'})
        else:
            response.update(
                {'info': 'Request parameter error', 'text_body': 'failed'})
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
    print(response)
    try:
        with open(vcs_path, 'r', encoding=encoding, ) as f:
            data = [i for i in csv.reader(f) if i]
        if header:
            response.update(
                {'version-server': data[1:][-1][0], 'url': data[1:][-1][1]})
        else:
            response.update(
                {'version-server': data[-1][0], 'url': data[-1][1]})

        if usr_version and response['version-server'] != usr_version:
            response.update({'need_update': True})
        elif not usr_version:
            response = {'latestVersion': response['version-server']}

    except FileNotFoundError:
        response = {'msg': 'failed'}
    finally:
        return response
