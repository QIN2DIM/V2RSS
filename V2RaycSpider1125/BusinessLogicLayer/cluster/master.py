# TODO:
#  1.继续微调加载参数
#  2.采集不求快，求稳！


__all__ = ['ActionMasterGeneral']

import time
import random
from datetime import datetime, timedelta
from string import printable
from os.path import join

from redis.exceptions import RedisError
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from config import CHROMEDRIVER_PATH, TIME_ZONE_CN, SERVER_DIR_DATABASE_CACHE, logger
from BusinessCentralLayer.middleware.subscribe_io import *
from BusinessLogicLayer.cluster.plugins import get_header, get_proxy


class BaseAction(object):
    """针对STAFF机场的基准行为"""

    def __init__(self, silence=True, anti=True, email_class='@qq.com', life_cycle=1) -> None:
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

        self.life_cycle = self.generate_life_cycle(life_cycle)

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
            WebDriverWait(api, timeout).until(EC.presence_of_all_elements_located)
        else:
            WebDriverWait(api, timeout).until(EC.presence_of_element_located((
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
        self.subscribe = WebDriverWait(api, 100).until(EC.presence_of_element_located((
            By.XPATH,
            element_xpath_str
        ))).get_attribute(href_xpath_str)
        if self.subscribe:
            for x in range(3):
                try:
                    flexible_distribute(self.subscribe, class_, self.life_cycle, driver_name=self.__class__.__name__)
                    logger.info(">> GET <{}> -- {}:{}".format(self.__class__.__name__, class_, self.subscribe))
                    break
                except RedisError:
                    time.sleep(1)
                    continue
            else:
                return None
        else:
            if retry >= 3:
                return None
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

    def __init__(self, register_url: str, silence: bool = True, anti: bool = True, email: str = '@gmail.com',
                 life_cycle: int = 1, hyper_params: dict = None):
        """

        @param register_url: 机场注册网址，STAFF原生register接口
        @param silence: 静默启动；为True时静默访问<linux 必须启用>
        @param anti: 目标是否有反爬虫措施；默认为True BaseAction将根据目标是否具备反爬虫措施做出不同的行为
        @param email: register页面显示的默认邮箱；常见为 @qq.com or @gmail.com
        @param life_cycle: 会员试用时长 trail time；
        @param hyper_params: 模型超级参数
        """
        super(ActionMasterGeneral, self).__init__(silence, anti, email, life_cycle)

        # 机场注册网址
        self.register_url = register_url

        # 模型超级参数
        self.hyper_params = {
            'v2ray': True,
            'ssr': True,
            'trojan': False,
            'anti_slider': False,
        }
        if hyper_params:
            self.hyper_params.update(hyper_params)

    # TODO -> 断网重连 -> 引入retrying 第三方库替代原生代码
    def sign_up(self, api, anti_slider=False, retry_=0, max_retry_num_=3):
        """

        @param api:
        @param anti_slider:
        @param retry_:
        @param max_retry_num_:
        @return:
        """
        if retry_ > max_retry_num_:
            raise WebDriverException
        from BusinessLogicLayer.cluster.plugins import anti_module
        WebDriverWait(api, 15) \
            .until(EC.presence_of_element_located((By.ID, 'name'))) \
            .send_keys(self.username)

        api.find_element_by_id('email').send_keys(self.username)

        api.find_element_by_id('passwd').send_keys(self.password)

        api.find_element_by_id('repasswd').send_keys(self.password)

        # 滑动验证
        def spider_module(retry=0, max_retry_num=2):
            if retry > max_retry_num:
                return False
            try:
                full_bg_path = join(SERVER_DIR_DATABASE_CACHE, 'fbg.png')
                bg_path = join(SERVER_DIR_DATABASE_CACHE, 'bg.png')
                response = anti_module(api, methods='slider', full_bg_path=full_bg_path, bg_path=bg_path)
                return response
            except NoSuchElementException:
                retry += 1
                spider_module(retry)

        if self.hyper_params['anti_slider']:
            if not spider_module():
                api.refresh()
                return self.sign_up(api)

        api.find_element_by_id('register-confirm').click()

        for x in range(max_retry_num_):
            try:
                time.sleep(1.5)
                api.find_element_by_xpath("//button[contains(@class,'confirm')]").click()
                break
            except NoSuchElementException as e:
                # logger.exception('{} || {}'.format(self.__class__, e))
                logger.error('{}验证超时，3s 后重试'.format(self.__class__.__name__))
                time.sleep(3)

    @logger.catch()
    def run(self):
        logger.info("DO -- <{}>".format(self.__class__.__name__))

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
            if self.hyper_params['ssr']:
                self.load_any_subscribe(
                    api,
                    """//a[@onclick="importSublink('ssr')"]/..//a[contains(@class,'copy')]""",
                    'data-clipboard-text',
                    'ssr'
                )
        except WebDriverException as e:
            logger.exception(">>> Exception <{}> -- {}".format(self.__class__.__name__, e))
        finally:
            api.quit()
