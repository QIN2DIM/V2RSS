import sys

import easygui
import os
import threading
from Panel import GUI_Panel, all_airPort, NetCheck_panel
from config import ROOT_DATABASE, TITLE

home_list = ['[1]查看机场生态', '[2]获取订阅链接', '[3]检查网络状态', '[4]检查版本更新', '[5]退出', ]


def INIT_USER_AGENT():
    """
    将伪装请求头文件写入系统缓存，不执行该初始化步骤 fake-useragent库将发生致命错误
    :return:
    """
    import tempfile
    if 'fake_useragent_0.1.11.json' not in os.listdir(tempfile.gettempdir()):
        os.system('copy {} {}'.format(
            ROOT_DATABASE + '/fake_useragent_0.1.11.json',
            tempfile.gettempdir() + '/fake_useragent_0.1.11.json'
        ))
        easygui.exceptionbox('>>> 环境初始化成功,请重启脚本', TITLE)
        sys.exit()


# 程序入口,所有初始化设置函数请在此编写
class HomePanel(object):

    def __int__(self):
        # 装载fake useragent
        INIT_USER_AGENT()

    def start(self, ):
        resp = True
        usr_c = easygui.choicebox('功能列表', TITLE, home_list, preselect=1)
        try:
            if '[1]' in usr_c:
                resp = all_airPort.sAirportSpider().Home()
            elif '[2]' in usr_c:
                resp = GUI_Panel.SSRcS_panel().Home()
            elif '网络' in usr_c:
                threading.Thread(target=NetCheck_panel.getReport, ).start()
                easygui.ynbox('正在审查网络环境', 'V2Ray云彩姬')
            elif '更新' in usr_c:
                easygui.textbox("封测阶段暂不开放联网更新接口！", title='V2Ray云彩姬')
            else:
                resp = False
        except TypeError:
            # 若出现未知异常，则启动垃圾回收机制，强制退出
            sys.exit()
        finally:
            if resp:
                self.start()
            else:
                sys.exit()

    @staticmethod
    def kill(info):
        try:
            easygui.exceptionbox(info, TITLE)
            # os.remove(cash_fp)
        except FileNotFoundError:
            pass
