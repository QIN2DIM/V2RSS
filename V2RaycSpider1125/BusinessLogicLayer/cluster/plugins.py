__all__ = [
    'anti_module',  # 反爬虫组件调用入口
    'get_header',  # 获取FAKE USERAGENT
    'get_proxy',  # 获取GlobalProxyIP
]

import os
import base64
import random
import time

import requests
from PIL import Image
from requests.exceptions import *
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# -------------------------------------------
# v4.3.X version plugin: !anti-crawler
# -------------------------------------------

# 邮箱验证
class FakerEmailMechanism(object):
    def __init__(self, api): ...

    def run(self, email): ...


# 滑动验证模组
class SliderMechanism(object):

    def __init__(self, driver):
        self.api = driver
        self.wait = WebDriverWait(self.api, 5)

    @staticmethod
    def save_base64img(data_str, save_name):
        """
        将 base64 数据转化为图片保存到指定位置
        :param data_str: base64 数据，不包含类型
        :param save_name: 保存的全路径
        """
        img_data = base64.b64decode(data_str)
        file = open(save_name, 'wb')
        file.write(img_data)
        file.close()

    @staticmethod
    def get_base64_by_canvas(driver, class_name, contain_type):
        """
        将 canvas 标签内容转换为 base64 数据
        :param class_name: canvas 标签的类名
        :param contain_type: 返回的数据是否包含类型
        :param driver: 返回的数据是否包含类型
        :return: base64 数据
        """
        # 防止图片未加载完就下载一张空图
        bg_img = ''
        while len(bg_img) < 5000:
            getImgJS = 'return document.getElementsByClassName("' + class_name + '")[0].toDataURL("image/png");'
            bg_img = driver.execute_script(getImgJS)

            time.sleep(0.5)
        # print(bg_img)
        if contain_type:
            return bg_img
        else:
            return bg_img[bg_img.find(',') + 1:]

    def save_full_bg(self, driver, full_bg_path="fbg.png",
                     full_bg_class='geetest_canvas_fullbg geetest_fade geetest_absolute'):
        """
        保存完整的的背景图
        :param driver: webdriver 对象
        :param full_bg_path: 保存路径
        :param full_bg_class: 完整背景图的 class 属性
        :return: 保存路径
        """
        bg_img_data = self.get_base64_by_canvas(driver, full_bg_class, False)
        self.save_base64img(bg_img_data, full_bg_path)
        return full_bg_path

    def save_bg(self, driver, bg_path="bg.png",
                bg_class='geetest_canvas_bg geetest_absolute'):
        """
        保存包含缺口的背景图
        :param driver: webdriver 对象
        :param bg_path: 保存路径
        :param bg_class: 背景图的 class 属性
        :return: 保存路径
        """
        bg_img_data = self.get_base64_by_canvas(driver, bg_class, False)
        self.save_base64img(bg_img_data, bg_path)
        return bg_path

    @staticmethod
    def is_pixel_equal(img1, img2, x, y):
        """
        判断两个像素是否相同
        :param img2: 图片1
        :param img1: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(
                pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    def get_offset(self, full_bg_path, bg_path, offset=60):
        """
        获取缺口偏移量
        :param full_bg_path: 不带缺口图片路径
        :param bg_path: 带缺口图片路径
        :param offset: 偏移量， 默认 35
        :return:
        """
        full_bg = Image.open(full_bg_path)
        bg = Image.open(bg_path)
        for i in range(offset, full_bg.size[0]):
            for j in range(full_bg.size[1]):
                if not self.is_pixel_equal(full_bg, bg, i, j):
                    offset = i
                    return offset
        return offset

    @staticmethod
    def get_track(distance):
        """
        根据偏移量获取拟人的移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        track = []
        current = 0
        mid = distance * 3 / 4
        t = 0.4
        v = 0
        while current < distance:
            if current < mid:
                a = random.randint(3, 4)
            else:
                a = -random.randint(7, 8)
            v0 = v
            v = v0 + a * t
            move = v0 * t + 1 / 2 * a * t * t
            current += move
            track.append(round(move))
        return track

    def get_slider(self, driver, slider_class='geetest_slider_button'):
        """
        获取滑块
        :param driver:
        :param slider_class: 滑块的 class 属性
        :return: 滑块对象
        """
        while True:
            try:
                slider = driver.find_element_by_class_name(slider_class)
                break
            except Exception as e:
                print("{}:{}".format(self.__class__, e))
                time.sleep(0.5)
        return slider

    def drag_the_ball(self, driver, track):
        """
        根据运动轨迹拖拽
        :param driver: webdriver 对象
        :param track: 运动轨迹
        """
        slider = self.get_slider(driver)
        ActionChains(driver).click_and_hold(slider).perform()
        while track:
            x = random.choice(track)
            ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
            track.remove(x)
        time.sleep(0.1)
        # 模拟人往回滑动
        imitate = ActionChains(driver).move_by_offset(xoffset=-2, yoffset=0)
        time.sleep(0.015)
        imitate.perform()
        time.sleep(random.randint(6, 10) / 10)
        imitate.perform()
        time.sleep(0.04)
        imitate.perform()
        time.sleep(0.012)
        imitate.perform()
        time.sleep(0.019)
        imitate.perform()
        time.sleep(0.033)
        ActionChains(driver).move_by_offset(xoffset=1, yoffset=0).perform()
        # 放开圆球
        ActionChains(driver).pause(random.randint(6, 14) / 10).release(slider).perform()

    def is_try_again(self):
        """[summary]

        判断是否能够点击重试
        """
        button_text = self.api.find_element_by_class_name('geetest_radar_tip_content')
        text = button_text.text
        if text == '尝试过多' or text == '网络不给力' or text == '请点击重试':
            button = self.api.find_element_by_class_name('geetest_reset_tip_content')
            button.click()

    def is_success(self):
        """[summary]

        判断是否成功
        """
        button_text2 = self.api.find_element_by_class_name('geetest_success_radar_tip_content')
        text2 = button_text2.text
        if text2 == '验证成功':
            # print(text2)
            return True
        return False

    def run(self, hyper_params=None):

        # 唤醒极验
        self.api.find_element_by_class_name('geetest_radar_tip').click()
        time.sleep(1)

        # 加载 Geetest 验证码
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_slice')))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_fullbg')))

        for x in range(10):
            # get full image
            full_bg_path = self.save_full_bg(self.api, full_bg_path=hyper_params.get('full_bg_path', 'fbg.png'))

            # get defective image
            bg_path = self.save_bg(self.api, bg_path=hyper_params.get('bg_path', 'bg.png'))

            # 移动距离
            distance = self.get_offset(full_bg_path, bg_path, offset=25)

            # 获取移动轨迹
            track = self.get_track(distance)

            # 滑动圆球至缺口处
            self.drag_the_ball(self.api, track)

            time.sleep(1.5)
            if self.is_success():
                return True
            else:
                return False


