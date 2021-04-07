# coding=utf-8
import os
import sys
import platform
import time
from threading import Thread

# Python版本 简要区分2.x 及3.X
PY_VERSION = 3
# Linux发行版本 简要区分主流CentOS以及Ubuntu
LINUX_KERNEL = ""
COMMAND_HEADER = ""
# 工程根目录
PROJECT_ROOT = "/qinse"
# 运行模式
DEBUG = True
# PIP 源
PIP_SOURCE = "-i https://pypi.tuna.tsinghua.edu.cn/simple"
GIT_RPO = "https://github.com/QIN2DIM/V2RayCloudSpider"
# 指令集参数
IS_NEW_SYSTEM = False
UPGRADE_LATEST_PIP = False
UPGRADE_REQUIREMENTS = False

"""==================================辅助脚本=================================="""


def input_checker():
    try:
        if PY_VERSION == 2:
            usr_choice_ = raw_input(echo_content(">>> 请选择："))
        else:
            usr_choice_ = input(echo_content(">>> 请选择："))

        if usr_choice_ == '':
            raise ValueError
        else:
            return usr_choice_
    except KeyboardInterrupt:
        print(echo_content("\r---> 脚本退出"))
        exit()


# 文本修饰器
def echo_content(text, text_color='white'):
    """
    https://www.cnblogs.com/easypython/p/9084426.html
    :param text: 要装饰的文本
    :param text_color: 颜色模式，前景色，可选参数 见 set_text_color()
    :return:
    """

    def set_text_color():
        """
        设置字体颜色,也叫前景色
        前景色         背景色              颜色
        ---------------------------------------
        30                40              黑色
        31                41              红色
        32                42              绿色
        33                43              黃色
        34                44              蓝色
        35                45              洋红
        36                46              青色
        37                47              白色
        :return:
        """
        if text_color == 'bk' or text_color == 'black':
            return '30'
        elif text_color == 'r' or text_color == 'red':
            return '31'
        elif text_color == 'g' or text_color == 'green':
            return '32'
        elif text_color == 'y' or text_color == 'yellow':
            return '33'
        elif text_color == 'bl' or text_color == 'blue':
            return '34'
        elif text_color == 'm' or text_color == 'magenta':
            return '35'
        elif text_color == 'c' or text_color == 'cyan ':
            return '36'
        elif text_color == 'w' or text_color == 'white':
            return '37'
        else:
            return '37'

    return "\033[{}m{}\033[0m".format(set_text_color(), text)


def _clear(sleep=0):
    if sleep > 0:
        time.sleep(sleep)
    if platform.system() == "Linux":
        os.system("clear")
    elif platform.system() == 'Windows':
        os.system("cls")


def _screen_clear(func):
    def wrapper(*args, **kwargs):
        _clear()
        func(*args, **kwargs)
        _clear()

    return wrapper


def pull_linux(func):
    def wrapper(*args, **kwargs):
        if LINUX_KERNEL != "":
            func(*args, **kwargs)

    return wrapper


class JobManager(object):

    def __init__(self):
        super(JobManager, self).__init__()
        self.job_queue = []

    def add_job(self, func, **kwargs):
        job = Thread(target=func, kwargs=kwargs)
        job.start()
        self.job_queue.append(job)

    def release_job(self):
        while self.job_queue.__len__() > 0:
            job = self.job_queue.pop()
            job.join()


"""==================================TB工具箱=================================="""


