import easygui
import socket

report = ''


def getReport():
    global report
    report = checker()
    easygui.msgbox(report, 'V2Ray云彩姬', )


def isNetChainOK(test_server):
    """

    :param test_server: tuple('ip or domain name', port)
    :return:
    """
    s = socket.socket()
    s.settimeout(2)
    try:
        status = s.connect_ex(test_server)
        if status == 0:
            s.close()
            return True
        else:
            return False
    except Exception as e:
        return False


def checker():
    global report
    test_list = {
        'google': ('www.google.com', 443),
        'baidu' : ('www.baidu.com', 443)
    }

    PROXY_status = isNetChainOK(test_list['google'])
    PAC_status = isNetChainOK(test_list['baidu'])
    Evaluation = ''
    if PAC_status is True and PROXY_status is False:
        Evaluation = '当前网络状态良好, 网络代理未开启'
    elif PAC_status and PROXY_status is True:
        Evaluation = '网络状态极佳, 代理服务运行正常'
    else:
        Evaluation = '当前网络环境较差，且网络代理运行异常'

    report = ">>> www.google.com, 443, {}\n>>> www.baidu.com, 443, {}\n>>> {}" \
             "".format(str(PROXY_status), str(PAC_status), Evaluation)

    return report
