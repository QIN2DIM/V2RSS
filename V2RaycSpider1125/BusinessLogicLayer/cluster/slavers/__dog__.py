# TODO:垂直挖掘STAFF机场
# FIXME 该模块未完成禁止调用
from gevent import monkey

monkey.patch_all()
from os.path import join

import gevent
from gevent.queue import Queue
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

from BusinessLogicLayer.cluster.plugins import get_header

target_Q = Queue()
response_Q = Queue()
data_list = []


class sAirportSpider(object):
    def __init__(self):

        # 白嫖首页
        self.airHome = 'https://52bp.org'

    def get_vip_link(self):
        return self.run(self.airHome + '/vip-airport.html', 'url')

    def get_free_link(self):
        return self.run(self.airHome + '/free-airport.html', 'url')

    def get_all_link(self):
        return self.data_cleaning(self.run(self.airHome + '/airport.html', 'url'))

    @staticmethod
    def data_cleaning(data):

        from urllib.parse import urlparse
        if isinstance(data, str):
            data = [data, ]

        if isinstance(data, list):
            return ['{}://{}'.format(urlparse(href).scheme, urlparse(href).netloc) for href in data if "http" in href]

    @staticmethod
    def run(url, mode=''):

        # 审查网络状况
        def layer():
            try:
                headers = {'User-Agent': get_header()}
                res = requests.get(url, headers=headers)
                res.raise_for_status()
                return res.text
            except RequestException as e:
                print(e)
                return False

        # 获取导航语
        def h3Log(target):
            own = target.find_all('span', class_='fake-install_title')
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

        # 数据回流
        def regDataFlow(barSize=1):
            out_flow = [['序号', '项目名', '备注', '官网链接']]
            if barSize == 1:
                for i, x in enumerate(zip(names, hrefs)):
                    Out_item = [i + 1, list(x)[0], barInfo[0], list(x)[-1]]
                    out_flow.append(Out_item)
                return out_flow
            else:
                return out_flow

        def show_data():
            global data_list
            out_flow = ['序号    机场名    官网链接']
            for i, x in enumerate(zip(names, hrefs)):
                Out_item = '【{}】 【{}】 【{}】'.format(i + 1, list(x)[0], list(x)[-1])
                out_flow.append(Out_item)

            dataList = out_flow
            # show_response()

        response = layer()
        if response:
            soup = BeautifulSoup(response, 'html.parser')

            # 定位导航语
            barInfo = h3Log(soup)

            # 定位项目
            items = soup.find_all('li', class_='link-item')

            # 机场名
            names = [item.find('span', class_='sitename').text.strip() for item in items]

            # 获取去除邀请码的机场链接
            hrefs = [item.find('a')['href'] for item in items]
            hrefs = href_cleaner(hrefs)

            # 数据回流
            DataFlow = regDataFlow(barInfo.__len__())

            if mode == 'url':
                return hrefs


def Out_flow(dataFlow='', init=False):
    from config import SERVER_DIR_DATABASE
    if init:
        with open(join(SERVER_DIR_DATABASE, 'staff_airport.txt'), 'w', encoding='utf-8') as f:
            pass
    with open(join(SERVER_DIR_DATABASE, 'staff_airport.txt'), 'a', encoding='utf-8') as f:
        f.write(dataFlow)


def verity_staff():
    """

    :return:
    """
    while not target_Q.empty():
        target = target_Q.get_nowait()

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
            res = requests.get(target, headers=headers, timeout=5)

            code = res.status_code

            if code == 200:
                Out_flow('{}\t{}\n'.format(target, code))

            response_Q.put_nowait([target, code])

            print(['{}'.format(response_Q.qsize()), target, code])

        except RequestException:
            pass
            # print(['x', '{}'.format(target.split('staff')[0])])


def quick_start(TIP):
    for href in TIP:
        target_Q.put_nowait(href)

    task_list = []
    for x in range(target_Q.qsize()):
        task = gevent.spawn(verity_staff)
        task_list.append(task)
    gevent.joinall(task_list)


def run():
    """STAFF sAirport.txt 中导出结果，机场质量较差，v4.3.X+版本已弃用该模块。机场由人工评测筛选后录入"""
    Out_flow(init=True)

    sas = sAirportSpider()
    links = sas.get_all_link()
    quick_start(links)


if __name__ == '__main__':
    run()
