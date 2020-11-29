# FIXME：
#  --该模块在当前版本负责panel的版本管理 -> <检查更新><文件拉取><文件解压><软件更新>
#  --请在版本更新前将该文件中的代码集成到panel中

# TODO：
#  --重写该模块运行逻辑
#  --引入性能更高的桌面前端解决方案
#       (绝了这个模块当前的安装界面是没有进度条的！！)


# 软件安装引导

import os
import shutil
import zipfile

import easygui
import requests
import yaml
from concurrent.futures import ThreadPoolExecutor
from BusinessViewLayer.panel.panel import PrepareEnv
from config import LOCAL_DIR_DATABASE, TITLE, USER_YAML, LOCAL_PATH_DATABASE_YAML

install_title = 'v2ray云彩姬安装向导'

v2raycs_url = 'your_interface'

v2raycs_name = 'v2ray云彩姬.exe'


def get_server_version():
    """
    :return: [version:str, url:str]
    """
    return requests.get(v2raycs_url).text.split('\n')[-1].split(',')


class InstallGuider(object):

    def __init__(self):
        self.open_dir = ''

        self.open_fp = ''

        self.prepare_check()

        self.exe_name = 'v2ray云彩姬.exe'

    @staticmethod
    def prepare_check():
        try:
            requests.get('https://www.baidu.com')
        except requests.exceptions.RequestException:
            easygui.msgbox('网路异常', install_title)
            exit()

    def download(self, ):
        # FILENAME
        res = requests.get(v2raycs_url)
        res.encoding = res.apparent_encoding
        v2raycs = res.text.strip().split(',')[-1]

        self.open_fp = os.path.join(self.open_dir, v2raycs.split('/')[-1])

        res = requests.get(v2raycs)

        with open(self.open_fp, 'wb') as f:
            f.write(res.content)

    def kill_main(self, exe_name: str = None):
        import psutil
        import signal

        if exe_name is None:
            exe_name = self.exe_name

        def get_all_pid():
            pid_dict = {}
            pids = psutil.pids()
            for pid in pids:
                p = psutil.Process(pid)
                pid_dict[pid] = p.name()
                print(f'pid-{pid},pname-{p.name()}')
            return pid_dict

        def kill(pid):
            try:
                os.kill(pid, signal.SIGABRT)
                print("located pid: {}".format(pid))
            except Exception as e:
                print('NoFoundPID || {}'.format(e))

        dic = get_all_pid()
        for t in dic.keys():
            if dic[t] == exe_name:
                kill(t)

    def run(self, use_updated=False):
        try:
            usr_choice = easygui.ynbox('是否执行v2ray云彩姬一键安装脚本？', install_title)
            if usr_choice:
                # 首次安装
                if use_updated is False:
                    PrepareEnv()
                    for x in range(3):
                        self.open_dir = easygui.diropenbox('请选择安装路径', install_title, default=LOCAL_DIR_DATABASE)
                        # 退出-放弃更新
                        if self.open_dir is None:
                            return False
                        # 选择限制
                        if os.listdir(self.open_dir):
                            easygui.msgbox('当前目录下存在其他文件，请选择独立的文件夹！', TITLE)
                        else:
                            # 记录用户选择的下载目录，便于软件更新时的项目文件拉取
                            with open(LOCAL_PATH_DATABASE_YAML, 'w', encoding='utf-8') as f:
                                proj = USER_YAML
                                proj['path'] = self.open_dir
                                yaml.dump(proj, f)
                            break
                    # 给头铁的孩子一点教育
                    else:
                        easygui.msgbox('操作有误，请重试！', TITLE)
                        return False
                # 软件更新
                else:
                    try:
                        self.kill_main()

                        # fixme:将updated模块移植到系统路径，通过外部操作控制软件更新；
                        # TODO: 将self.open_dir赋值为软件所在路径
                        with open(LOCAL_PATH_DATABASE_YAML, 'r', encoding='utf-8') as f:
                            data = yaml.load(f, Loader=yaml.FullLoader)
                            print(data['path'])
                        # self.open_dir = easygui.diropenbox()
                        self.open_dir = data['path']

                    except Exception as e:
                        print(e)

                # 下载线程
                os.startfile(self.open_dir)
                print(f"install path >> {self.open_dir}")
                with ThreadPoolExecutor(max_workers=1) as t:
                    t.submit(self.download)
                    # t.submit(easygui.msgbox, '正在拉取项目文件，请等待下载', install_title)
                easygui.msgbox('下载完成', install_title)

                # 解压线程
                with ThreadPoolExecutor(max_workers=2) as t:
                    t.submit(UnZipManager, self.open_fp)
                    t.submit(easygui.msgbox, '正在解压核心组件，请等待解压', title=install_title)
                easygui.msgbox('解压完成', install_title)

                # 自启动
                target_file = self.open_fp.replace('.zip', '') + f'_v{get_server_version()[0]}'
                try:
                    os.startfile(os.path.join(
                        target_file,
                        v2raycs_name))
                except OSError:
                    pass
                finally:
                    for filename in os.listdir(self.open_dir):
                        if '.zip' in filename:
                            try:
                                os.remove(os.path.join(self.open_dir, filename))
                            except OSError:
                                pass
                        elif os.path.basename(target_file).split('_')[-1] != filename.split('_')[-1]:
                            if os.path.basename(target_file).split('_')[0] in filename:
                                try:
                                    shutil.rmtree(os.path.join(self.open_dir, filename))
                                    os.rmdir(os.path.join(self.open_dir, filename))
                                except OSError:
                                    pass

        except Exception as e:
            easygui.exceptionbox(f'{e}')
        # over
        finally:
            easygui.msgbox('感谢使用', install_title)


class UnZipManager(object):
    def __init__(self, target: list or str):
        if isinstance(target, str):
            target = [target, ]

        for i in target:
            if i.endswith('.zip') and os.path.isfile(i):
                self.unzip(i)

    def unzip(self, filename: str):
        try:
            file = zipfile.ZipFile(filename)
            dirname = filename.replace('.zip', '') + f'_v{get_server_version()[0]}'

            # 创建文件夹，并解压
            os.mkdir(dirname)
            file.extractall(dirname)
            file.close()
            # 递归修复编码
            self.rename(dirname)
            return dirname

        except Exception as e:
            print(f'{filename} unzip fail || {e}')

    def rename(self, pwd: str, filename=''):
        """压缩包内部文件有中文名, 解压后出现乱码，进行恢复"""

        path = f'{pwd}/{filename}'
        if os.path.isdir(path):
            for i in os.scandir(path):
                self.rename(path, i.name)
        newname = filename.encode('cp437').decode('gbk')
        os.rename(path, f'{pwd}/{newname}')


if __name__ == '__main__':
    InstallGuider().run()
