# -*- coding: utf-8 -*-
# Time       : 2021/12/18 19:29
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import csv
import os.path
import random
import sys
from datetime import datetime
from datetime import timedelta

import requests
from bs4 import BeautifulSoup

from services.settings import TIME_ZONE_CN, logger, DIR_CACHE_CLASSIFY, DIR_CACHE_MINING
from services.utils import SSPanelHostsClassifier, SSPanelHostsCollector

__all__ = ["run_collector", "run_classifier"]

# Collector 数据集路径
_FOCUS_SUFFIX = ".txt"
_FOCUS_PREFIX = "dataset"
# 路径模版
PATH_DATASET_TEMPLATE = os.path.join(
    DIR_CACHE_MINING, _FOCUS_PREFIX + "_{}" + _FOCUS_SUFFIX
)


def create_env(path_file_txt: str) -> bool:
    """
    初始化运行环境

    :param path_file_txt: such as `dataset_2022-01-1.txt`
    :return:
    """
    # 若文件不存在或仅存在空白文件时返回 True
    # 若文件不存在，初始化文件
    if not os.path.exists(path_file_txt):
        with open(path_file_txt, "w", encoding="utf8"):
            pass
        return True

    # 若文件存在但为空仍返回 True
    with open(path_file_txt, "r", encoding="utf8") as f:
        return False if f.read() else True


def data_cleaning(path_file_txt: str):
    """
    链接去重

    :param path_file_txt: such as `dataset_2022-01-1.txt`
    :return:
    """

    with open(path_file_txt, "r", encoding="utf8") as f:
        data = {i for i in f.read().split("\n") if i}
    with open(path_file_txt, "w", encoding="utf8") as f:
        for i in data:
            f.write(f"{i}\n")


def load_sspanel_hosts() -> list:
    """
    sspanel-预处理数据集 获取过去X天的历史数据

    :return:
    """
    # 待分类链接
    urls = []

    # 识别并读回 Collector 输出
    for t in os.listdir(DIR_CACHE_MINING):
        if t.endswith(_FOCUS_SUFFIX) and t.startswith(_FOCUS_PREFIX):
            # 补全路径模版
            path_file_txt = os.path.join(DIR_CACHE_MINING, t)
            # 读回 Collector 输出
            with open(path_file_txt, "r", encoding="utf8") as f:
                for url in f.read().split("\n"):
                    urls.append(url)

    # 清洗杂质
    urls = {i for i in urls if i}

    # 返回参数
    return list(urls)


def load_sspanel_hosts_remote(batch: int = 1):
    """
    sspanel-预处理数据集
    访问 https://github.com/RobAI-Lab/sspanel-mining/tree/main/database/staff_hosts
    :param batch: 获取过去X天的历史数据
    :return:
    """

    # 初始化数据集
    url_ = (
        "https://raw.githubusercontent.com/RobAI-Lab/sspanel-mining/main/src/database"
        "/sspanel_hosts/dataset_{}.txt"
    )
    urls = []
    today_ = datetime.now()

    # 获取过去X天的历史数据
    for _ in range(batch):
        today_ -= timedelta(days=1)
        focus_ = url_.format(str(today_).split(" ")[0])
        res = requests.get(focus_)
        if res.status_code == 200:
            logger.info(f"正在下载数据集 {focus_}")
            soup = BeautifulSoup(res.text, "html.parser")
            urls += soup.text.split("\n")

    # 返回参数
    return list(set(urls))


def output_cleaning_dataset(
    dir_output: str, docker: list, path_output: str = None
) -> str:
    """
    输出分类/清洗结果

    :param dir_output:
    :param docker:
    :param path_output:
    :return:
    """
    if not docker:
        return ""

    # 规则清洗后导出的数据集路径
    path_output_template = os.path.join(
        DIR_CACHE_CLASSIFY,
        "mining_{}".format(
            str(datetime.now(TIME_ZONE_CN)).split(".")[0].replace(":", "-")
        ),
    )
    path_output_ = f"{path_output_template}.csv" if path_output is None else path_output

    docker = sorted(docker, key=lambda x: x["label"])
    try:
        with open(path_output_, "w", encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "label"])
            for context in docker:
                writer.writerow([context["url"], context["label"]])
        return path_output_
    except PermissionError:
        logger.warning(f"导出文件被占用 - file={path_output_}")
        path_output_ = f"{path_output_template}.{random.randint(1, 10)}.csv"
        return output_cleaning_dataset(dir_output, docker, path_output=path_output_)


def load_classified_hosts(filter_: bool = True) -> list:
    """
    获取最新的分类数据

    :param filter_: 过滤器，是否滤除无价值的标签数据
    :return:
    """
    filter_ = bool(filter_)

    # 读取 mining 分类结果
    classifier_outputs = [
        os.path.join(DIR_CACHE_CLASSIFY, i)
        for i in os.listdir(DIR_CACHE_CLASSIFY)
        if i.startswith("mining") and i.endswith(".csv")
    ]

    # 默认目录下不存在分类结果
    if not classifier_outputs:
        logger.critical("默认目录下缺少分类器的缓存文件 - " f"dir={DIR_CACHE_CLASSIFY}")
        sys.exit()

    # 导入最新的分类数据
    classifier_output_latest = max(classifier_outputs)
    with open(classifier_output_latest, "r", encoding="utf8") as f:
        context = list(csv.reader(f))
        title_, body_ = context[0], context[1:]
        data = [dict(zip(title_, element)) for element in body_]

    # 返回源数据
    if filter_ is False:
        data = [element["url"] for element in data]
        return data

    # 过滤掉无价值的标签数据
    filter_docker = []
    for element in data:
        url_, label_ = element["url"], element["label"]
        if "危险通信" in label_ or "请求异常" in label_:
            continue
        filter_docker.append(url_)

    return filter_docker