class ToolBoxInstaller(object):
    """
    > 目录创建
    > 项目依赖拉取
    1. 系统级依赖拉取（yum/apt,kernel,gcc,）
    2. python生态搭建（pyenv/py3，requirements，pip）
    3. 第三方依赖拉取（tmux,wget,git,）
    """

    def __init__(self):

        self.project_dir_root = PROJECT_ROOT
        self.project_dir_redis = os.path.join(self.project_dir_root, "redis")
        self.project_path_installer = os.path.join(self.project_dir_root, os.path.basename(__file__))
        # 依赖清单<相互独立>
        self.req_kernel = ["gcc", "tmux", "git", "wget", "curl"]
        self.multi_task = []

        self.jm = JobManager()

    def startup(self):
        """
        :return:
        """
        # =======================================
        # 初始化工程目录
        # =======================================
        self._create_project_root()
        # =======================================
        # 拉取最新版项目代码
        # =======================================
        self._git_clone_latest_src()
        # =======================================
        # 拉取或升级必要的系统/第三方依赖
        # ---> 组内并发 部分任务相互独立
        # =======================================
        self._create_env_kernel()
        self._create_env_py3()
        self._create_env_third_party()
        # =======================================
        # 清空任务队列
        # =======================================
        self.jm.release_job()
        return self.response_()

    @staticmethod
    def response_():
        input(echo_content(">>>安装完毕 按任意键继续"))
        _clear(1)
        return True

    @pull_linux
    # @_screen_clear
    def _create_project_root(self):
        # =======================================
        # 检查目录完整性
        # =======================================
        print(echo_content("---> 检查目录完整性", "green"))
        # 深度创建，不可颠倒
        for dir_name in [
            self.project_dir_root,
            self.project_dir_redis
        ]:
            if not os.path.exists(dir_name):
                print(echo_content("---> [create] {}".format(dir_name)))
                os.mkdir(dir_name)
        # =======================================
        # 移动installer
        # =======================================
        # print(echo_content("---> [create] {}".format(self.project_path_installer)))
        if not os.path.exists(self.project_path_installer):
            os.system("mv -f {} {} >/dev/null".format(os.path.abspath(__file__), self.project_path_installer))
        else:
            os.system("mv -u {} {} >/dev/null".format(os.path.abspath(__file__), self.project_path_installer))
        # =======================================
        # 创建软连接
        # =======================================
        print(echo_content("---> 创建软链接: v2raycs", "green"))
        # os.symlink("/usr/bin/v2raycs", self.project_path_installer)
        os.system("ln -s {} /usr/bin/v2raycs >/dev/null | "
                  "chmod +x /usr/bin/v2raycs".format(self.project_path_installer))

    @pull_linux
    def _create_env_kernel(self):
        # =======================================
        # 初始化时更新系统
        # =======================================
        if IS_NEW_SYSTEM:
            print(echo_content("---> 更新系统", "green"))
            os.system("sudo {} update -y".format(COMMAND_HEADER))
            os.system("sudo {} update {} -y".format(COMMAND_HEADER, COMMAND_HEADER))
            _clear(sleep=1)

        # =======================================
        # 拉取项目依赖
        # =======================================
        print(echo_content("---> 拉取项目依赖 {}".format(self.req_kernel), "green"))
        for pointer in self.req_kernel:
            if os.system("sudo {} list installed | grep {} >/dev/null".format(COMMAND_HEADER, pointer)) != 0:
                self.jm.add_job(
                    func=os.system,
                    command="sudo {} install {} -y ".format(COMMAND_HEADER, pointer)
                )

    @staticmethod
    def _create_env_py3():

        def installer_py3():
            print(echo_content("---> 创建Python3编程环境", "green"))

        def update_latest_pip():
            """

            :return:
            """
            print(echo_content("---> 拉取并安装最新版pip", "green"))
            if UPGRADE_LATEST_PIP is True:
                os.system("pip install --upgrade pip >/dev/null")

        def installer_requirements():
            print(echo_content("---> 拉取并升级py3-requirements", "green"))
            for i in os.walk(os.path.abspath(".")):
                if "requirements.txt" in i[-1]:
                    os.system(
                        "pip install -r {} {} >/dev/null".format(os.path.join(i[0], "requirements.txt"), PIP_SOURCE))
                    return True
            else:
                print(echo_content("---> py3-requirements拉取失败，未在规定目录下找到requirements.txt依赖文档", "red"))

        installer_py3()
        update_latest_pip()
        installer_requirements()

    def _create_env_third_party(self):
        def installer_redis():
            print(echo_content("---> 安装redis", "green"))
            if LINUX_KERNEL == "ubuntu":
                pass
            elif LINUX_KERNEL == "centos":
                # 01.Start by enabling the Remi repository by running the following commands in your SSH terminal:
                os.system("sudo yum install epel-release yum-utils -y -q >/dev/null")
                os.system("sudo yum install http://rpms.remirepo.net/enterprise/remi-release-7.rpm -y -q >/dev/null")
                os.system("sudo yum-config-manager --enable remi -y -q >/dev/null")
                # 02.Install the Redis package by typing:
                os.system("sudo yum install redis -y -q >/dev/null")
                # 03.Once the installation is completed, start the Redis service and enable it to start automatically on boot with:
                os.system("sudo systemctl start redis >/dev/null")
                os.system("sudo systemctl enable redis >/dev/null")
                # TODO 04. Modify the configuration file

        def installer_chromedriver():
            print(echo_content("---> 安装chromedriver", "green"))

            os.system("wget http://npm.taobao.org/mirrors/chromedriver/2.41/chromedriver_linux64.zip >/dev/null")
            os.system("unzip chromedriver_linux64.zip -d /usr/bin/chromedriver -y >/dev/null")
            os.system("chmod +x /usr/bin/chromedriver")

        def installer_google_chrome():
            print(echo_content("---> 安装google-chrome-stable", "green"))
            # FIXME Need to test code
            if LINUX_KERNEL == "ubuntu":
                os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
                os.system("sudo dpkg -i google-chrome-stable_current_amd64.deb")
                os.system("sudo apt -f install")
            # FIXME Need to test code
            elif LINUX_KERNEL == "centos":
                os.system("wget -O /etc/yum.repos.d/CentOS-Base.repo "
                          "http://mirrors.aliyun.com/repo/Centos-7.repo >/dev/null")
                os.system("{} install mesa-libOSMesa-devel gnu-free-sans-fonts"
                          " wqy-zenhei-fonts >/dev/null".format(COMMAND_HEADER))
                os.system("curl https://intoli.com/install-google-chrome.sh | bash >/dev/null")
            time.sleep(1)

        self.jm.add_job(func=installer_redis)
        self.jm.add_job(func=installer_google_chrome)
        self.jm.add_job(func=installer_chromedriver)

    def _git_clone_latest_src(self):
        """
        在安装最新版git、创建工程根之后才能调用此模块拉取项目文件
        :return:
        """
        # 若“当前目录”已存在同名文件且不为空，则不会进行拉取操作
        print(echo_content("---> 拉取Github项目文件", "green"))
        self.jm.add_job(
            func=os.system,
            command="git clone -q --single-branch {}.git >/dev/null".format(GIT_RPO)
        )


