__all__ = ['validation_interface', 'SliderValidation']

import base64
import random
import time

from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# --------------------------------------------------
# v4.3.X version plugin: anti-anti-spider-mechanism
# --------------------------------------------------
# 临时邮箱
temp_email_url = 'https://www.linshiyouxiang.net/'


# 邮箱验证
class EmailAddressVerification(object):
    def __init__(self, api): ...

    def run(self, email): ...


# 滑动验证模组
class SliderValidation(object):

    def __init__(self, driver, debug=False):
        self.api = driver
        self.debug = debug
        self.wait = WebDriverWait(self.api, 5)

        if self.debug:
            print(">>> 正在加载 Slider Validation Debug Module...")

    def _debug_printer(self, msg):
        if self.debug:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))} | {msg}")

    @staticmethod
    def _save_base64img(data_str, save_name):
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
    def _get_base64_by_canvas(driver, class_name, contain_type):
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
            get_img_js = 'return document.getElementsByClassName("' + class_name + '")[0].toDataURL("image/png");'
            bg_img = driver.execute_script(get_img_js)

            time.sleep(0.5)
        # print(bg_img)
        if contain_type:
            return bg_img
        else:
            return bg_img[bg_img.find(',') + 1:]

    def _save_full_bg(self, driver, full_bg_path="fbg.png",
                      full_bg_class='geetest_canvas_fullbg geetest_fade geetest_absolute'):
        """
        保存完整的的背景图
        :param driver: webdriver 对象
        :param full_bg_path: 保存路径
        :param full_bg_class: 完整背景图的 class 属性
        :return: 保存路径
        """
        bg_img_data = self._get_base64_by_canvas(driver, full_bg_class, False)
        self._save_base64img(bg_img_data, full_bg_path)
        return full_bg_path

    def _save_bg(self, driver, bg_path="bg.png",
                 bg_class='geetest_canvas_bg geetest_absolute'):
        """
        保存包含缺口的背景图
        :param driver: webdriver 对象
        :param bg_path: 保存路径
        :param bg_class: 背景图的 class 属性
        :return: 保存路径
        """
        bg_img_data = self._get_base64_by_canvas(driver, bg_class, False)
        self._save_base64img(bg_img_data, bg_path)
        return bg_path

    @staticmethod
    def _is_pixel_equal(img1, img2, x, y):
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

    def _get_offset(self, full_bg_path, bg_path, offset=60):
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
                if not self._is_pixel_equal(full_bg, bg, i, j):
                    offset = i
                    return offset
        return offset

    @staticmethod
    def _get_track(distance):
        """
        根据偏移量获取拟人的移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        track = []
        current = 0
        mid = distance * 3.724481 / 4
        t = 1.4414
        v = 0
        while current < distance:
            if current < mid:
                a = random.uniform(0.7012, 0.812)
            else:
                a = -random.uniform(0.11, 0.13)
            v0 = v
            v = v0 + a * t
            move = v0 * t + 1 / 2 * a * t * t
            current += move
            track.append(round(move, 3))

        return track

    def _get_slider(self, driver, slider_class='geetest_slider_button'):
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

    def _drag_the_ball(self, driver, track):
        """
        根据运动轨迹拖拽
        :param driver: webdriver 对象
        :param track: 运动轨迹
        """
        slider = self._get_slider(driver)
        ActionChains(driver).click_and_hold(slider).perform()
        for step in track:
            ActionChains(driver).move_by_offset(xoffset=step, yoffset=0).perform()

        time.sleep(0.1)
        # 模拟人往回滑动
        imitate = ActionChains(driver).move_by_offset(xoffset=-2, yoffset=0)
        time.sleep(0.015)
        imitate.perform()
        time.sleep(random.uniform(0.6, 1))
        imitate.perform()
        time.sleep(0.04)
        imitate.perform()
        time.sleep(0.012)
        imitate.perform()
        time.sleep(0.019)
        imitate.perform()
        time.sleep(0.033)
        ActionChains(driver).move_by_offset(xoffset=3, yoffset=0).perform()
        # 放开圆球
        ActionChains(driver).release(slider).perform()
        time.sleep(1.5)

    def _awakening(self):
        self.api.find_element_by_class_name('geetest_radar_tip').click()
        time.sleep(1)

    def _is_try_again(self):
        """[summary]

        判断是否能够点击重试
        """
        button_text = self.api.find_element_by_class_name('geetest_radar_tip_content')
        text = button_text.text
        if text == '尝试过多' or text == '网络不给力' or text == '请点击重试':
            button = self.api.find_element_by_class_name('geetest_reset_tip_content')
            button.click()

    def _is_success(self):
        """[summary]

        判断是否成功
        """
        button_text2 = self.api.find_element_by_class_name('geetest_success_radar_tip_content')
        text2 = button_text2.text
        if text2 == '验证成功':
            # print(text2)
            return True
        return False

    def run(self, full_bg_path: str = 'fbg.png', bg_path: str = 'bg.png', retry_num: int = 1):

        self._debug_printer("唤醒极验...")

        self._awakening()

        self._debug_printer("正在加载 Geetest 验证码...")
        self.wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_slice')))
        self.wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_fullbg')))

        self._debug_printer("正在截取拼图图像...")
        full_bg_path = self._save_full_bg(self.api, full_bg_path)
        bg_path = self._save_bg(self.api, bg_path)

        # 失败重试循环体
        for _ in range(retry_num):

            self._debug_printer("计算移动距离...")
            distance = self._get_offset(full_bg_path, bg_path, offset=45)

            self._debug_printer("获取移动轨迹...")
            track = self._get_track(distance)

            self._debug_printer("正在拽动滑块...")
            self._drag_the_ball(self.api, track)

            # 执行成功，结束重试循环，返回true
            if self._is_success():
                self._debug_printer("程序执行成功！")
                return True
            # 元素加载超时，捕获失败，陷入重试循环
            else:
                # 等待滑块复位
                self._debug_printer("元素加载超时！正在等待重试...")
                time.sleep(1.5)
                continue
        # 执行失败
        self._debug_printer("程序执行失败！即将返回主干业务流...")
        return False


eav = EmailAddressVerification
sv = SliderValidation


def validation_interface(api, methods='slider', **kwargs):
    """
    :api: 传入driver驱动
    full_bg_path: 自定义截图路径
    bg_path：自定义截图路径
    """
    # 加载 Geetest 滑动验证
    if methods == 'slider':
        return sv(api).run(full_bg_path=kwargs.get("full_bg_path"), bg_path=kwargs.get("bg_path"))
    # TODO:加载Email邮箱验证模块<开发中>
    if methods == 'email':
        return eav(api).run(kwargs)


def utils_slider(api, full_bg_path, bg_path):
    return SliderValidation(driver=api).run(full_bg_path=full_bg_path, bg_path=bg_path)
