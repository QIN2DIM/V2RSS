import csv

import easygui
import requests
import webbrowser
from bs4 import BeautifulSoup

from config import *

"""*************************菜单设置*************************"""
# 菜单设置
home_list = ['[1]白嫖机场', '[2]高端机场', '[3]机场汇总', '[4]返回', '[5]退出']
func_list = ['[1]查看', '[2]保存', '[3]返回']
"""*************************INIT*************************"""


# 初始化文档树
def INIT_docTree():
    if not os.path.exists(SYS_LOCAL_fPATH):
        os.mkdir(SYS_LOCAL_fPATH)


INIT_docTree()

"""###########################################################"""


# 保存数据至本地
def out_flow(dataFlow, reFP=''):
    try:
        with open(SYS_LOCAL_aPATH, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for x in dataFlow:
                writer.writerow(x)
    except PermissionError:
        easygui.exceptionbox('系统监测到您正在占用核心文件，请解除该文件的资源占用:{}'.format(SYS_LOCAL_aPATH))


# 通过前端panel展示数据
dataList = []


def show_response():
    """

    :return:
    """
    usr_c = easygui.choicebox(msg='选中即可跳转目标网址,部分机场需要代理才能访问', title=TITLE, choices=dataList)
    if usr_c:
        if 'http' in usr_c:
            url = usr_c.split(' ')[-1][1:-1]
            webbrowser.open(url)
        else:
            easygui.msgbox('机场网址失效或操作有误', title=TITLE, ok_button='返回')
            show_response()
    elif usr_c is None:
        return 'present'


"""###########################################################"""


class sAirportSpider(object):
    def __init__(self):

        # 白嫖首页
        self.airHome = 'https://52bp.org'

        # 自启
        # self.Home()

    def Home(self):
        """GUI导航"""
        usr_c = easygui.choicebox('功能列表', TITLE, home_list, preselect=0)
        resp = True
        try:
            if '[1]' in usr_c:
                resp = self.slaver(self.airHome + '/free-airport.html', )
            elif '[2]' in usr_c:
                resp = self.slaver(self.airHome + '/vip-airport.html', )
            elif '[3]' in usr_c:
                resp = self.slaver(self.airHome + '/airport.html', )
            elif '[4]' in usr_c:
                # __retrace__('返回')
                return resp
            else:
                # __retrace__('退出')
                resp = False

        except TypeError:
            return False
        finally:
            if resp == 'present':
                return self.Home()
            else:
                return resp

    @staticmethod
    def slaver(url, ):

        # 审查网络状况
        def layer():
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
                res = requests.get(url, headers=headers)
                res.raise_for_status()
                return res.text
            except Exception as e:
                print(e)
                return False

        # 获取导航语
        def h3Log(target):
            own = target.find_all('span', class_='fake-TITLE')
            souls = []
            for soul in own:
                try:
                    soul = soul.text.split('.')[-1].strip()
                    souls.append(soul)
                except TypeError as e:
                    print(e)
            return souls

        # 清洗链接中的邀请码和注册码，返回纯净的链接
        def href_cleaner(hrefTarget, ):
            if isinstance(hrefTarget, list):
                clean_href = []
                for href in hrefs:
                    if '?' in href:
                        href = href.split('?')[0]
                        clean_href.append(href)
                    else:
                        clean_href.append(href)
                return clean_href

            elif isinstance(hrefTarget, str):
                return hrefTarget.split('?')[0]

        def show_data(show=True):
            # 使用全局变量输出前端信息
            global dataList
            Out_flow = ['序号    机场名    官网链接']

            if show:
                dataList = Out_flow + ['【{}】 【{}】 【{}】'.format(i + 1, list(x)[0], list(x)[-1]) for i, x in
                                       enumerate(zip(names, hrefs)) if 'http' in list(x)[-1]]
                # 前端展示API
                return show_response()
            else:
                return [['序号', '机场名', '官网连接'], ] + \
                       [[i + 1, list(x)[0], list(x)[-1]] for i, x in
                        enumerate(zip(names, hrefs)) if 'http' in list(x)[-1]]

        # func_list = ['[1]查看', '[2]保存', '[3]返回']
        usr_d = easygui.choicebox(title=TITLE, choices=func_list)
        if '返回' in usr_d:
            return 'present'

        response = layer()
        if response:
            soup = BeautifulSoup(response, 'html.parser')

            # 定位导航语
            # barInfo = h3Log(soup)

            # 定位项目
            items = soup.find_all('li', class_='link-item')

            # 机场名
            names = [item.find('span', class_='sitename').text.strip() for item in items]

            # 获取去除邀请码的机场链接
            hrefs = [item.find('a')['href'] for item in items]
            hrefs = href_cleaner(hrefs)

            if '保存' in usr_d:
                # 保存至本地
                out_flow(show_data(show=False))
                # 自动打开
                os.startfile(SYS_LOCAL_aPATH)
            elif '查看' in usr_d:
                # 前端打印
                return show_data()


"""###########################################################"""

if __name__ == '__main__':
    sAirportSpider()