class ToolBoxMaintain(object):
    def __init__(self):
        pass

    @staticmethod
    def _core_func_deploy():
        return None

    @staticmethod
    def _vcs_is_old():
        """

        :return:
        """
        return None

    @staticmethod
    def vcs_update_kernel():
        print(echo_content("---> 拉取Github项目文件", "green"))
        if os.system("git clone -q --single-branch {}.git".format(GIT_RPO)) == 0:
            print(echo_content("---> kernel下载成功", "green"))
        else:
            print(echo_content("---> 更新Kernel", "green"))
            os.system("cd V2RayCloudSpider && git fetch")
            time.sleep(1)
            print(echo_content("---> Kernel更新成功", "green"))
        return True

    @staticmethod
    def vcs_update_task_queue():
        return None

    @staticmethod
    def vcs_update_script():
        return None

    @staticmethod
    def script_manager_view_log():
        return None

    @staticmethod
    def script_manager_uninstall():
        """
        清空本地运行日志，定位源码文件，删除源码文件，清除链接
        :return:
        """
        return None


class ToolBoxScaffold(object):
    def __init__(self):
        self.path_scaffold = ""

    def locate_scaffold(self):
        interface_ = ""
        for i in os.walk(os.path.abspath(".")):
            # 检索入口函数
            if "main.py" in i[-1]:
                interface_ = os.path.join(i[0], "main.py")
            # 存在scaffold文件
            if "BusinessCentralLayer" in i[0] and "scaffold.py" in i[-1]:
                self.path_scaffold = interface_
                return True
        else:
            print(echo_content("---> 未在当前工程目录下找到scaffold调试工具", "red"))
            print(echo_content("---> 请拉取/更新项目源码，或访问Github项目仓库 >{}/issues".format(GIT_RPO)))

    def transfer(self, *args):
        # 脚手架仅兼容py3
        os.system("python {} {}".format(self.path_scaffold, " ".join(args)))


"""==================================菜单交互=================================="""
README = "{}\n{}\n{}".format(
    echo_content("作者：A-RAI.DM", "green"),
    echo_content("当前版本：v0.1.1", "green"),
    echo_content("Github：https://github.com/QIN2DIM/V2RayCldouSpider", "green")
)


