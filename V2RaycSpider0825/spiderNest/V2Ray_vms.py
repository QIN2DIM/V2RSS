from spiderNest.preIntro import *
from MiddleKey import VMes_IO

import threading
"""#######################################################################################"""
# 机场官网
fa = FakeAccount()
ufo_SignUP = random.choice(fa.air_target('v2ray'))
ufo_SignIn = '/'.join(ufo_SignUP.split('/')[:-1] + ['login'])
# 账号信息
username, password, email = fa.get_fake_account()
"""#######################################################################################"""
# 全局静默
wait = 30


# 自动化行为
class UFO_Spider(object):

    def __init__(self, silence=True, Anti_mode=False):
        """
        设定登陆选项，初始化登陆器
        :param silence: （默认使用）为True时静默访问
        """

        # 初始化注册信息
        self.user, self.psw, self.email = username, password, email

        # v2ray订阅链接
        self.VMess = ''

        """初始化浏览器"""
        # 静默设定
        self.silence = silence

        # 目标是否设置反爬虫机制
        self.anti = Anti_mode

        # 获取Chrome操作权限
        self.api = set_spiderOption(self.silence, self.anti)

        # 设定全局静默市场
        self.wait = WebDriverWait(self.api, 5)

        # 启动爬虫
        self.ufo_spider(self.api)

    def sign_in(self, api, user, psw):
        api.switch_to.window(api.current_window_handle)
        self.wait.until(EC.presence_of_all_elements_located)
        api.find_element_by_id('email').send_keys(user)
        api.find_element_by_id('password').send_keys(psw)
        api.find_element_by_id('login').click()

    def getLink(self, api, timeout=wait):
        try:
            # 获取订阅链接
            self.VMess = WebDriverWait(api, wait).until(EC.presence_of_element_located((
                By.XPATH,
                "//div[@class='buttons']/a[contains(@class,'v2ray')]"
            ))).get_attribute('data-clipboard-text')
        except Exception or TimeoutException:
            # 任务超时，或断言异常，保存注册成功的账号信息
            self.VMess = '  '.join([email, password])
        finally:
            # 对象转换
            global VMess
            VMess = self.VMess

    def ufo_spider(self, api):

        # 加载 Geetest 验证码 滑动验证
        def __assert__():
            # 加载 Geetest 验证码 滑动验证
            self.wait.until(EC.presence_of_all_elements_located)
            # 滑块验证模块
            anti_slider(api)

        # 断言页面跳转，若注册页面跳转至登录页面，则调用相应模块，否则随引导直接进入机场首页
        def __switcher__():
            try:
                self.sign_in(api, email, password)
            except NoSuchElementException or WebDriverException:
                pass

        # 进入注册页面
        api.get(ufo_SignUP)

        # 断言反爬虫机制
        __assert__()

        # 注册界面
        # api:驱动 username：用户名 password：密码 wait：等待时长
        sign_up_STAFF(api, username, password, wait)

        # 断言审计规则
        TOS_STAFF(api, wait)

        # 断言界面切换
        __switcher__()

        # 成功进入内页:并获取链接
        self.getLink(api, wait)

        # threading.Thread(target=get_STAFF_info, args=(self.api, )).start()

        # 保存数据
        # save_login_info(self.VMess)
        VMes_IO.save_login_info(self.VMess, 'v2ray')
        # 安全退出
        api.quit()


"""#######################################################################################"""

if __name__ == '__main__':
    VMess = ''
    # 静默启动,Linux无头驱动，降低驱动性能，提升运行稳定性
    UFO_Spider(silence=True, Anti_mode=False)

    # 显式启动，本地调试
    # UFO_Spider(silence=False, Anti_mode=True)
    print(VMess)
