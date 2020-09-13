# TODO:垂直挖掘STAFF机场
from gevent import monkey

monkey.patch_all()

import gevent
from gevent.queue import Queue
from spiderNest.preIntro import *

target_Q = Queue()
response_Q = Queue()
dataList = []


class sAirportSpider(object):
    def __init__(self):

        # 白嫖首页
        self.airHome = 'https://52bp.org'

    def get_vip_link(self):
        return self.slaver(self.airHome + '/vip-airport.html', 'url')

    def get_free_link(self):
        return self.slaver(self.airHome + '/free-airport.html', 'url')

    def get_all_link(self):
        return self.slaver(self.airHome + '/airport.html', 'url')

    @staticmethod
    def get_sAirHome(mode):
        raw_linkList = [i for i in mode if "#" not in i]
        sAirport_HomeList = []
        for i in raw_linkList:
            if 'register' in i:
                home_link = i[:-13]
                sAirport_HomeList.append(home_link)
            else:
                sAirport_HomeList.append(i)
        return sAirport_HomeList

    @staticmethod
    def slaver(url, mode=''):

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
            global dataList
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


def Out_flow(dataFlow):
    path_ = os.path.dirname(__file__) + '/STAFF sAirport.txt'
    with open(path_, 'a', encoding='utf-8') as f:
        f.write(dataFlow)


def verity_staff():
    """

    :return:
    """
    while not target_Q.empty():
        target = target_Q.get_nowait()
        if target[-1] != '/':
            target += '/staff'
        else:
            target += 'staff'

        # 审查网络状况
        def layer():
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
                res = requests.get(target, headers=headers)
                res.raise_for_status()
                return res
            except Exception as e:
                print(e)
                # print(['x', '{}'.format(target.split('staff')[0])])
                return False

        if layer() is not False:
            code = layer().status_code
            try:
                Out_flow('{}\n'.format(target))
            finally:
                response_Q.put_nowait([target, code])
                print(['{}'.format(response_Q.qsize()), target, code])


def quick_start(TIP):
    for href in TIP:
        target_Q.put_nowait(href)

    task_list = []
    for x in range(target_Q.qsize()):
        task = gevent.spawn(verity_staff)
        task_list.append(task)
    gevent.joinall(task_list)


if __name__ == '__main__':

    sas = sAirportSpider()

    quick_start(
        sas.get_sAirHome(
            sas.get_free_link()
        )
    )
