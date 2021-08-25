__all__ = [
    'apis_admin_get_subs',
    'apis_admin_get_subs_v2',
    'apis_admin_get_subs_v2_debug',
    "apis_admin_get_entropy",

    'apis_get_subs_num',
    'apis_version_manager',
    'apis_capture_subscribe',
]

import csv

from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.middleware.subscribe_io import pop_subs_to_admin, select_subs_to_admin
from src.BusinessCentralLayer.setting import CRAWLER_SEQUENCE, NGINX_SUBSCRIBE, SERVER_PATH_DEPOT_VCS, REDIS_SECRET_KEY


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


def apis_version_manager(
        vcs_path: str = SERVER_PATH_DEPOT_VCS,
        usr_version: str = None,
        encoding='utf8',
        header=True
) -> dict:
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
        with open(vcs_path, 'r', encoding=encoding) as f:
            data = [i for i in csv.reader(f) if i]

        # TODO 2.获取服务器文件版本号以及下载地址
        if header:
            response.update(
                {'version-server': data[1:][-1][0], 'url': data[1:][-1][1]})
        else:
            response.update(
                {'version-server': data[-1][0], 'url': data[-1][1]})

        # TODO 3. response params of Get methods
        if not usr_version:
            return {'latestVersion': response['version-server']}

        # TODO 4.比对版本号 -> if need to update
        usr_version_cmp = usr_version.split('.')
        server_version_cmp = response['version-server'].split('.')
        for i in range(len(usr_version_cmp)):
            if int(server_version_cmp[i]) > int(usr_version_cmp[i]):
                response.update({'need_update': True})
                break
        else:
            response.update({'need_update': False})
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


def apis_admin_get_subs(command_: str):
    if not (command_ and isinstance(command_, str)) or command_ not in CRAWLER_SEQUENCE:
        return {"msg": "failed", "info": "参数类型错误"}
    return pop_subs_to_admin(command_)


def apis_get_subs_num() -> dict:
    return RedisClient().subs_info()


def apis_admin_get_entropy() -> list:
    return RedisClient().get_driver().get(REDIS_SECRET_KEY.format("__entropy__")).split("$")


def apis_admin_get_subs_v2(entropy_name: str = None) -> dict:
    return select_subs_to_admin(select_netloc=entropy_name)


def apis_admin_get_subs_v2_debug(entropy_name: str = None, _debug=True) -> dict:
    """测试接口|获取链接后，该链接不会被主动移除"""
    return select_subs_to_admin(select_netloc=entropy_name, _debug=_debug)


if __name__ == '__main__':
    print(apis_admin_get_subs_v2_debug(entropy_name="r"))
