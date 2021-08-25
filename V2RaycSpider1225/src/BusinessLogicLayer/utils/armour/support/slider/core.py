# -*- coding: utf-8 -*-
# Time       : 2021/7/21 17:39
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import random
import time

from PIL import Image, ImageDraw, ImageFont
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class SliderValidator:
    def __init__(self, driver: Chrome, debug: bool = False, full_img_path: str = None, notch_img_path: str = None,
                 business_name: str = "SliderValidator"):
        self.debug = debug
        # Selenium操作句柄
        self.api = driver
        # 设置默认的全局等待时长
        self.wait = WebDriverWait(self.api, 5)
        # 业务名 用于debug模式下标记控制台的信息输出
        self.business_name = business_name
        # 完整图形和缺口图形文件路径
        self.full_img_path = full_img_path if full_img_path else f"full_img_path_{time.time()}.png"
        self.notch_img_path = notch_img_path if notch_img_path else f"notch_img_path_{time.time()}.png"
        # 像素相似度阈值 用于粗糙地比对两张size一致的图形的相同像素坐标下的RGBA残差
        self.threshold: int = 60
        # 偏置起点 拼图在x轴上的像素体积
        self.offset: int = 35
        # 缓存物理算子的运动终点坐标（计算值而非真实值）
        self.boundary = self.offset
        # 滑块对象初始化
        self.slider = None
        # 滑块轨迹初始化
        self.track: list = []

    def activate_validator(self):
        """
        唤醒验证 若无需唤醒则pass
        :return:
        """
        pass

    def capture_slider(self, xpath: str = None, class_name: str = None):
        if xpath:
            self.slider = self.wait.until(
                ec.element_to_be_clickable((By.XPATH, xpath))
            )
        elif class_name:
            self.slider = self.wait.until(
                ec.element_to_be_clickable((By.CLASS_NAME, class_name))
            )

    def capture_full_img(self):
        """
        # 获取完整的截图并存储
        :return:
        """
        pass

    def capture_notch_img(self):
        """
        # 获取缺口截图并存储
        :return:
        """
        pass

    @staticmethod
    def generate_track(solution, phys_params) -> list:
        if callable(solution):
            return solution(phys_params)

    def operator_sport_v1(self, phys_params) -> tuple:
        """
        计算方案1：根据匀变速直线运动公式生成物理算子运动轨迹
        :return: 生成一维坐标的运动轨迹
        """
        # 运动终点坐标
        boundary = phys_params['boundary']
        # 轨迹树
        track = []
        # 物理算子当前所在的一维空间位置
        current_coordinate = phys_params.get("current_coordinate") if phys_params.get("current_coordinate") else 0
        # 切割变加速度的边界距离
        mid = phys_params.get("mid") if phys_params.get("mid") else boundary * 3.2 / 4
        # 运动时间（采样间隔）越高则单步位移提升越大，任务耗时降低，但误差增大
        t = phys_params.get("t") if phys_params.get("t") else 1.
        # 运动初速度为0
        v = 0
        # 当算子还未抵达终点时，持续生成下一步坐标
        alpha_factor = phys_params.get("alpha_factor") if phys_params.get("alpha_factor") else 1.8712
        beta_factor = phys_params.get("beta_factor") if phys_params.get("beta_factor") else 1.912
        while current_coordinate < boundary:
            # 当算子处于“距离中点”前时加速，越过后减速
            if current_coordinate < mid:
                a = random.uniform(alpha_factor, beta_factor)
            else:
                a = -random.uniform(0.11, 0.13)
            v0 = v
            v = v0 + a * t
            # move 是每一步的位移
            move = v0 * t + 1 / 2 * a * t * t
            current_coordinate += move
            track.append(int(move))
        if self.debug:
            print(f">>> displacement: {sum(track)}, boundary: {boundary}, position: {sum(track) - boundary}")
        # 返回算子运动轨迹
        return track, sum(track) - boundary

    def operator_sport_v2(self):
        """
        计算方案2：借鉴Momentum动量收敛思想，生成包含“混频震荡”“累积速度”等行为的物理算子运动轨迹
        :return:
        """

        pass

    def operator_sport_v3(self):
        """
        计算方案3：使用强化学习暴力破解，生成拟人化的物理算子运动轨迹
        :return:
        """
        pass

    def identify_boundary(self, full_img_path, notch_img_path, offset: int = 35):
        """
        获取缺口偏移量
        :param full_img_path: 不带缺口图片路径
        :param notch_img_path: 带缺口图片路径
        :param offset: 偏移量， 默认 35
        :return:
        """
        # 1.读取完整背景图与残缺背景图
        # 完整背景图与残缺背景图的边长参数一致
        full_img, notch_img = Image.open(full_img_path), Image.open(notch_img_path)

        # 2.遍历ImageObject图片对象的每一个像素点
        # ImageObject.size[0] 图片长度
        for i in range(offset, full_img.size[0]):
            # ImageObject.size[1] 图片宽度
            for j in range(full_img.size[1]):
                # 2.1将遍历到的像素点坐标（x,y）传到像素比对方法 is_pixel_equal() 用于找出像素明度差距较大的像素坐标集合
                if not self.is_pixel_equal(full_img, notch_img, i, j):
                    # 视此坐标点为第一个明度差值较大的像素点，既“缺口拼图”的像素临界（起）点
                    # 因为“滑块移动”是橫向移动滑块，不考虑垂直方向（y轴）坐标的影响，故此时仅返回x轴坐标，既横向坐标
                    # 将此时遍历到的坐标返回
                    self.boundary = i
                    return self.boundary

        # 2.2 此时返回的坐标点必然是错误的
        # 但为了程序高效运行，需要返回一个符合参数格式的变量
        return self.boundary

    def is_pixel_equal(self, img1, img2, x, y):
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]

        if (abs(pix1[0] - pix2[0] < self.threshold) and abs(pix1[1] - pix2[1] < self.threshold) and abs(
                pix1[2] - pix2[2] < self.threshold)):
            return True
        return False

    def check_boundary(self, boundary):
        """
        测试缺口识别算法精确度，根据full-notch色域残差计算得出的边界坐标boundary，
        在notch图上做出一条垂直线段，用于对比“边界”真实值与计算值的差距
        :return:
        """
        text_size = 14
        text_font = "arialbi.ttf"
        line_width = 1
        # 打开文件对象
        boundary_notch = Image.open(self.notch_img_path)
        # 打开作图句柄
        draw = ImageDraw.Draw(boundary_notch)
        # 标识边界线（计算值）
        draw.line((boundary, 0, boundary, boundary_notch.size[1]), fill=(30, 255, 12), width=line_width)
        # 标识边界线x轴坐标
        ft = ImageFont.truetype(text_font, size=text_size)
        draw.text((boundary + line_width, 10), f"x = ({boundary}, )", fill=(255, 0, 0), font=ft)
        # 显示图片
        boundary_notch.show()

    @staticmethod
    def de_dark(x, halt):
        time.sleep(halt)
        return x, abs(round(x / halt, 2))

    @staticmethod
    def shock(step_num: int = 9, alpha=0.3, beta=0.5):
        pending_step = []
        for _ in range(step_num):
            correct_step = random.choice([-1, 0, 0, 1])
            if correct_step == 0 and random.uniform(0, 1) > alpha:
                if random.uniform(0, 1) <= beta:
                    correct_step = 1
                else:
                    correct_step = -1
            pending_step.append(correct_step)
        return pending_step

    def drag_slider(
            self, track, slider, position: int, boundary: int,
            use_imitate=True,
            is_hold=False,
            momentum_convergence=False
    ):
        """

        :param position: 滑块走完轨迹后与boundary预测值的相对位置，position > 0在右边，反之在左边
        :param is_hold: 是否已拖住滑块，用于兼容不同的验证触发方式
        :param boundary:
        :param slider:
        :param track:
        :param use_imitate:仿生旋转。对抗geetest-v3务必开启。
            百次实验中，当识别率为100%时，对抗成功率92%。
        :param momentum_convergence: 动量收敛。对抗geetest-v2务必开启。
            百次实验中，当识别率为100%时，对抗成功率99%。仅当boundary ~= 48（拼图遮挡）时失效。
        :return:
        """
        # ====================================
        # 参数转换与清洗
        # ====================================
        # float -> int
        if not isinstance(position, int):
            position = int(position)
        # 重定向滑块对象
        if is_hold:
            pass
        else:
            time.sleep(0.5)
            ActionChains(self.api).click_and_hold(slider).perform()
        # 震荡收敛步伐初始化
        catwalk = []
        # 参数表
        debugger_map = {'position': position, }
        # ====================================
        # 执行核心逻辑
        # ====================================
        # step1: 根据轨迹拖动滑块，使滑块逼近boundary附近
        for step in track:
            ActionChains(self.api).move_by_offset(xoffset=step, yoffset=0).perform()
        # step2.1: operator于一维空间中的位置回衡 基于仿生学
        if use_imitate:
            step_num = 9
            # 拼图与boundary重合 -> 震荡收敛
            if position == 0:
                catwalk = self.shock(step_num=step_num, alpha=0.3, beta=0.5)
                # 执行步态
                for step in catwalk:
                    ActionChains(self.api).move_by_offset(xoffset=step, yoffset=0).perform()
                # 姿态回衡
                if abs(sum(catwalk)) >= int(step_num / 2):
                    ActionChains(self.api).move_by_offset(xoffset=-sum(catwalk) + 1, yoffset=0).perform()
            else:
                if position > 0:
                    # 拼图位于boundary右方 -> 回落
                    # 修正后落于区间 ∈ [-2,1,2,3,4,5,6]
                    emergency_braking = -int((position / 2)) if -int((position / 2)) != 0 else -2
                else:
                    # 拼图位于boundary左方 -> 补偿
                    # 修正后落于区间 ∈ [3, 4, 5, 6, 7...]
                    emergency_braking = abs(position) + 2

                # 向左抖动
                pending_step = self.shock(step_num=step_num, alpha=0.3, beta=0.2)

                # 一级步态修正
                ActionChains(self.api).move_by_offset(xoffset=emergency_braking, yoffset=0).perform()
                catwalk.append(emergency_braking)
                for step in pending_step:
                    if random.uniform(0, 1) < 0.2:
                        time.sleep(0.5)
                    ActionChains(self.api).move_by_offset(xoffset=step, yoffset=0).perform()
                    catwalk.append(step)

                # 二级步态修正
                stance = sum(catwalk) + position
                while abs(stance) > 3 and position != 0:
                    # 踏出对抗步伐
                    step = - (position / abs(position))
                    ActionChains(self.api).move_by_offset(xoffset=step, yoffset=0).perform()
                    # 更新参数
                    catwalk.append(step)
                    position += step
                    stance = sum(catwalk) + position
            debugger_map.update({'catwalk': catwalk})
        # step2.2: operator于一维空间中的位置回衡 基于极限收敛
        if momentum_convergence:
            # 通过强化学习拟合出的收敛区间
            convergence_region = list(range(-9, -2))
            low_confidence_region = list(range(47, 52))
            # 补偿算子初始化，作为momentum收敛后的单步步长回衡姿态
            inertial = 0
            # 当算子处于低置信度空间内，使用手工调平的方法回衡
            # 当boundary落在此区间内时，缺口识别有极大概率出现偏差，使用手工调平的方法回衡姿态
            # 若出现遮挡，回衡成功率较高
            # 若识别错误，回衡成功率必然为0
            if boundary in low_confidence_region:
                if abs(position) < 1.1:
                    inertial = random.randint(-5, -2)
                elif abs(position) <= 5:
                    inertial = random.randint(-8, -5)
                else:
                    inertial = -8
            # 当算子处于收敛空间外时，使用运动补偿的方法回落姿态
            elif position not in convergence_region:
                if position < convergence_region[0]:
                    inertial = random.randint(convergence_region[0] - position, convergence_region[-1] - position)
                else:
                    inertial = -random.randint(position - convergence_region[-1], position - convergence_region[0])
            # 将补偿算子inertial作为单步像素距离移动
            ActionChains(self.api).move_by_offset(xoffset=inertial, yoffset=0).perform()
            debugger_map.update({'inertial': inertial})
        # 打印参数表
        if self.debug:
            print(f"{self.business_name}: {debugger_map}")
        # 松开滑块 统计通过率
        ActionChains(self.api).release(slider).perform()
        time.sleep(1.5)
        return debugger_map

    def is_try_again(self):
        """

        :return:
        """

        # v3
        button_text = self.api.find_element_by_class_name('geetest_radar_tip_content')
        text = button_text.text
        if text in ("尝试过多", "网络不给力", "请点击重试"):
            button = self.api.find_element_by_class_name('geetest_reset_tip_content')
            button.click()

    def is_success(self):
        """

        :return:
        """
        pass

    def run(self):
        """
        The reference logic flow is as follows
        :return:
        """
        # Change the execution order appropriately according to the specific situation.
        # 1. EC.Presence_of_all_elements_located.
        # 2. Get the slider object.
        # 3. Get a complete screenshot.
        # 4. Activate GeeTest.
        # 5. Get a screenshot of the gap.

        # It is recommended to execute in order.
        # 6. Identify the coordinates of the left boundary of the gap.
        # ~(Visual recognition results in debug mode.)
        # 7. Generate the trajectory of the physical operator.
        # 8. Drag the slider.
        # 9. Determine whether the execution is successful and return the relevant bool signal.
