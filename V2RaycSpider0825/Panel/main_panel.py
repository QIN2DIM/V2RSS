import easygui
import threading
from Panel import GUI_Panel, all_airPort, NetCheck_panel
from config import *

# 主菜单
home_list = ['[1]查看机场生态', '[2]获取订阅链接', '[3]检查网络状态', '[4]检查版本更新', '[5]退出', ]


# 程序入口,所有初始化设置函数请在此编写
class PrepareENV(object):
    """环境初始化检测"""

    @staticmethod
    def init_user_agent():
        """
        将伪装请求头文件写入系统缓存，不执行该初始化步骤 fake-useragent库将发生致命错误
        :return:
        """
        import tempfile
        # fake_useragent json file name
        fup = 'fake_useragent_0.1.11.json'
        if fup not in os.listdir(tempfile.gettempdir()):
            os.system('copy {} {}'.format(
                os.path.join(ROOT_DATABASE, fup),
                os.path.join(tempfile.gettempdir(), fup)
            ))
            easygui.exceptionbox('>>> 环境初始化成功,正在尝试重启脚本', TITLE)
            try:
                os.system('python {}'.format(os.path.join(ROOT_PROJECT_PATH, 'main.py')))
                sys.exit()
            except OSError:
                easygui.exceptionbox('查找失败，请手动重启脚本', TITLE)

    @staticmethod
    def init_service_info():
        """检查服务器书写是否正确"""
        msg = """
        >>> ECS_HOSTNAME:{}\n
        >>> ECS_PORT:{}\n
        >>> ECS_PASSWORD:{}\n
        >>> ECS_USERNAME:{}\n""".format(ECS_HOSTNAME, ECS_PORT, ECS_PASSWORD, ECS_USERNAME)
        if ECS_HOSTNAME == '':
            easygui.textbox('\n系统监测到您config.py服务器配置异常'
                            '\n\n当hostname为空时,默认启动本地采集', TITLE, msg, codebox=True)

    def run_start(self, init=False):
        if init is True:
            self.init_user_agent()
            self.init_service_info()


class HomePanel(object):

    def start(self, init=False):
        # 环境初始化
        self.prepare(init)

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
            resp = False
        finally:
            if resp:
                self.start()
            else:
                sys.exit()

    @staticmethod
    def prepare(init=True):
        """环境初始化"""
        pe = PrepareENV()
        pe.run_start(init=init)

    @staticmethod
    def kill(info):
        try:
            easygui.exceptionbox(info, TITLE)
            # os.remove(cash_fp)
        except FileNotFoundError:
            pass
