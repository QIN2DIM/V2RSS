__all__ = ['api']

import os
import random
from string import printable

import paramiko

from src.BusinessCentralLayer.scaffold import command_set
from src.BusinessCentralLayer.setting import logger, SERVER_DIR_PROJECT, SERVER_DIR_DATABASE_CACHE
from src.BusinessLogicLayer.utils.channel_surge.support import sckey_steward


class _AutoUpdater(object):
    function_set = {
        "help": "帮助菜单 返回远程调试权限指令及其简介",
        "upload": "同步actions-entropy采集队列（多机系统仅更新采集器），将本地文件夹数据上传至云",
        "update": "更新actions-entropy采集队列（多机系统仅更新采集器），拉取V2RayCloudSpider任务队列至云",
    }
    debug = True

    def __init__(self, hostname: str, port: int, username: str, password: str):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        # setup work channel
        # self._setup_channel()
        self.client_mode = ''

    # ------------------------------
    # private
    # ------------------------------
    def _setup_channel(self, work_mode='ssh'):
        """该种文件更新方案非常不安全，仅供测试使用，更新系统请将项目封装成镜像后操作"""
        # instantiate
        self.client_mode = work_mode
        try:
            if work_mode == 'ssh':
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.hostname, self.port, self.username, self.password)
            elif work_mode == 'sftp':
                self.tran = paramiko.Transport(self.hostname, self.port)
                self.tran.connect(username=self.username, password=self.password)
                self.sftp = paramiko.SFTPClient.from_transport(self.tran)
            logger.success("<AutoUpdater> | 服务器连接成功！")
        except paramiko.ssh_exception.AuthenticationException:
            logger.error("SSH身份验证异常，请检查键入的信息是否准确，服务器是否异常。")

    def _scan_icon(self, lo_go='qinse'):
        if lo_go not in self.sftp.listdir('/'):
            logger.warning("<AutoUpdate> | 检测到非法运行环境 系统根目录下缺少“/qinse”路径")

    @staticmethod
    def _kill_channel(driver):
        driver.close()
        logger.success("<AutoUpdater> | 登出服务器")

    def _work_upload(self):
        tag_action = 'BusinessLogicLayer/cluster/slavers\\actions.py'
        local_action = os.path.join(SERVER_DIR_PROJECT, tag_action)
        target_action = os.path.join(f"/qinse/V2RaycSpiderDev", tag_action)

        self.debug_printer(msg=f">>> 本机文件地址  {local_action}")
        self.debug_printer(msg=f">>> 服务器推送地址  {target_action}")
        try:
            self.sftp.put(local_action, target_action)
        except FileNotFoundError:
            server_dir = os.path.dirname(target_action)
            logger.error(f"<AutoUpdater> | FileNotFoundError | 目标地址不存在 {server_dir}")

    def _work_update(self):
        pass

    def _work_scaffold(self, trans_command: str):
        pass

    @staticmethod
    def debug_printer(msg):
        if _AutoUpdater.debug:
            logger.debug(msg)

    # ------------------------------
    # public
    # ------------------------------
    @staticmethod
    def function_intro():

        _AutoUpdater.function_set.update(command_set)
        print("基础指令".center(50, "="))
        for i, tag in enumerate(_AutoUpdater.function_set.items()):
            print(f"{i + 1}. {tag[0]} | {tag[-1]}")
        print("".center(50, "="))
        print("TOS:运行环境请与项目技术文档中的保持一致（或改动本脚本代码）")

    def function_exec(self, function_name: str = "help"):

        # ------------------------------
        # TODO 最高优先级指令解析 -- 使用简介
        # ------------------------------
        if "help" in function_name:
            self.function_intro()

        # ------------------------------
        # TODO 远程调试
        # ------------------------------

        # 文件交互
        if function_name in ['upload', 'update']:
            try:
                # 身份验证 连接服务器
                self._setup_channel(work_mode='sftp')

                # 服务器文件扫描
                self._scan_icon(lo_go='qinse')

                # 参数传递
                exec(f"self._work_{function_name}()")

            except Exception as e:
                logger.exception(e)
            finally:
                self._kill_channel(driver=self.sftp)

        # 脚本驱动
        elif function_name in command_set:
            try:
                self._work_scaffold(trans_command=function_name)
            except Exception as e:
                logger.exception(e)
            finally:
                pass