def output_foul_dataset():
    raise NotImplementedError


def preview(path_output: str, docker: list = None):
    """

    :param path_output:
    :param docker:
    :return:
    """
    # Windows 系统下自动打开洗好的导出文件
    if path_output:
        if "win" in sys.platform:
            os.startfile(path_output)
        logger.success("清洗完毕 - path={}".format(path_output))
        return True
    else:
        logger.error("数据异常 - docker={}".format(docker))
        return False


def run_collector(env: str = "development", silence: bool = True):
    """

    :param silence:
    :param env: within [development production]
    :return:
    """
    # 实例化并运行采集器
    # 假设的应用场景中，非Windows系统强制无头启动Selenium
    silence_ = bool(silence) if "win" in sys.platform else True

    # 补全模版文件名
    path_file_txt = PATH_DATASET_TEMPLATE.format(
        str(datetime.now(TIME_ZONE_CN)).split(" ")[0]
    )

    # 初始化运行环境
    need_to_build_collector = create_env(path_file_txt)

    """
    TODO [√]启动采集器
    -------------------
    当程序初次运行时需要启动一次采集器挖掘站点。
    缓存的数据长时间内有效，而采集过程较为耗时，故不必频繁启用。
    """
    # 确保定时任务下每日至少采集一次
    # 生产环境下每次运行程序都要启动采集器
    if need_to_build_collector or env == "production":
        SSPanelHostsCollector(
            path_file_txt=path_file_txt, silence=silence_, debug=False
        ).run()

        # Collector 使用 `a` 指针方式插入新数据，此处使用 data_cleaning() 去重
        data_cleaning(path_file_txt)


def run_classifier(power: int = 16, source: str = "local", batch: int = 1):
    """

    :param batch: batch 应是自然数，仅在 source==remote 时生效，用于指定拉取的数据范围。
        - batch=1 表示拉取昨天的数据（默认），batch=2 表示拉取昨天+前天的数据，以此类推往前堆叠
        - 当设置的 batch 大于母仓库存储量时会自动调整运行了逻辑，防止溢出。
    :param source: within [local remote] 指定数据源，仅对分类器生效
        - local：使用本地 Collector 采集的数据进行分类
        - remote：使用 SSPanel-Mining 母仓库数据进行分类（需要下载数据集）
    :param power: 采集功率
    :return:
    """
    # 校准分类器功率
    power = power if isinstance(power, int) else max(os.cpu_count(), 4)
    power = os.cpu_count() * 2 if os.cpu_count() >= power else power

    # 限定核心启动参数
    if source not in ["local", "remote"]:
        return

    # 限定远程数据的获取批次
    batch = 1 if not isinstance(batch, int) else batch
    batch = 1 if batch < 1 else batch

    """
    TODO [√]启动分类器
    -------------------
    发动一次超高并发数的检测行为。
    刷新运行缓存，并对采集到的链接进行清洗、分类、二级存储。
    """
    if source == "local":
        # 导入数据集，也即识别并读回 Collector 的输出
        urls = load_sspanel_hosts()
    else:
        # 下载母仓库数据集
        logger.info("正在访问远程数据...")
        urls = load_sspanel_hosts_remote(batch=batch)

    # 数据清洗
    sug = SSPanelHostsClassifier(docker=urls)
    sug.go(power=power)

    """
    TODO [√]分类简述
    -------------------
    #   - 分类数据将以 .csv 文件形式存储在 `/database/staff_hosts/classifier` 中
    #   - 分为以下几种类型（存在较小误判概率）：
    #       - Normal：无验证站点
    #       - Google reCAPTCHA：Google reCAPTCHA 人机验证
    #       - GeeTest Validation：极验滑块验证（绝大多数）/选择文字验证（极小概率）
    #       - Email Validation：邮箱验证（开放域名）
    #       - SMS：手机短信验证 [钓鱼执法？]
    #       - CloudflareDefenseV2：站点正在被攻击 or 高防服务器阻断了爬虫流量
    #   - 存在以下几种限型实例：
    #       - 限制注册(邮箱)：要求使用指定域名的邮箱接收验证码
    #       - 限制注册(邀请)：要求必须使用有效邀请码注册
    #       - 请求异常(ERROR:STATUS_CODE)：请求异常，携带相应状态码
    #       - 拒绝注册：管理员关闭注册接口
    #       - 危险通信：HTTP 直连站点
    """
    # 存储分类结果
    docker = sug.offload()
    path_output = output_cleaning_dataset(dir_output=DIR_CACHE_CLASSIFY, docker=docker)

    # 数据预览
    preview(path_output=path_output, docker=docker)
