# -*- coding: utf-8 -*-
# Time       : 2021/7/22 21:34
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 区分geetest_v2/geetest_v3
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome

from .geetest_v2 import GeeTest2
from .geetest_v3 import GeeTest3


class GeeTestAdapter:
    def __init__(self, driver: Chrome, debug=False, business_name=None, full_img_path=None, notch_img_path=None):
        self.api = driver
        self.debug = debug
        self.business_name = business_name
        self.full_img_path = full_img_path
        self.notch_img_path = notch_img_path

        self.core = self.checker(self.api)

    @staticmethod
    def checker(api: Chrome):
        try:
            api.find_element_by_class_name("geetest_radar_tip_content")
            return GeeTest3
        except NoSuchElementException:
            return GeeTest2

    def run(self):
        return self.core(
            driver=self.api,
            debug=self.debug,
            business_name=self.business_name,
            full_img_path=self.full_img_path,
            notch_img_path=self.notch_img_path
        ).run()
