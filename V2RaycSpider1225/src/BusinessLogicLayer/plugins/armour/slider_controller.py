import base64
import random
import time

from PIL import Image
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class SliderValidation(object):

    def __init__(self, driver, debug=False, business_name: str = "SliderValidation"):
        # Selenium操作句柄
        self.api = driver
        # 设置默认的全局等待时长
        self.wait = WebDriverWait(self.api, 5)
        # 业务名 用于debug模式下标记控制台的信息输出
        self.business_name = business_name
        # 缓存物理算子的运动终点坐标（计算值而非真实值）
        self.distance = 0

        self.debug = debug
        if self.debug:
            print(">>> 正在加载 Slider Validation Debug Module...")

    def _debug_printer(self, msg):
        if self.debug:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} | <{self.business_name}>{msg}")

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
        # 1.读取完整背景图与残缺背景图
        # 完整背景图与残缺背景图的边长参数一致
        full_bg, bg = Image.open(full_bg_path), Image.open(bg_path)

        # 2.遍历ImageObject图片对象的每一个像素点
        # ImageObject.size[0] 图片长度
        for i in range(offset, full_bg.size[0]):
            # ImageObject.size[1] 图片宽度
            for j in range(full_bg.size[1]):
                # 2.1将遍历到的像素点坐标（x,y）传到像素比对方法 is_pixel_equal() 用于找出像素明度差距较大的像素坐标集合
                if not self._is_pixel_equal(full_bg, bg, i, j):
                    # 视此坐标点为第一个明度差值较大的像素点，既“缺口拼图”的像素临界（起）点
                    # 因为“滑块移动”是橫向移动滑块，不考虑垂直方向（y轴）坐标的影响，故此时仅返回x轴坐标，既横向坐标
                    offset = i
                    # 将此时遍历到的坐标返回
                    return offset

        # 2.2 此时返回的坐标点必然是错误的
        # 但为了程序高效运行，需要返回一个符合参数格式的变量
        return offset

    @staticmethod
    def _get_track(boundary_coordinates):
        """
        生成一维坐标的运动轨迹
        :param boundary_coordinates:运动终点坐标
        :return:运动轨迹
        """
        # 轨迹树
        track = []
        # 物理算子当前所在的一维空间位置
        current_coordinates = 0
        """
        计算方案1：根据匀变速直线运动公式生成物理算子运动轨迹
        - 已知量：运动终点坐标 boundary_coordinates
        """
        mid = boundary_coordinates * 3.2 / 4
        t = 1.
        v = 0
        # 当算子还未抵达终点时，持续生成下一步坐标
        while current_coordinates < boundary_coordinates:
            # 当算子处于“距离中点”前时加速，越过后减速
            if current_coordinates < mid:
                a = random.uniform(1.8712, 1.912)
            else:
                a = -random.uniform(0.11, 0.13)
            v0 = v
            v = v0 + a * t
            # move 是每一步的位移
            move = v0 * t + 1 / 2 * a * t * t
            current_coordinates += move
            track.append(round(move, 3))

        return track

    def _get_slider(self, driver, slider_class='geetest_slider_button'):
        """
        获取滑块
        :param driver:
        :param slider_class: 滑块的 class 属性
        :return: 滑块对象
        """
        # 重试10次，每次失败冷却0.5s 最多耗时5s，否则主动抛出错误
        for _ in range(10):
            try:
                slider = driver.find_element_by_class_name(slider_class)
                return slider
            except Exception as e:
                print("{}:{}".format(self.__class__, e))
                time.sleep(0.5)
        else:
            raise NoSuchElementException

    def _drag_the_ball(self, driver, track):
        """
        根据运动轨迹拖拽
        :param driver: webdriver 对象
        :param track: 运动轨迹
        """
        # 获取物理算子对象
        slider = self._get_slider(driver)

        # 捕获物理算子 keep hold
        ActionChains(driver).click_and_hold(slider).perform()

        # 控制算子按照规定轨迹 -> 向前行走
        # 由于生成算子轨迹的算法包含超餐及扰动因子，故算子并不能刚刚好“踏在终点线上”
        # 故在规定路径行完后需要进行拟人化的微调
        for step in track:
            # step是每一步的位移
            ActionChains(driver).move_by_offset(xoffset=step, yoffset=0).perform()

        # 算子一维空间物理位置的校准 -> 回滑或震荡
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
        time.sleep(0.5)

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

    def run(self, full_bg_path: str = 'fbg.png', bg_path: str = 'bg.png') -> bool:

        self._debug_printer("唤醒极验...")
        self._awakening()

        self._debug_printer("正在加载 Geetest 验证码...")
        self.wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_slice')))
        self.wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_fullbg')))

        self._debug_printer("正在截取拼图图像...")
        full_bg_path, bg_path = self._save_full_bg(self.api, full_bg_path), self._save_bg(self.api, bg_path)

        self._debug_printer("获取残缺边界...")
        x_axis_coordinate_of_boundary = self._get_offset(full_bg_path, bg_path, offset=35)

        self._debug_printer("获取移动轨迹...")
        track = self._get_track(x_axis_coordinate_of_boundary)

        self._debug_printer("正在拽动滑块...")
        self._drag_the_ball(self.api, track)

        # 执行成功，结束重试循环，返回true
        if self._is_success():
            self._debug_printer("程序执行成功！")
            return True
        # 元素加载超时，捕获失败，陷入重试循环
        else:
            self._debug_printer("程序执行失败！即将返回主干业务流...")
            return False
