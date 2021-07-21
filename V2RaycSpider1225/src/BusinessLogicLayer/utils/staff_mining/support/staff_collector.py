__all__ = ['StaffCollector']

import random
import time
import warnings

from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

from ..common.exceptions import CollectorSwitchError


class StaffCollector(object):
    def __init__(self, cache_path: str, chromedriver_path: str, silence: bool = True, debug: bool = False, ):
        """

        :param cache_path:
        :param silence:
        :param debug:
        :param chromedriver_path:
        """
        self.GOOGLE_SEARCH_API = "https://www.google.com.hk"
        self.SEARCH_QUERY = '"特此免费授予任何获得副本的人这个软件和相关的文档文件"'

        self.CHROMEDRIVER_PATH = chromedriver_path
        self.cache_path = cache_path
        self.debug = debug
        self.silence = silence

    @staticmethod
    def _down_to_api(api: Chrome, search_query: str):
        """# 键入并跳转至相关页面"""
        while True:
            try:
                input_tag = api.find_element_by_xpath("//input[@name='q']")
                input_tag.click()
                input_tag.clear()
                input_tag.send_keys(search_query)
                input_tag.send_keys(Keys.ENTER)
                break
            except NoSuchElementException:
                time.sleep(0.5)
                continue

    @staticmethod
    def _page_switcher(api: Chrome, is_home_page: bool = False):
        # 首页 -> 第二页
        if is_home_page:
            while True:
                try:
                    ActionChains(api).send_keys(Keys.END).perform()
                    time.sleep(0.5)
                    api.find_element_by_xpath("//a[@id='pnnext']").click()
                    break
                except NoSuchElementException:
                    # 检测到到流量拦截 主动抛出异常并采取备用方案
                    if "sorry" in api.current_url:
                        raise CollectorSwitchError
                    time.sleep(0.5)
                    api.refresh()
                    continue
        # 第二页 -> 第N页
        else:
            while True:
                try:
                    ActionChains(api).send_keys(Keys.END).perform()
                    time.sleep(0.5)
                    page_switchers = api.find_elements_by_xpath("//a[@id='pnnext']")
                    next_page_bottom = page_switchers[-1]
                    next_page_bottom.click()
                    break
                except NoSuchElementException:
                    # 检测到到流量拦截 主动抛出异常并采取备用方案
                    if "sorry" in api.current_url:
                        raise CollectorSwitchError
                    time.sleep(0.5)
                    continue

    def _capture_host(self, api: Chrome):
        # hosts = api.find_elements_by_xpath("//span[@class='qXLe6d dXDvrc']//span[@class='fYyStc']")
        hosts = api.find_elements_by_xpath("//div[contains(@class,'NJjxre')]//cite[@class='iUh30 Zu0yb qLRx3b tjvcx']")

        with open(self.cache_path, 'a', encoding='utf8') as f:
            for host in hosts:
                try:
                    f.write(f"{host.text.split(' ')[0].strip()}/auth/register\n")
                except Exception as e:
                    warnings.warn(f"{e}")

    def set_spider_options(self) -> Chrome:
        options = ChromeOptions()

        # 最高权限运行
        options.add_argument('--no-sandbox')

        # 隐身模式
        options.add_argument('-incognito')

        # 无缓存加载
        options.add_argument('--disk-cache-')

        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')

        # 更换头部
        options.add_argument(f"user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                             f" AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'")

        options.add_argument('--disable-blink-features=AutomationControlled')

        # 静默启动
        if self.silence is True:
            options.add_argument('--headless')

        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        try:
            # 有反爬虫/默认：一般模式启动
            if self.CHROMEDRIVER_PATH:
                _api = Chrome(options=options, executable_path=self.CHROMEDRIVER_PATH)
            else:
                _api = Chrome(options=options)
            _api.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                           Object.defineProperty(navigator, 'webdriver', {
                             get: () => undefined
                           })
                         """
            })
            return _api
        except WebDriverException as e:
            if "chromedriver" in str(e):
                print(f">>> 指定目录下缺少chromedriver {self.CHROMEDRIVER_PATH}")
                exit()

    def run(self, page_num: int = 26, sleep_node: int = 5):
        # API 实例化
        api = self.set_spider_options()
        # 进度条 初始化
        loop_progress = tqdm(
            total=page_num,
            desc=f"STAFF COLLECTOR",
            ncols=150,
            unit="piece",
            dynamic_ncols=False,
            leave=True
        )
        loop_progress.set_postfix({"status": "__initialize__"})

        try:
            # 根据关键词 去首页
            api.get(self.GOOGLE_SEARCH_API)
            self._down_to_api(api=api, search_query=self.SEARCH_QUERY)

            # 获取page_num页的注册链接
            # 正常情况一页10个链接 既共获取page_num * 10个链接
            for x in range(page_num):

                # ==============================================================
                # 采集器
                # ==============================================================
                # 萃取注册链接并保存
                self._capture_host(api=api)
                loop_progress.set_postfix({"status": "__collect__"})
                loop_progress.update(1)
                # self._debugger(message=f"Successfully collected the staff-hosts from page {x + 1}", level="info")
                # print(f"<StaffCollector> Successfully collected the staff-hosts  [{x + 1}/{page_num}]")
                # ==============================================================
                # 翻页控制器
                # ==============================================================
                # 第1页 -> 第2页
                if x == 0:
                    self._page_switcher(api=api, is_home_page=True)
                # 第2页-> 第N页
                self._page_switcher(api=api, is_home_page=False)
                # ==============================================================
                # 休眠控制器
                # ==============================================================
                # 每sleep_node页进行一次随机时长的休眠
                if x % sleep_node == 0:
                    tax_ = random.uniform(3, 5)
                    # self._debugger(message=f"Tactical sleep! The mission will continue in {round(tax_, 3)} seconds",
                    #                level="debug")
                    # print(f"<StaffCollector> Tactical sleep! The mission will continue in {round(tax_, 3)} seconds")
                    loop_progress.set_postfix({"status": "__sleep__"})
                    time.sleep(tax_)
        finally:
            api.quit()

            # self._debugger(message="Mission completed", level="info")
            # self._debugger(message=f"the cache file address is {self.cache_path}", level="info")