def anti_module(api, methods='slider', **kwargs):
    """
    :api: 传入driver驱动
    full_bg_path: 自定义截图路径
    bg_path：自定义截图路径
    """
    # 加载 Geetest 滑动验证
    if methods == 'slider':
        return SliderMechanism(api).run(kwargs)
    # TODO:加载Email邮箱验证模块<开发中>
    if methods == 'email':
        return FakerEmailMechanism(api).run(kwargs)


# -------------------------------------------
# v4.3.X version plugin: !anti-crawler
# -------------------------------------------

def get_header(use_fake=True) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    try:
        if use_fake:
            import tempfile
            from fake_useragent import UserAgent
            from config import SERVER_PATH_DATABASE_HEADERS, SERVER_DIR_DATABASE, logger

            try:
                if SERVER_PATH_DATABASE_HEADERS not in os.listdir(tempfile.gettempdir()):
                    os.system('copy {} {}'.format(
                        os.path.join(SERVER_DIR_DATABASE, SERVER_PATH_DATABASE_HEADERS),
                        os.path.join(tempfile.gettempdir(), SERVER_PATH_DATABASE_HEADERS)
                    ))
                headers.update({"User-Agent": UserAgent().random})
            except Exception as e:
                logger.exception(e)
    finally:
        return headers['User-Agent']


def get_proxy(deployment=False) -> str or bool:
    proxy_pool_interface = 'http://127.0.0.1:5555/random'
    if deployment:
        try:
            return 'http://{}'.format(requests.get(proxy_pool_interface).text.strip())
        except RequestException:
            return False


# -------------------------------------------
# fixme:v4.3.X version Plugin--deprecated
# -------------------------------------------

# 获取STAFF机场关键信息：可用时长、可用流量
def get_STAFF_info(api):
    """

    :param api: chrome driver
    :return:
    """
    time.sleep(3)
    try:
        card_body = api.find_elements_by_xpath("//div[@class='card-body']")

        # 会员时长
        available_time = card_body[0].text

        # 可用流量
        available_flow = card_body[1].text

        print(available_time, available_flow)
        return available_time, available_flow

    except NoSuchElementException:
        return '找不到元素,或本机场未基于STAFF开发前端'
