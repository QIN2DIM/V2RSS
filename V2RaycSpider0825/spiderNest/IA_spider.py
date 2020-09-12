"""
机场信息聚合爬虫
"""
from lxml import etree
from spiderNest.preIntro import *

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/84.0.4147.135 Safari/537.36 ',
}

cookies = {
    'cookie': '__cfduid=da42e5b95b38e48848d0da42ff31ce09c1598338127; uid=1984; email=qinse%40gmail.com; '
              'key=6c6f13063e3ddd64ae02636917b459803369cd061072c; ip=aa816823fa6b948f96e8b73f68752641; '
              'expire_in=1598942944; pop=VIP%u9650%u65F66%u6298%u4F18%u60E0%u62A2%u8D2D%u6D3B%u52A8-%u4F18%u60E0'
              '%u7801%3A40off; pop_time=7 '
}
HOME = 'https://www.xjycloud.xyz'
USER = HOME + '/user'
NODE = HOME + 'user/node'


class IASpider(object):

    def __int__(self):
        self.cookies = ''

    def handle_html(self, url, proxy=None):
        response = requests.get(url, headers=headers, cookies=cookies, )
        # response.encoding = response.apparent_encoding
        if response.status_code == 200:
            return response.text

    def parse_html(self, url):
        html = self.handle_html(url)
        tree = etree.HTML(html, )
        return tree

    def get_v2ray_subscribed_links(self) -> str:
        """
        获取v2ray订阅连接
        """
        return self.parse_html(USER).xpath("//a[contains(@class,'v2ray')]/@data-clipboard-text")[0]

    def get_account_information(self) -> dict:
        """
        获取机场新注册账号信息
        """
        info = ''.join(self.parse_html(USER).xpath("//div[contains(@class,'wrap')]//text()")).split()
        print(info)
        info = {
            'vip' : info[1] + info[2],
            'flow': info[4] + info[5]
        }

        return info

    def run(self):
        resp = self.get_account_information()
        print(resp)


if __name__ == '__main__':
    ia = IASpider()
    ia.run()
