__all__ = ['ActionMasterGeneral']

import random
import time
from datetime import datetime, timedelta
from os.path import join
from string import printable
from urllib.parse import urlparse

from selenium.common.exceptions import *
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from BusinessCentralLayer.middleware.subscribe_io import FlexibleDistribute
from BusinessCentralLayer.setting import CHROMEDRIVER_PATH, TIME_ZONE_CN, SERVER_DIR_CACHE_BGPIC, logger
from BusinessLogicLayer.plugins.faker_info import get_header, get_proxy


class BaseAction(object):
    """针对STAFF机场的基准行为"""

    def __init__(self, silence=True, anti=True, email_class='@qq.com', life_cycle=1, beat_sync=True) -> None:
        """
        设定登陆选项，初始化登陆器
        @param silence: 静默启动；为True时静默访问<linux 必须启用>
        @param anti: 目标是否有反爬虫措施；默认为True BaseAction将根据目标是否具备反爬虫措施做出不同的行为
        @param email_class: register页面显示的默认邮箱；常见为 @qq.com or @gmail.com
        @param life_cycle: 会员试用时长 trail time；
        """

        # 初始化注册信息
        self.username, self.password, self.email = self.generate_account(email_class=email_class)

        # 信息共享v2ray订阅链接
        self.subscribe = ''

        # 初始化浏览器
        self.silence, self.anti = silence, anti

        self.register_url = ''

        self.end_life = self.generate_life_cycle(life_cycle)

        # 是否为单爬虫调试模式
        self.beat_sync = beat_sync

    @staticmethod
    def generate_account(email_class: str = '@qq.com') -> tuple:
        """
        :param email_class: @qq.com @gmail.com ...
        """
        # 账号信息
        username = ''.join([random.choice(printable[:printable.index('!')]) for _ in range(9)])
        password = ''.join([random.choice(printable[:printable.index(' ')]) for _ in range(15)])
        email = username + email_class

        return username, password, email

    @staticmethod
    def generate_life_cycle(trial_time: int) -> str:
        """
        end_life = Shanghai_nowTime + trialTime
        @param trial_time:机场VIP时长（试用时间）
        @return: subscribe失效时间
        """
        return str(datetime.now(TIME_ZONE_CN) + timedelta(days=trial_time)).split('.')[0]

    def set_spider_option(self, use_proxy=False) -> Chrome:
        """
        ChromeDriver settings
        @param use_proxy: 使用代理 <当前版本禁用>：部分机场禁止国内ip访问
        @return:
        """

        options = ChromeOptions()

        # 最高权限运行
        options.add_argument('--no-sandbox')

        # 隐身模式
        options.add_argument('-incognito')

        # 无缓存加载
        options.add_argument('--disk-cache-')

        # 设置中文
        options.add_argument('lang=zh_CN.UTF-8')

        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # 更换头部
        options.add_argument(f'user-agent={get_header()}')

        if use_proxy:
            proxy_ip = get_proxy(True)
            if proxy_ip:
                options.add_argument(f'proxy-server={proxy_ip}')

        # 静默启动
        if self.silence is True:
            options.add_argument('--headless')

        # 无反爬虫机制：高性能启动，禁止图片加载及js动画渲染，加快selenium页面切换效率
        def load_anti_module():
            chrome_pref = {"profile.default_content_settings": {"Images": 2, 'javascript': 2},
                           "profile.managed_default_content_settings": {"Images": 2}}
            options.experimental_options['prefs'] = chrome_pref
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            d_c = DesiredCapabilities.CHROME
            d_c['pageLoadStrategy'] = 'none'
            return Chrome(
                options=options,
                executable_path=CHROMEDRIVER_PATH,
                desired_capabilities=d_c
            )

        if self.anti is False:
            return load_anti_module()
        else:
            # 有反爬虫/默认：一般模式启动
            return Chrome(options=options, executable_path=CHROMEDRIVER_PATH)

    def sign_in(self, api: Chrome):
        """Please rewrite this function!"""

    def sign_up(self, api: Chrome):
        """Please rewrite this function!"""

    @staticmethod
    def wait(api: Chrome, timeout: float, tag_xpath_str) -> None:
        if tag_xpath_str == 'all':
            time.sleep(1)
            WebDriverWait(api, timeout).until(expected_conditions.presence_of_all_elements_located)
        else:
            WebDriverWait(api, timeout).until(expected_conditions.presence_of_element_located((
                By.XPATH, tag_xpath_str
            )))

    def check_in(self, button_xpath_str: str):
        """daily check in ,add available flow"""

    def load_any_subscribe(self, api: Chrome, element_xpath_str: str, href_xpath_str: str, class_: str, retry=0):
        """

        @param api: ChromeDriverObject
        @param element_xpath_str: 用于定位链接所在的标签
        @param href_xpath_str: 用于取出目标标签的属性值，既subscribe
        @param class_: 该subscribe类型，如`ssr`/`v2ray`/`trojan`
        @param retry: 失败重试
        @todo 使用 retrying 模块替代retry参数实现的功能（引入断网重连，断言重试，行为回滚...）
        @return:
        """
        self.subscribe = WebDriverWait(api, 30).until(expected_conditions.presence_of_element_located((
            By.XPATH,
            element_xpath_str
        ))).get_attribute(href_xpath_str)

        # 若对象可捕捉则解析数据并持久化数据
        if self.subscribe:
            # 失败重试3次
            for x in range(3):
                # ['domain', 'subs', 'class_', 'end_life', 'res_time', 'passable','username', 'password', 'email']
                try:
                    # 机场域名
                    domain = urlparse(self.register_url).netloc
                    # 采集时间
                    res_time = str(datetime.now(TIME_ZONE_CN)).split('.')[0]
                    # 链接可用，默认为true
                    passable = 'true'
                    # 信息键
                    docker = [domain, self.subscribe, class_, self.end_life, res_time, passable, self.username,
                              self.password, self.email]
                    # 根据不同的beat_sync形式持久化数据
                    FlexibleDistribute(docker=docker, beat_sync=self.beat_sync)
                    # 数据存储成功后结束循环
                    logger.success(">> GET <{}> -> {}:{}".format(self.__class__.__name__, class_, self.subscribe))
                    # TODO ADD v5.1.0更新特性，记录机场域名-订阅域名映射缓存
                    # set_task2url_cache(task_name=self.__class__.__name__, register_url=self.register_url,
                    #                    subs=self.subscribe)
                    break
                except Exception as e:
                    logger.debug(">> FAILED <{}> -> {}:{}".format(self.__class__.__name__, class_, e))
                    time.sleep(1)
                    continue
            # 若没有成功存储，返回None
            else:
                return None
        # 否则调入健壮工程
        # TODO 判断异常原因，构建解决方案，若无可靠解决方案，确保该任务安全退出
        else:
            if retry >= 3:
                raise TimeoutException
            retry += 1
            self.load_any_subscribe(api, element_xpath_str, href_xpath_str, class_, retry)

    def run(self):
        """Please rewrite this function!"""

        # Get register url

        # Locate register tag and send keys

        # Click the submit button

        # * Shut down the sAirPort TOS pop-us

        # * Jump to the login page
        # ** Locate sign in tag and send keys
        # ** Click the sign in button

        # To the sAirPort homepage

        # Wait for page elements to load

        # Get the subscribe link of ssr/trojan/v2ray

        # Save subscribe link and refresh redis task list

        # Close Chrome driver and release memory


