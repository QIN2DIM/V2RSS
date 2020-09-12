import easygui
import os
import threading
from Panel import GUI_Panel, all_airPort, NetCheck_panel
from Panel.reball import cash_fp

home_list = ['[1]查看机场生态', '[2]获取订阅链接', '[3]检查网络状态', '[4]检查版本更新', '[5]退出', ]


class HomePanel(object):

    def start(self, ):
        usr_c = easygui.choicebox('功能列表', 'V2Ray云彩姬', home_list, preselect=1)
        try:
            if '[1]' in usr_c:
                all_airPort.sAirportSpider()
            elif '[2]' in usr_c:
                GUI_Panel.SSRcS_panel()
            elif '检查网络' in usr_c:
                threading.Thread(target=NetCheck_panel.getReport, ).start()
                easygui.ynbox('正在审查网络环境', 'V2Ray云彩姬')
                self.start()
            elif '更新' in usr_c:
                easygui.textbox("封测阶段暂不开放联网更新接口！", title='V2Ray云彩姬')
                self.start()
            else:
                pass
        except TypeError:
            pass
        finally:
            try:
                with open(cash_fp, 'r', encoding='utf-8') as f:
                    if '返回' in f.read():
                        self.start()
                    elif '退出' in f.read():
                        pass
            except FileNotFoundError:
                pass

    @staticmethod
    def kill():
        try:
            os.remove(cash_fp)
        except FileNotFoundError:
            pass
