# 三堡包架构数据管理

from spiderNest.preIntro import *
from MiddleKey import VMes_IO

"""#######################################################################################"""
# 机场官网
fa = FakeAccount()
ufo_SignUP = random.choice(fa.air_target('ssr'))
ufo_SignIn = '/'.join(ufo_SignUP.split('/')[:-1] + ['login'])
# 账号信息
username, password, email = fa.get_fake_account()
"""#######################################################################################"""


class UFO_Spider(object):
    """VMess链接抓取脚本[嵌入滑块验证模块]"""

    def __init__(self, silence=True, anti=True):
        """
        设定登陆选项，初始化登陆器
        :param silence: （默认使用）为True时静默访问
        """

        # 初始化注册信息
        self.user, self.psw, self.email = username, password, email

        # 信息共享v2ray订阅链接
        self.VMess = ''

        # 初始化浏览器
        self.silence = silence
        self.anti = anti
        # self.api = set_spiderOption(self.silence, self.anti)
        # self.wait = WebDriverWait(self.api, 5)

        # 自启
        # self.ufo_spider(self.api)

    @staticmethod
    def sign_in(api, user, psw):
        # api.switch_to.window(api.current_window_handle)
        for x in range(50):
            try:
                api.find_element_by_id('remember_me')
                api.find_element_by_id('email').send_keys(user)
                api.find_element_by_id('passwd').send_keys(psw)
                api.find_element_by_id('login').click()
                break
            except NoSuchElementException or TimeoutException:
                time.sleep(.5)
                continue

    def ufo_spider(self):

        api = set_spiderOption(self.silence, self.anti)

        api.get(ufo_SignUP)

        WebDriverWait(api, 15) \
            .until(EC.presence_of_element_located((By.ID, 'email'))) \
            .send_keys(username)
        api.find_element_by_id('passwd').send_keys(password)
        api.find_element_by_id('repasswd').send_keys(password)

        # click sign up bottom
        try:
            time.sleep(0.5)
            api.find_element_by_id('reg').click()
        except NoSuchElementException:
            pass

        try:
            self.sign_in(api, email, password)
            time.sleep(0.5)
        except NoSuchElementException or WebDriverException:
            pass

        # try to get link
        try:
            VMess = WebDriverWait(api, 20).until(EC.presence_of_element_located((
                By.XPATH,
                "//div[@class='cur-input-group-btn']/button[contains(@class,'sub-ssr')]"
            ))).get_attribute('data-clipboard-text')
            self.VMess = VMess
            VMes_IO.save_login_info(VMess, 'ssr')
        except Exception or TimeoutException:
            pass
        finally:
            api.quit()

    def start(self):
        self.ufo_spider()


class LocalResp(UFO_Spider):

    def __init__(self, silence=True, anti=False):
        super(LocalResp, self).__init__(silence=silence, anti=anti)

    def quick_get(self):
        ssr_link = requests.get('http://yao.qinse.top/ssr.txt').text
        self.VMess = ssr_link if 'http' in ssr_link else ''

    def start(self):
        self.quick_get()
        if self.VMess:
            return self.VMess
        else:
            try:
                self.ufo_spider()
                return self.VMess
            except WebDriverException:
                return 'DRIVER驱动设置有误'


if __name__ == '__main__':
    us = UFO_Spider(silence=True, anti=True)
    us.start()
    print(us.VMess)