class InterfaceMenu(object):
    def __init__(self):
        self.maintain = ToolBoxMaintain()
        self.scaffold = ToolBoxScaffold()
        self.installer = ToolBoxInstaller()

    def _submenu_scaffold_func_launcher(self):
        pass

    def _submenu_scaffold_transfer(self):
        _clear()
        # ===================================================
        # Top frame
        # ===================================================
        print(echo_content("".center(62, "="), "red"))
        print(README)
        print(echo_content("描述：V2Ray云彩姬scaffold接口调试工具", "green"))
        print(echo_content("".center(62, "="), "red"))
        # ===================================================
        # tools
        # ===================================================
        # print(echo_content("系统管理".center(58, "="), "cyan"))
        print(echo_content("1.一键还原config.yaml[单机配置]", "yellow"))
        print(echo_content("2.测试数据库连接", "yellow"))

        print(echo_content("订阅管理".center(58, "="), "cyan"))
        print(echo_content("3.查看Redis剩余订阅", "yellow"))
        print(echo_content("4.清洗Redis过期|失效订阅", "yellow"))

        print(echo_content("任务管理".center(58, "="), "cyan"))
        print(echo_content("5.使用当前配置启动一次采集任务", "yellow"))
        print(echo_content("6.单步采集指定机场订阅", "yellow"))

        # ===================================================
        # Capture user input
        # ===================================================
        print(echo_content("".center(62, "="), "red"))
        if not self.scaffold.locate_scaffold():
            return

        # 使用试错方案兼容2x与3x特性
        try:
            usr_choice = int(input_checker())
            # TODO 1.一键还原config.yaml[单机配置]
            if usr_choice == 1:
                pass
            elif usr_choice == 2:
                self.scaffold.transfer("ping")
            elif usr_choice == 3:
                self.scaffold.transfer("remain")
            elif usr_choice == 4:
                self.scaffold.transfer("overdue", "decouple")
                _clear(sleep=1)
            elif usr_choice == 5:
                self.scaffold.transfer("force_run")
            elif usr_choice == 6:
                self.scaffold.transfer("launcher")
            else:
                raise ValueError
        except ValueError:
            print(echo_content("---> 选择错误", "red"))

    def home(self):
        # ===================================================
        # Top frame
        # ===================================================
        print(echo_content("".center(62, "="), "red"))

        # README
        print(README)
        print(echo_content("描述：V2Ray云彩姬一步到胃单机部署脚本", "green"))

        # FIXME Component status
        print(echo_content("程序状态：{}", "yellow"))
        print(echo_content("已安装组件：{}", "yellow"))

        print(echo_content("".center(62, "="), "red"))
        # ===================================================
        # Core functions
        # ===================================================
        print(echo_content("1.一键部署[单机]", "yellow"))
        # print (echo_content("-.其他方案部署", "yellow"))

        # ===================================================
        # Toolbox
        # ===================================================
        print(echo_content("工具管理".center(58, "="), "cyan"))

        print(echo_content("2.scaffold调试程序", "yellow"))

        # ===================================================
        # Version management
        # ===================================================
        print(echo_content("版本管理".center(58, "="), "cyan"))

        print(echo_content("3.更新kernel源码", "yellow"))
        print(echo_content("4.更新采集队列", "yellow"))
        print(echo_content("5.更新脚本", "yellow"))
        # ===================================================
        # Script management
        # ===================================================
        print(echo_content("脚本管理".center(58, "="), "cyan"))

        print(echo_content("6.查看日志", "yellow"))
        print(echo_content("7.卸载脚本", "yellow"))

        # ===================================================
        # Capture user input
        # ===================================================
        print(echo_content("".center(62, "="), "red"))

        # 使用试错方案兼容2x与3x特性
        show_menu = False
        try:
            usr_choice = int(input_checker())
            if usr_choice == 1:
                show_menu = self.installer.startup()
            elif usr_choice == 2:
                return self._submenu_scaffold_transfer()
            elif usr_choice == 3:
                show_menu = self.maintain.vcs_update_kernel()
            elif usr_choice == 4:
                return self.maintain.vcs_update_task_queue()
            elif usr_choice == 5:
                return self.maintain.vcs_update_script()
            elif usr_choice == 6:
                return self.maintain.script_manager_view_log()
            elif usr_choice == 7:
                return self.maintain.script_manager_uninstall()
            else:
                raise ValueError
        except ValueError:
            print(echo_content("---> 选择错误", "red"))
        finally:
            if show_menu:
                self.home()


"""==================================程序接口=================================="""


class InterfaceGlobal(object):
    def __init__(self):
        self.menu = InterfaceMenu()

    def startup(self, params):
        global IS_NEW_SYSTEM, UPGRADE_LATEST_PIP, UPGRADE_REQUIREMENTS, \
            PY_VERSION, LINUX_KERNEL, COMMAND_HEADER, DEBUG

        # =============================================
        # 指令解析
        # =============================================
        # 创建系统 首次拉取项目时必须加上此参数
        if "--create" in params:
            IS_NEW_SYSTEM = True
            UPGRADE_LATEST_PIP = True
            UPGRADE_REQUIREMENTS = True
        # todo  This is a hurdle I can't cross in my heart
        if "--debug" not in params:
            DEBUG = False
        # =============================================
        # 参数初始化
        # =============================================
        # 标记运行环境版本
        PY_VERSION = int(platform.python_version_tuple()[0])
        # 简要区分两类主流发行版本
        if platform.system() == "Linux":
            LINUX_KERNEL = "centos" if os.system("yum -help") == 0 else "ubuntu"
            COMMAND_HEADER = "yum" if LINUX_KERNEL == 'centos' else "apt"
            os.system("clear")
        # 若非调试模式，则阻止非Linux操作系统用户的进一步操作
        elif not DEBUG:
            print(echo_content("[注意] 该脚本仅服务于LINUX操作系统！", "red"))
            time.sleep(1)
            exit()
        # =============================================
        # 参数传递 程序启动
        # =============================================
        # 启动交互主菜单
        self.menu.home()


if __name__ == '__main__':
    InterfaceGlobal().startup(sys.argv)
