"""
1. 该脚本用于快速拉取项目第三方依赖，运行前请确保环境中存在`脚本依赖`中的指令
2. 该脚本未经其他部署环境测试，请谨慎运行
3. 该脚本未完全消除由指令产生的输入缓存，请勿在生产环境中运行，会出大事

> 使用环境：CentOS7 | Python3.x |
> 脚本依赖：yum | wget | git | pip | unzip
> 拉取资源：google-chrome | chromedriver | GitProject-latest |

"""
import os
import platform
import shlex
import sys

# 版本断言，该脚本应当在 Python3+ 的环境中运行
if int(platform.python_version_tuple()[0]) == 2:
    print("---> This project does not support running in the Python2 environment."
          "Please use Python3.6+ to run this  script.")
    sys.exit()
# 导入第三方包，若当前环境足够干净，则自动拉取
try:
    import requests
    from bs4 import BeautifulSoup

except ImportError:
    os.system(shlex.quote("pip install requests bs4"))
    print("---> If something goes wrong, please restart the script.")
    import requests
    from bs4 import BeautifulSoup

GITHUB_REPO = "https://github.com/QIN2DIM/V2RayCloudSpider"
PROJECT_NAME = "V2RayCloudSpider"
CHROMEDRIVER_UNZIP_PATH = "src/BusinessCentralLayer/chromedriver"
THIS_WALK = "."


def shell_echo(cmd: str, mode="default"):
    """
    为了输出安全做的协调函数
    :param cmd:
    :param mode:
    :return:
    """
    if mode == "default":
        return os.system(cmd)
    if mode == "safe":
        return os.system(shlex.quote(cmd))


def are_you_ready():
    """
    测试当前环境是否预装 wget git 核心依赖，若未安装则依靠 yum 运行安装指令
    :return:
    """
    exist_wget = shell_echo("wget --help >/dev/null") == 0
    exist_git = shell_echo("git --version >/dev/null") == 0

    if exist_git is False:
        shell_echo("sudo yum install git -y")
    if exist_wget is False:
        shell_echo("sudo yum install wget -y")


def this_file_is_empty() -> str:
    # 递归遍历脚本所在目录
    for check in os.walk(THIS_WALK):
        # 脚本所在根目录下，应仅有脚本一个文件，且无其他子文件夹存在
        # 也即该脚本文件应是目录下的唯一文件
        if not (len(check[-1]) == 1 and not check[1]):
            print("---> The current file is not empty")
            sys.exit()
        return check[-1][0]


def pull_project():
    print("---> Pulling Github project files")
    res = shell_echo("git clone -q --single-branch {}.git".format(GITHUB_REPO))

    if res == 0:
        print("---> kernel_downloaded_successfully")
        src_dir = [node[0] for node in os.walk(THIS_WALK) if
                   node[0].startswith("./{}/V2RaycSpider".format(PROJECT_NAME)) and 'src' in node[1]][0]

        print("---> Mobile_core_project_source_code")
        shell_echo(f"cp -r {src_dir}/* ./")

        print("---> Github project file is successfully pulled")
    else:
        print("---> Github project file pull failed")
        sys.exit()


def set_google_chrome_on_centos7():
    # Google-chrome already exists in the current environment
    if shell_echo("google-chrome --version") == 0:
        # uninstall command
        # os.system("sudo rpm -e google-chrome-stable")
        return True

    # installing Google Chrome on CentOS7
    shell_echo("wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm")
    shell_echo("sudo yum localinstall google-chrome-stable_current_x86_64.rpm")


def set_chromedriver(unzip_path=None):
    # chromedriver 的解压安装目录
    unzip_path = "/usr/bin/chromedriver" if unzip_path is None else unzip_path

    # 读取 google-chrome 的发行版本 Such as 89.0.4389.23
    chrome_version = "".join(os.popen("google-chrome --version").readlines()).strip().split(' ')[-1]

    # 访问 chromedriver 镜像
    res = requests.get("http://npm.taobao.org/mirrors/chromedriver")
    soup = BeautifulSoup(res.text, 'html.parser')

    # 通过文件名清洗定位到所需版本文件的下载地址
    options = [i.split('/')[0] for i in soup.text.split('\n') if i.startswith(chrome_version[:5])]
    if len(options) == 1:
        chromedriver_version = options[0]
    else:
        chromedriver_version = max(options)

    # 拉取 chromedriver
    shell_echo(f"wget http://npm.taobao.org/mirrors/chromedriver/{chromedriver_version}"
               "/chromedriver_linux64.zip >/dev/null")

    # 解压 chromedriver
    shell_echo("unzip chromedriver_linux64.zip")

    # 死循环等待解压完成
    while True:
        if "chromedriver" not in list(os.walk(THIS_WALK))[0][-1]:
            pass
        else:
            break

    # 给予 chromedriver 运行运行权限
    shell_echo("chmod +x chromedriver")

    # 将 chromedriver 移动到预设的解压安装目录
    shell_echo(f"mv -f chromedriver {unzip_path}")


def init_project(script_name: str):
    print("---> Remove irrelevant information")
    shell_echo(f"rm -rf {PROJECT_NAME}")
    shell_echo("rm -rf chromedriver_linux64.zip")
    shell_echo("rm -rf google-chrome-stable_current_x86_64.rpm")

    print("---> Project initialization completed")
    shell_echo("clear")

    print("Welcome to use V2RayCloudSpider!")
    shell_echo("python main.py")

    print(f"---> Please replace the configuration file  {os.path.abspath(THIS_WALK)}/src/config.yaml")
    print(f"---> If you have any questions, please visit the project homepage.See {GITHUB_REPO}")
    print("---> Please press any key to exit.")
    shell_echo(f"rm -rf {script_name}")


def run():
    # 检测脚本运行依赖 wget git
    are_you_ready()

    # 检测脚本是否运行在空目录下
    script_name = this_file_is_empty()

    # 拉取 GitHub Repository 源代码并自动调整目录结构
    pull_project()

    # 为 CentOS7 适配 google-chrome
    set_google_chrome_on_centos7()

    # 拉取对应 google-chrome 版本的 linux chromedriver 到项目运行路径下
    set_chromedriver(unzip_path=CHROMEDRIVER_UNZIP_PATH)

    # 清理运行缓存
    init_project(script_name)


if __name__ == '__main__':
    run()
