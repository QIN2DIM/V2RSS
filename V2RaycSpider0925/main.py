from Panel.master_panel import *

"""欢迎使用V2Ray云彩姬"""
if __name__ == '__main__':
    vmp = V2RaycSpider_Master_Panel()
    try:
        vmp.home_menu()
    except Exception as e:
        vmp.kill(e)
