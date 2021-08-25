"""
    - 集爬取、清洗、分类与测试为一体的STAFF采集队列自动化更新组件
    - 需要本机启动系统全局代理，或使用“国外”服务器部署
    - 本模块内嵌协程启动项，请勿从外部并发调用此模块，此举将引起重大复写灾难
    - 本模块网络通信基于协程进行，在程序调试时请注释掉 monkey包
"""
__all__ = ['staff_api']

import os

from src.BusinessCentralLayer.setting import logger, SERVER_DIR_DATABASE, CHROMEDRIVER_PATH
from src.BusinessLogicLayer.utils.staff_mining import StaffChecker, StaffCollector, IdentifyRecaptcha, \
    StaffEntropyGenerator
from src.BusinessLogicLayer.utils.staff_mining.common.exceptions import CollectorSwitchError, NoSuchWindowException


class _Interface:

    def __init__(self):
        self._cache_dir_staff_hosts = os.path.join(SERVER_DIR_DATABASE, "staff_hosts")
        self._cache_dir_classifier = os.path.join(self._cache_dir_staff_hosts, "classifier")

        self._cache_path_staff_hosts = os.path.join(self._cache_dir_staff_hosts, "staff_host.txt")
        self._path_staff_arch_recaptcha = os.path.join(self._cache_dir_classifier, "staff_arch_recaptcha.txt")
        self._path_staff_arch_entropy = os.path.join(self._cache_dir_classifier, "staff_arch_entropy.txt")

        self._cache_files = []
        self._create_local_db()

        self.sc_ = None

    def _create_local_db(self):
        """
        初始化生产结果输出路径
        :return:
        """
        # 1. If the target path does not exist:
        #   the cache path will be generated in the order of the structure tree (the order cannot be wrong)
        # 2. If the target path exists:
        #   upload the cache file path to `self._cache_files` for subsequent cache cleaning
        for node in [self._cache_dir_staff_hosts, self._cache_dir_classifier]:
            if not os.path.exists(node):
                os.mkdir(node)
            else:
                for cache_file in os.listdir(node):
                    # Keep the data that is more expensive to collect.
                    if ("staff_host.txt" in cache_file) or ('staff_arch_recaptcha.txt' in cache_file):
                        continue
                    if cache_file.endswith('.txt'):
                        self._cache_files.append(os.path.join(node, cache_file))

    def refresh_cache(self, mode='reset'):
        """
        Clear the classified cache of staff-host, the data in staff-host.txt will not be affected
        :return:
        """
        if mode == 'reset':
            for cache_file in self._cache_files:
                with open(cache_file, 'w', encoding="utf8"):
                    pass
        elif mode == 'de-dup':
            for cache_file in self._cache_files:
                with open(cache_file, 'r', encoding="utf8") as f:
                    data = [i for i in f.read().split('\n') if i]
                with open(cache_file, 'w', encoding="utf8") as f:
                    for element in set(data):
                        f.write(f"{element}\n")

    @logger.catch()
    def collector(self, silence: bool = True, debug: bool = False, page_num: int = 26, sleep_node: int = 5):
        """
        STAFF site collector

        Use Selenium to obtain small batch samples through Google Search Engine
        (according to statistics, there are about 245 legal sites worldwide)

        The collection principle is roughly as follows:
        Use the characteristic word SEO to detect whether the target site exists `/staff` page content.

        :param silence: True无头启动（默认），False显示启动（请仅在调试时启动）
        :param debug:
        :param page_num: 采集“页数”，一页约10条检索结果，依上文所述，此处page_num设置为26左右
        :param sleep_node: 每采集多少页进行一次随机时长的休眠，默认sleep_node为5
        :return:
        """
        logger.info(f"Successfully obtained interface permissions -> {StaffCollector.__name__}")

        try:
            # 采集器实例化
            StaffCollector(
                silence=silence,
                # cache_path 为采集到的站点链接输出目录
                cache_path=self._cache_path_staff_hosts,
                chromedriver_path=CHROMEDRIVER_PATH,
                debug=debug
            ).run(
                page_num=page_num,
                sleep_node=sleep_node
            )
        except CollectorSwitchError:
            logger.error("<StaffCollector> Traffic interception is detected, and the system is taking a backup plan")
        except IndexError:
            logger.warning("<StaffCollector> An error occurred while switching the page number")
        except NoSuchWindowException:
            logger.error("<StaffCollector> The Chromedriver exited abnormally")
        except Exception as e:
            logger.exception(f"<StaffCollector> {e}")

    def checker(self, business_name: str, debug: bool = True, power: int = os.cpu_count()):
        """
        STAFF checker executes related function modules according to different business names
        :param business_name: STAFF检查器业务名 此处业务名应与StaffChecker中的相应的方法名完全一致
                filter_live_urls | 筛选存活链接（可以正常握手的站点）
                filter_std_urls  | 尽最大努力筛选标准链接[1.剔除需要邮箱注册的；2.剔除拒绝注册的；3.剔除夹带私活的]
                classify_urls    | 根据不同的注册条件分类订阅源

                -- 业务集成 -> classify
        :param debug: Only affect the output of different levels of logs, and will not affect entity behavior
        :param power: Collect the power,
            determine the number of concurrent coroutine engines, the maximum cannot exceed 60
        :return:
        """

        if business_name == "classify_urls":
            cache_path_load = self._cache_path_staff_hosts
            cache_dir_save = self._cache_dir_classifier
        else:
            return False

        # Read cache cache file
        with open(cache_path_load, 'r', encoding='utf8') as f:
            data = [i for i in f.read().split('\n') if i]

        # Instantiate the STAFF checker
        # Specify the link iterator to be cleaned, output cache address, task power, debug mode, and business name
        self.sc_ = StaffChecker(
            task_docker=set(data),
            output_dir=cache_dir_save,
            power=power,
            debug=debug,
            work_name=business_name
        )
        self.sc_.go()

    def extractor(self):
        _classifier = {}
        for node in os.listdir(self._cache_dir_classifier):
            file = os.path.join(self._cache_dir_classifier, node)
            if file.endswith('.txt'):
                with open(file, 'r', encoding="utf8") as f:
                    _classifier[node.replace('.txt', '')] = list(set([i for i in f.read().split("\n") if i]))
        return self._cache_dir_classifier, _classifier

    @logger.catch()
    def is_recaptcha(self, urls, silence=True):
        """

        :param urls:
        :param silence:
        :return:
        """
        if isinstance(urls, str):
            urls = [urls, ]
        elif isinstance(urls, list):
            urls = list(set(urls))
        elif isinstance(urls, set):
            urls = list(urls)
        IdentifyRecaptcha(
            task_docker=urls,
            chromedriver_path=CHROMEDRIVER_PATH,
            output_path=self._path_staff_arch_recaptcha,
            power=os.cpu_count(),
            silence=silence
        ).go()

    @staticmethod
    def manual_labeling(input_path: str, output_path: str):
        """
        [NOTE] Please call this interface only during program debugging

        Manually mark the type of staff site

        :param input_path: It must be a plain text file with links, using utf 8 encoding, and cutting one line with ‘\n’
        :param output_path:
        :return:
        """
        # FileNotFoundError
        if (not os.path.exists(input_path)) or (not os.path.exists(os.path.dirname(output_path))):
            return False

        # Use Selenium to open the corresponding sites one by one, and manually mark the object properties
        with open(input_path, 'r', encoding='utf8') as f:
            data = [i for i in f.read().split('\n') if i]
        # Instantiate Selenium operation object
        driver = StaffCollector(
            cache_path='',
            chromedriver_path=CHROMEDRIVER_PATH,
            silence=False
        ).set_spider_options()
        # Perform related business processes
        for url in data:
            driver.get(url)
            # It is recommended to use simple mark symbols to classify objects with a clear meaning
            # For example: this is the expected goal -> t
            # For example: this is not the expected goal -> f
            # For example: This is a noise sample -> x
            label = input(f">>> {url} <<<")
            with open(os.path.join(output_path), 'a', encoding="utf8") as f:
                f.write(f"{label}\t{url}\n")

        driver.quit()

    def generator(self, urls, silence=True):
        """

        :param silence:
        :param urls:
        :return:
        """
        if isinstance(urls, str):
            urls = [urls, ]
        elif isinstance(urls, list):
            urls = list(set(urls))
        elif isinstance(urls, set):
            urls = list(urls)
        StaffEntropyGenerator(
            task_docker=urls,
            chromedriver_path=CHROMEDRIVER_PATH,
            output_path=self._path_staff_arch_entropy,
            power=4,
            silence=silence
        ).go()

    def is_first_run(self) -> bool:
        """
        Determine whether this module is running for the first time
        :return:
                - True: first run
                - False: at least one cycle has been successfully completed
        """
        if not os.path.exists(self._cache_path_staff_hosts):
            return True
        with open(self._cache_path_staff_hosts, 'r', encoding="utf8") as f:
            return not f.read()

    def go(self, debug: bool = False, silence: bool = True, power: int = os.cpu_count(),
           use_collector: bool = True, use_checker: bool = True, identity_recaptcha: bool = False,
           use_generator: bool = False) -> tuple:
        """
        Execute business flow in series.

        collect -> check -> extract -> generate

        :param power:
        :param debug:
        :param silence: Control the headless startup mode of Selenium-Google Search Engine (--headless)
            True: The program starts silently (default). It must be started silently when deployed in Linux.
            False：Display startup, display the operating process of the browser (only used when debugging the program).

        :param use_collector: Whether to use the collector
            True：Start Selenium-GoogleSearchEngine indiscriminate collection_staff-host.
            False: Not enabled
            - If you use this module for the first time,
                be sure to start the collector to complete the original accumulation of staff-host,
                otherwise the checker cannot be started.
            - Since the staff host is not a data that changes frequently,
                after the initial collection,
                logic can be designed to close the collector to improve the operating efficiency of the module

        :param use_checker: Whether to use the checker
            - True: Start the checker to clean the staff-host layer by layer
        and save the output to the corresponding cache directory
            - False: not enabled - It is recommended to open the
        whole process STAFF Checker is used to clean, filter, test, and update the system collection queue. - The
        case of not opening: when debugging the program

        :param identity_recaptcha:

        :param use_generator: Generate system collection queue.

        :return:
        """
        # 启动STAFF采集器
        if use_collector:
            self.collector(silence=silence, debug=debug, page_num=26, sleep_node=5)
        # 启动STAFF检查器
        if use_checker:
            # 进行基本的站点分类任务
            self.checker(business_name="classify_urls", debug=debug, power=power)
        # 识别reCAPTCHA人机验证站点
        if identity_recaptcha:
            # 供检测的站点实体列表
            urls = []
            # 未初始化STAFF检查器
            if self.sc_ is None:
                # STAFF MINING 模块初次运行，无系统缓存
                # 此时无法使用决策器
                if self._cache_files is None:
                    pass
                # 读取上一次STAFF检查器的运行缓存
                else:
                    files = [node for node in self._cache_files if ('general' in node) or ('other' in node)]
                    for file in files:
                        with open(file, 'r', encoding="utf8") as f:
                            urls += [i for i in f.read().split('\n') if i]
            # 本次go运行启动了STAFF检查器
            # 使用本次STAFF检查器的运行缓存执行决策器
            else:
                urls = self.sc_.queue_staff_arch_pending
            # 若有可供识别的站点实体，则执行决策器，否则输出警告日志
            if urls:
                self.is_recaptcha(urls=set(urls), silence=True)
            else:
                logger.warning("No identifiable site instance.")
        # 启动STAFF生成器
        if use_generator:
            self.generator(urls=[], silence=True)

        return self.extractor()


staff_api = _Interface()

if __name__ == '__main__':
    staff_api.go(
        debug=False,
        silence=False,
        power=32,
        identity_recaptcha=False,
        use_collector=True,
        use_checker=False,
        use_generator=False,
    )