class ActionMasterGeneral(BaseAction):
    """
    观察了一波发现，大多数机场主前端功底薄弱，基于STAFF原生的代码基本一致，故生此类+协程大幅度减少代码量
    """

    def __init__(self, register_url: str, silence: bool = True, anti_slider: bool = False, email: str = '@gmail.com',
                 life_cycle: int = 1, hyper_params: dict = None, beat_sync: bool = True, sync_class: dict = None):
        """

        @param register_url: 机场注册网址，STAFF原生register接口
        @param silence: 静默启动；为True时静默访问<linux 必须启用>
        @param anti_slider: 目标是否有反爬虫措施；默认为True BaseAction将根据目标是否具备反爬虫措施做出不同的行为
        @param email: register页面显示的默认邮箱；常见为 @qq.com or @gmail.com
        @param life_cycle: 会员试用时长 trail time；
        @param hyper_params: 模型超级参数
        """
        super(ActionMasterGeneral, self).__init__(silence, True, email, life_cycle, beat_sync)

        self.action_name = self.__class__.__name__

        # 机场注册网址
        self.register_url = register_url

        self.anti_slider = anti_slider

        # 模型超级参数
        self.hyper_params = {
            'v2ray': True,
            'ssr': True,
            'trojan': False,
            'rocket': False,  # Shadowrocket
            'qtl': False,  # Quantumult
            'kit': False,  # Kitsunebi

            'usr_email': False,  # True: 需要自己输入邮箱后缀(默认为qq) False:邮箱后缀为选择形式只需填写主段
        }
        if hyper_params:
            self.hyper_params.update(hyper_params)

        if not self.hyper_params['usr_email']:
            self.email = self.username

        # TODO 使用该参数控制账户解耦合时采集的链接类型
        # 当前版本弃用
        if sync_class:
            self.sync_class = sync_class

    # TODO -> 断网重连 -> 引入retrying 第三方库替代原生代码
    def sign_up(self, api, retry_=0, max_retry_num_=5):
        """

        @param api:
        @param retry_:
        @param max_retry_num_:
        @return:
        """
        if retry_ > max_retry_num_:
            return False

        from BusinessLogicLayer.plugins.defensive_counter import validation_interface
        WebDriverWait(api, 15) \
            .until(expected_conditions.presence_of_element_located((By.ID, 'name'))) \
            .send_keys(self.username)

        api.find_element_by_id('email').send_keys(self.email)

        api.find_element_by_id('passwd').send_keys(self.password)

        api.find_element_by_id('repasswd').send_keys(self.password)

        # 滑动验证
        def spider_module(retry=0, max_retry_num=2):
            if retry > max_retry_num:
                return False
            try:
                full_bg_path = join(SERVER_DIR_CACHE_BGPIC, f'fbg_{self.action_name}.png')
                bg_path = join(SERVER_DIR_CACHE_BGPIC, f'bg_{self.action_name}.png')
                response = validation_interface(api, methods='slider', full_bg_path=full_bg_path, bg_path=bg_path)
                return response
            except NoSuchElementException:
                retry += 1
                spider_module(retry)

        if self.anti_slider:
            if not spider_module():
                api.refresh()
                return self.sign_up(api)

        api.find_element_by_id('register-confirm').click()

        for x in range(max_retry_num_):
            try:
                time.sleep(1.5)
                api.find_element_by_xpath("//button[contains(@class,'confirm')]").click()
                break
            except NoSuchElementException:
                logger.debug('{}验证超时，3s 后重试'.format(self.__class__.__name__))
                time.sleep(3)

    # TODO 当sync_class 参数可用时，使用if-if 结构发起任务；否则使用if-elif，该操作防止链接溢出
    def run(self):
        logger.info("DO -- <{}>:beat_sync:{}".format(self.__class__.__name__, self.beat_sync))

        api = self.set_spider_option()

        api.get(self.register_url)

        try:
            self.sign_up(api)

            self.wait(api, 20, "//div[@class='card-body']")

            # get v2ray link
            if self.hyper_params['v2ray']:
                self.load_any_subscribe(
                    api,
                    "//div[@class='buttons']//a[contains(@class,'v2ray')]",
                    'data-clipboard-text',
                    'v2ray'
                )

            # get ssr link
            elif self.hyper_params['ssr']:
                self.load_any_subscribe(
                    api,
                    """//a[@onclick="importSublink('ssr')"]/..//a[contains(@class,'copy')]""",
                    'data-clipboard-text',
                    'ssr'
                )
            # if self.hyper_params['trojan']: ...
            # if self.hyper_params['kit']: ...
            # if self.hyper_params['qtl']: ...
        except TimeoutException:
            logger.error(f'>>> TimeoutException <{self.__class__.__name__}> -- {self.register_url}')
        # except WebDriverException as e:
        #     logger.exception(f">>> Exception <{self.__class__.__name__}> -- {e}")
        except Exception as e:
            logger.exception(f">>> Exception <{self.__class__.__name__}> -- {e}")
        finally:
            # Middleware.hera.put_nowait("push")
            api.quit()


if __name__ == '__main__':
    ActionMasterGeneral('', sync_class={'ssr': True})
