# -*- coding: utf-8 -*-
# Time       : 2021/7/21 17:39
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 识别GeeTest_v2滑动验证的示例
import time

from selenium.common.exceptions import NoSuchElementException

from .core import SliderValidator, By, ec, ActionChains


class GeeTest2(SliderValidator):
    def __init__(self, driver, debug=False, business_name="GeeTest_v2", full_img_path=None, notch_img_path=None):
        super(GeeTest2, self).__init__(driver=driver, debug=debug, business_name=business_name,
                                       full_img_path=full_img_path, notch_img_path=notch_img_path, )

        self.threshold = 60
        self.offset = 60

    def capture_full_img(self):
        gt_full_img = self.api.find_element_by_xpath("//a[contains(@class,'gt_fullbg')]")
        gt_full_img.screenshot(filename=self.full_img_path)

    def capture_notch_img(self):
        gt_notch_img = self.wait.until(
            ec.invisibility_of_element_located((By.XPATH, "//a[contains(@class,'gt_hide')]"))
        )
        gt_notch_img.screenshot(filename=self.notch_img_path)

    def activate_validator(self):
        ActionChains(self.api).click_and_hold(self.slider).perform()

    def is_success(self):
        for _ in range(2):
            try:
                label = self.api.find_element_by_class_name("gt_info_type")
                if self.debug:
                    print(f"--->result: {label.text.strip()}\n")
                if "通过" in label.text.strip():
                    return True
                return False
            except NoSuchElementException:
                time.sleep(0.5)
                continue

    def run(self) -> bool:
        # 加载元素
        self.wait.until(ec.presence_of_all_elements_located)
        # 获取滑块对象
        slider = self.capture_slider(xpath="//div[contains(@class,'slider_')]")
        # 获取完整的截图并存储
        self.capture_full_img()
        # 唤醒Geetest hold住
        self.activate_validator()
        # 获取缺口截图并存储
        self.capture_notch_img()
        # 识别缺口左边界坐标
        boundary = self.identify_boundary(self.full_img_path, self.notch_img_path, self.offset)
        if 60 <= boundary <= 63:
            boundary -= 12
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
                't': 1.2,
                'alpha_factor': 0.4011,
                'beta_factor': 0.5211,
            }
        )
        # 拖动滑块
        self.drag_slider(
            track=track,
            slider=slider,
            position=position,
            boundary=boundary,
            use_imitate=False,
            is_hold=True,
            momentum_convergence=True
        )
        # 验证通过
        if self.is_success():
            return True
        return False
