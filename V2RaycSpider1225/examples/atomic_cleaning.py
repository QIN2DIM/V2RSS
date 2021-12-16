"""
> SSPanel Services 二级清洗，导出无限制注册的服务提供商注册链接。
> 运行需求如下：
    - 本地代理，流量过墙
    - 包依赖 `1.25.7 <= urllib3 <= 1.25.11` 否则普通的流量请求会引发 SSLError，
    若版本不匹配，可以使用 `pip install urllib3==1.25.11` 重新安装指定版本的依赖
"""
from gevent import monkey

monkey.patch_all()
import os.path
import sys
from datetime import datetime, timedelta

import urllib.request
import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests.exceptions import SSLError, HTTPError, Timeout, ProxyError, ConnectionError

from BusinessLogicLayer.plugins.accelerator.core import CoroutineSpeedup, Queue
from BusinessCentralLayer.setting import SERVER_DIR_DATABASE_CACHE

# 原始链接数据集路径
PATH_DATASET = os.path.join(
    SERVER_DIR_DATABASE_CACHE,
    "sspanel_mining_dataset_{}.txt".format(str(datetime.now()).split(" ")[0])
)
# 规则清洗后导出的数据集路径
PATH_OUTPUT = os.path.join(
    SERVER_DIR_DATABASE_CACHE,
    "sspanel_mining_output_{}.txt".format(str(datetime.now()).split(" ")[0])
)


class SpawnUnitGuider(CoroutineSpeedup):
    def __init__(self, task_docker: list = None):
        super(SpawnUnitGuider, self).__init__(task_docker=task_docker)
        self.local_proxy = urllib.request.getproxies()
        logger.debug("本机代理状态 PROXY={}".format(self.local_proxy))

        self.done = Queue()

    @logger.catch()
    def control_driver(self, url: str):
        # 剔除 http 站点
        if not url.startswith("https://"):
            logger.warning(f"异常通信 - url={url}")
            return False

        try:
            session = requests.session()
            response = session.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            # 剔除异常状态码站点
            if response.status_code > 400:
                logger.error(f"站点异常 - url={url} status_code={response.status_code} ")
                return False

            # 剔除关闭注册以及必须使用邀请码注册的站点
            if "closed" in soup.text or "邀请码" in soup.text or "停止" in soup.text:
                logger.warning(f"拒绝注册 - url={url} status_code={response.status_code}")
                return False

            # 剔除限定注册邮箱后缀的站点
            if soup.find("select") and soup.find(id="email_verify"):
                logger.warning(f"限制注册 - url={url} status_code={response.status_code}")
                return False

            # 标注正常站点
            self.done.put_nowait(url)
            logger.success("实例正常 - "
                           f"url={url} "
                           f"status_code={response.status_code} "
                           f"progress=[{self.max_queue_size - self.work_q.qsize()}/{self.max_queue_size}]")
            return True
        # 站点被动行为，流量无法过墙
        except ConnectionError:
            logger.error(f"流量阻断 - url={url}")
            return False
        # 站点主动行为，拒绝国内IP访问
        except (SSLError, HTTPError, ProxyError):
            logger.warning(f"代理异常 - url={url}")
            return False
        # 站点负载紊乱或主要服务器已瘫痪
        except Timeout:
            logger.error(f"响应超时 - url={url}")
            return False


def load_dataset(batch: int = 1) -> list:
    """
    sspanel-预处理数据集
    访问 https://github.com/RobAI-Lab/sspanel-mining/tree/main/database/staff_hosts
    :param batch: 获取过去X天的历史数据
    :return:
    """

    # 初始化数据集
    if not os.path.exists(PATH_DATASET):
        url_ = "https://raw.githubusercontent.com/RobAI-Lab/sspanel-mining/main/database/" \
               "staff_hosts/staff_host_{}.txt"
        today_ = datetime.now()
        try:
            # 获取过去X天的历史数据
            for _ in range(batch):
                today_ -= timedelta(days=1)
                focus_ = url_.format(str(today_).split(" ")[0])

                logger.info(f"正在下载数据集 {focus_}")
                res = requests.get(focus_)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    with open(PATH_DATASET, "a", encoding="utf8") as f:
                        f.write(soup.text)
            logger.success("数据集下载完毕 - path={}".format(PATH_DATASET))
        except requests.exceptions.RequestException:
            logger.error("数据集下载失败，可以手动今日获取数据集 - "
                         f"repo=https://github.com/RobAI-Lab/sspanel-mining/tree/main/database/staff_hosts")
            return []
    # 读回数据集
    with open(PATH_DATASET, "r", encoding="utf8") as f:
        urls = {i for i in f.read().split('\n') if i}

    # 返回参数
    return list(urls)


def demo():
    # 导入数据集
    urls = load_dataset(batch=1)

    # 链接清洗
    sug = SpawnUnitGuider(task_docker=urls)
    sug.interface(power=max(os.cpu_count(), 2))

    # 数据导出导出
    with open(PATH_OUTPUT, "w", encoding="utf8") as f:
        while not sug.done.empty():
            url = sug.done.get()
            f.write(f"{url}\n")

    # Windows 系统下自动打开洗好的导出文件，否则控制台提示文件路径
    if "win" in sys.platform:
        os.startfile(PATH_OUTPUT)
    else:
        logger.success("清洗完毕 - path={}".format(PATH_OUTPUT))


if __name__ == '__main__':
    demo()