class _Interface(object):

    def __init__(self):
        pass


def _guider_shell_sckey_setting(hostname, port, username, password, cache_path, _sckey=None, mode: str = 'signup'):
    exec("import time\ntime.sleep(1.5)")

    if mode == 'signup':
        usr_ans = input(f">>> 是否需要临时保存服务器敏感数据？相关信息将被加密后存放☞{cache_path}[Y/N]\n")
        if usr_ans[0].upper() == 'N':
            return None
        else:
            stream = f"{hostname}${port}${username}${password}"
            while True:
                if _sckey is None:
                    while True:
                        usr_ans = input(">>>【1】随机生成;\n>>>【2】自定义\n")
                        if usr_ans == '1':
                            _sckey = ''.join([random.choice(printable[:printable.index(' ')]) for _ in range(15)])
                            break
                        elif usr_ans == '2':
                            _sckey = input(">>> 请输入自定义密码:")
                            if input(">>> 确认密码:") == _sckey:
                                break
                        else:
                            continue
                    print(f">>> 您设置的文件密钥是：{_sckey}")
                    print(f">>> 请牢记或保管，请不要在本项目任意处存放_sckey明文！")
                    input(">>> 按任意键退出任务")
                    break
                else:
                    usr_ans = input(f">>> 系统检测到您传入的_sckey:{_sckey} 是否使用？[Y/N]")
                    if usr_ans[0].upper() == 'N':
                        _sckey = None
                        continue
                    break

            return sckey_steward.api(password=_sckey, cache_path=cache_path).encrypt(message=stream)


def _guider_easygui_sckey_setting():
    pass


def _load_server_info_from_cache(_sckey, cache_path):
    stream: str = sckey_steward.api(password=_sckey, cache_path=cache_path).decrypt()
    hostname, port, username, password = stream.split('$')
    port = int(port)
    return hostname, port, username, password


def api(run_steward: bool = True, function_select: str = 'upload'):
    # ----------------------------------------
    # TODO Define local variables
    # ----------------------------------------
    _cache_path = os.path.join(SERVER_DIR_DATABASE_CACHE, '_sckeyStream.v2raycs')
    _sckey = None

    # 找不到密钥文件 视为加密程序初始化
    if not os.path.exists(_cache_path):
        run_steward = False

    # ----------------------------------------
    #  TODO Load sensitive server data
    # ----------------------------------------
    if run_steward is False:
        try:
            hostname = input(">>> 请输入服务器IP：")
            port = int(input(">>> 请输入服务器访问端口Port："))
            username = input(">>> 请输入登录用户名：")
            password = input(">>> 请输入登录密码：")
        # 端口号的输入出现非数字文本
        except ValueError as e:
            print(f">>> 输入错误 请重试! | {e}")
            return False
    else:
        try:
            _sckey = input(">>> 请输入文件密钥SCKEY:")
            hostname, port, username, password = _load_server_info_from_cache(_sckey=_sckey, cache_path=_cache_path)
        # 密码错误
        except AttributeError:
            return api(run_steward=False)
    # ----------------------------------------
    # TODO Core Business
    # ----------------------------------------
    au = _AutoUpdater(hostname=hostname, port=port, username=username, password=password)
    au.function_exec(function_name=function_select)
    # ----------------------------------------
    # TODO Caching of sensitive data
    # ----------------------------------------
    _guider_shell_sckey_setting(hostname, port, username, password, _cache_path, _sckey)


if __name__ == '__main__':
    api(run_steward=True)
