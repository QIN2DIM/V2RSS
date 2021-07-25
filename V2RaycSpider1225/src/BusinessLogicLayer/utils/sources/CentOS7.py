import os
import platform

if int(platform.python_version_tuple()[0]) == 2:
    print("---> This project does not support running in the Python2 environment."
          "Please use Python3.6+ to run this  script.")
    exit()
else:
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        os.system("pip install requests bs4")
        print("---> If something goes wrong, please restart the script.")
        import requests
        from bs4 import BeautifulSoup

SCRIPT_NAME = ""
GITHUB_REPO = "https://github.com/QIN2DIM/V2RayCloudSpider"
PROJECT_NAME = "V2RayCloudSpider"
CHROMEDRIVER_UNZIP_PATH = "src/BusinessCentralLayer/chromedriver"
EXIST_WGET = True if os.system("wget --help >/dev/null") == 0 else False
EXIST_GIT = True if os.system("git --version >/dev/null") == 0 else False
THIS_WALK = "."


def are_you_ready():
    if EXIST_GIT is False:
        os.system("sudo yum install git -y")
    if EXIST_WGET is False:
        os.system("sudo yum install wget -y")


def this_file_is_empty():
    global SCRIPT_NAME
    for check in os.walk(THIS_WALK):
        if len(check[-1]) == 1 and not check[1]:
            SCRIPT_NAME = check[-1][0]
        else:
            print("---> The current file is not empty")
            exit()


def pull_project():
    print("---> Pulling Github project files")
    res = os.system("git clone -q --single-branch {}.git".format(GITHUB_REPO))
    if res == 0:
        print("---> kernel_downloaded_successfully")
        src_dir = [node[0] for node in os.walk(THIS_WALK) if
                   node[0].startswith("./{}/V2RaycSpider".format(PROJECT_NAME)) and 'src' in node[1]][0]
        print("---> Mobile_core_project_source_code")
        os.system(f"cp -r {src_dir}/* ./")
        print("---> Github project file is successfully pulled")

    else:
        print("---> Github project file pull failed")
        exit()


def set_google_chrome_on_centos7():
    # Google-chrome already exists in the current environment
    if os.system("google-chrome --version") == 0:
        # uninstall command
        # os.system("sudo rpm -e google-chrome-stable")
        return True

    # installing Google Chrome on CentOS7
    os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm")
    os.system("sudo yum localinstall google-chrome-stable_current_x86_64.rpm")


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
    os.system(f"wget http://npm.taobao.org/mirrors/chromedriver/{chromedriver_version}"
              f"/chromedriver_linux64.zip >/dev/null")
    os.system(f"unzip chromedriver_linux64.zip")
    while True:
        if "chromedriver" not in [i for i in os.walk(THIS_WALK)][0][-1]:
            pass
        else:
            break
    os.system(f"chmod +x chromedriver")
    os.system(f"mv -f chromedriver {unzip_path}")


def init_project():
    print("---> Remove irrelevant information")
    os.system(f"rm -rf {PROJECT_NAME}")
    os.system("rm -rf chromedriver_linux64.zip")
    os.system(f"rm -rf google-chrome-stable_current_x86_64.rpm")
    print("---> Project initialization completed")
    os.system("clear")

    print("Welcome to use V2RayCloudSpider!")
    os.system('python main.py')
    os.system('python main.py')
    print(f"---> Please replace the configuration file  {os.path.abspath(THIS_WALK)}/src/config.yaml")
    print(f"---> If you have any questions, please visit the project homepage.See {GITHUB_REPO}")
    print("---> Please press any key to exit.")
    os.system(f"rm -rf {SCRIPT_NAME}")


def run():
    are_you_ready()

    this_file_is_empty()
    pull_project()
    set_google_chrome_on_centos7()
    set_chromedriver(unzip_path=CHROMEDRIVER_UNZIP_PATH)
    init_project()


if __name__ == '__main__':
    run()
