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


def shell_echo(cmd: str):
    response = os.system(shlex.quote(cmd))
    return response


if int(platform.python_version_tuple()[0]) == 2:
    print("---> This project does not support running in the Python2 environment."
          "Please use Python3.6+ to run this  script.")
    sys.exit()
else:
    try:
        import requests
        from bs4 import BeautifulSoup

    except ImportError:
        shell_echo("pip install requests bs4")
        print("---> If something goes wrong, please restart the script.")
        import requests
        from bs4 import BeautifulSoup

SCRIPT_NAME = ""
GITHUB_REPO = "https://github.com/QIN2DIM/V2RayCloudSpider"
PROJECT_NAME = "V2RayCloudSpider"
CHROMEDRIVER_UNZIP_PATH = "src/BusinessCentralLayer/chromedriver"
EXIST_WGET = shell_echo("wget --help >/dev/null") == 0
EXIST_GIT = shell_echo("git --version >/dev/null") == 0
THIS_WALK = "."


def are_you_ready():
    if EXIST_GIT is False:
        shell_echo("sudo yum install git -y")
    if EXIST_WGET is False:
        shell_echo("sudo yum install wget -y")


def this_file_is_empty():
    global SCRIPT_NAME
    for check in os.walk(THIS_WALK):
        if len(check[-1]) == 1 and not check[1]:
            SCRIPT_NAME = check[-1][0]
        else:
            print("---> The current file is not empty")
            sys.exit()


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
    unzip_path = "/usr/bin/chromedriver" if unzip_path is None else unzip_path
    # Such as 89.0.4389.23
    chrome_version = "".join(os.popen("google-chrome --version").readlines()).strip().split(' ')[-1]
    res = requests.get("http://npm.taobao.org/mirrors/chromedriver")
    soup = BeautifulSoup(res.text, 'html.parser')
    options = [i.split('/')[0] for i in soup.text.split('\n') if i.startswith(chrome_version[:5])]
    if len(options) == 1:
        chromedriver_version = options[0]
    else:
        chromedriver_version = max(options)
    shell_echo(f"wget http://npm.taobao.org/mirrors/chromedriver/{chromedriver_version}"
               "/chromedriver_linux64.zip >/dev/null")
    shell_echo("unzip chromedriver_linux64.zip")
    while True:
        if "chromedriver" not in list(os.walk(THIS_WALK))[0][-1]:
            pass
        else:
            break
    shell_echo("chmod +x chromedriver")
    shell_echo(f"mv -f chromedriver {unzip_path}")


def init_project():
    print("---> Remove irrelevant information")
    shell_echo(f"rm -rf {PROJECT_NAME}")
    shell_echo("rm -rf chromedriver_linux64.zip")
    shell_echo("rm -rf google-chrome-stable_current_x86_64.rpm")
    print("---> Project initialization completed")
    shell_echo("clear")

    print("Welcome to use V2RayCloudSpider!")
    shell_echo("python main.py")
    shell_echo("python main.py")
    print(f"---> Please replace the configuration file  {os.path.abspath(THIS_WALK)}/src/config.yaml")
    print(f"---> If you have any questions, please visit the project homepage.See {GITHUB_REPO}")
    print("---> Please press any key to exit.")
    shell_echo("rm -rf {SCRIPT_NAME}")


def run():
    are_you_ready()

    this_file_is_empty()
    pull_project()
    set_google_chrome_on_centos7()
    set_chromedriver(unzip_path=CHROMEDRIVER_UNZIP_PATH)
    init_project()


if __name__ == '__main__':
    run()
