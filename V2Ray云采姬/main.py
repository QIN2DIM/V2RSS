import json
import os
import random
import time
from string import printable
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import *
"""#######################################################################################"""
# 机场官网
ufo_SignUP = 'https://ufocloud.xyz/auth/register'
ufo_SignIn = 'https://ufocloud.xyz/auth/login'
# 账号信息
username = ''.join([random.choice(printable[:printable.index('!')])
                    for i in range(9)])
password = ''.join([random.choice(printable[:printable.index(' ')])
                    for j in range(15)])
email = username + '@gmail.com'
"""#######################################################################################"""


class UFO_Spider(object):

    def __init__(self, silence=True):
        """
        设定登陆选项，初始化登陆器
        :param silence: （默认使用）为True时静默访问
        """

        # 初始化注册信息
        self.user, self.psw, self.email = username, password, email

        # 信息共享v2ray订阅链接
        self.VMess = ''

        # 初始化浏览器
        self.ufo_spider(silence)

    @staticmethod
    def ufo_spider(silence):
        global VMess

        # 浏览器初始化
        options = ChromeOptions()

        # 设置启动项
        if silence is True:
            options.add_argument('--headless')  # 静默启动
        options.add_argument('--no-sandbox')  # 最高权限运行
        options.add_argument('-incognito')  # 隐身模式
        options.add_argument('--disk-cache-')
        chrome_prefs = {"profile.default_content_settings": {"images": 2, 'javascript': 2},
                        "profile.managed_default_content_settings": {"images": 2}}
        options.experimental_options['prefs'] = chrome_prefs
        options.add_experimental_option(
            'excludeSwitches', ['enable-automation'])
        d_c = DesiredCapabilities.CHROME
        d_c['pageLoadStrategy'] = 'none'

        with webdriver.Chrome(
                options=options,
                desired_capabilities=d_c,
        ) as api:
            api.get(ufo_SignUP)

            # register
            time.sleep(1)
            WebDriverWait(api, 20)\
                .until(EC.presence_of_element_located((By.ID, 'name')))\
                .send_keys(username)
            api.find_element_by_id('email').send_keys(username)
            api.find_element_by_id('passwd').send_keys(password)
            api.find_element_by_id('repasswd').send_keys(password)

            # click sign up bottom
            time.sleep(1)
            api.find_element_by_id('register-confirm').click()

            # kill the Tos
            time.sleep(1)
            WebDriverWait(api, 30)\
                .until(EC.presence_of_element_located((
                    By.XPATH, "//button[@class='swal2-confirm swal2-styled']"
                ))).click()

            # try to get link
            VMess = WebDriverWait(api, 60).until(EC.presence_of_element_located((
                By.XPATH,
                "//div[@class='buttons']/a[contains(@class,'v2ray')]"
            ))).get_attribute('data-clipboard-text')


if __name__ == '__main__':
    VMess = ''
    UFO_Spider(
        silence=True,  # 云端采集必须静默运行
    )
    print(VMess)
