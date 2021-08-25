# -*- coding: utf-8 -*-
# Time       : 2021/7/21 17:39
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 识别GeeTest_v3滑动验证的示例
import base64
import time

from selenium.common.exceptions import NoSuchElementException

from .core import SliderValidator, By, ec


class GeeTest3(SliderValidator):

    def __init__(self, driver, debug=False, business_name="GeeTest_v3", full_img_path=None, notch_img_path=None):
        super(GeeTest3, self).__init__(driver=driver, debug=debug, full_img_path=full_img_path,
                                       notch_img_path=notch_img_path, business_name=business_name)
        self.threshold = 60
        self.offset = 35

    @staticmethod
    def save_base64img(data, path_):
        """
        将 base64 数据转化为图片保存到指定位置
        :param data: base64 数据，不包含类型
        :param path_: 保存的全路径
        """
        with open(path_, "wb") as f:
            f.write(base64.b64decode(data))

    def get_base64_by_canvas(self, class_name, contain_type):
        """
        将 canvas 标签内容转换为 base64 数据
        :param class_name: canvas 标签的类名
        :param contain_type: 返回的数据是否包含类型
        :return: base64 数据
        """
        # 防止图片未加载完就下载一张空图
        bg_img = ''
        while len(bg_img) < 5000:
            get_img_js = 'return document.getElementsByClassName("' + class_name + '")[0].toDataURL("image/png");'
            bg_img = self.api.execute_script(get_img_js)
            time.sleep(0.5)
        if contain_type:
            return bg_img
        return bg_img[bg_img.find(',') + 1:]

    def capture_full_img(self):
        element_class_name = "geetest_canvas_fullbg geetest_fade geetest_absolute"
        data = self.get_base64_by_canvas(element_class_name, False)
        self.save_base64img(data, self.full_img_path)
        return self.full_img_path

    def capture_notch_img(self):
        element_class_name = "geetest_canvas_bg geetest_absolute"
        data = self.get_base64_by_canvas(element_class_name, False)
        self.save_base64img(data, self.notch_img_path)
        return self.notch_img_path

    def capture_slider(self, xpath: str = None, class_name: str = None):
        # 重试10次，每次失败冷却0.5s 最多耗时5s，否则主动抛出错误
        for _ in range(10):
            try:
                self.slider = self.api.find_element_by_class_name(class_name)
                return self.slider
            except Exception as e:
                print("{}:{}".format(self.__class__, e))
                time.sleep(0.5)

        raise NoSuchElementException

    def activate_validator(self):
        self.api.find_element_by_class_name('geetest_radar_tip').click()
        time.sleep(0.5)

    def is_success(self):
        """

        :return:
        """
        button_text2 = self.api.find_element_by_class_name('geetest_success_radar_tip_content')
        text2 = button_text2.text

        if text2 == '验证成功':
            return True
        return False

    def run(self) -> bool:
        # 唤醒Geetest 点击唤出
        self.activate_validator()
        # 加载元素
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_slice')))
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_fullbg')))
        # 获取完整&有缺口的截图并存储
        full_img_path = self.capture_full_img()
        notch_img_path = self.capture_notch_img()
        # 识别缺口左边界坐标
        boundary = self.identify_boundary(full_img_path, notch_img_path, self.offset)
        # debug模式下 可视化识别结果
        if self.debug:
            self.check_boundary(boundary)
        # 生成轨迹
        track, position = self.generate_track(
            # 轨迹生成器解决方案
            solution=self.operator_sport_v1,
            # 计算所需的物理量初始值字典
            phys_params={
                'boundary': boundary,
                'current_coordinate': 0,
                'mid': boundary * 3.3 / 4,
                't': 0.5,
                'alpha_factor': 3.4011,
                'beta_factor': 3.5211,
            }
        )
        # 获取滑块对象
        slider = self.capture_slider(class_name="geetest_slider_button")
        # 根据轨迹拖动滑块
        self.drag_slider(
            track=track,
            slider=slider,
            position=position,
            boundary=boundary,
            use_imitate=True,
            is_hold=False,
            momentum_convergence=False
        )
        # 执行成功，结束重试循环
        if self.is_success():
            if self.debug:
                print(f"--->{self.business_name}：验证成功")
            return True
        if self.debug:
            print(f"--->{self.business_name}：验证失败")
        return False
