__all__ = ['send_email', 'sever_chan']

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from typing import List

from config import SMTP_ACCOUNT, SERVER_CHAN_SCKEY, logger, SERVER_DIR_DATABASE_LOG


# 邮件发送模块
def send_email(msg, to_: List[str] or str or set, headers: str = None):
    """
    发送运维信息，该函数仅用于发送简单文本信息
    :param msg: 正文内容
    :param to_: 发送对象
                1. str
                    to_ == 'self'，发送给“自己”
                2. List[str]
                    传入邮箱列表，群发邮件（内容相同）。
    :param headers:
    :@todo 加入日志读取功能（open file）以及富文本信息功能（html邮件）
    :return: 默认为'<V2Ray云彩姬>运维日志'
    """
    headers = headers if headers else '<V2Ray云彩姬>运维日志'
    sender = SMTP_ACCOUNT.get('email')
    password = SMTP_ACCOUNT.get('sid')
    smtp_server = 'smtp.qq.com'
    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header('ARAI.DM', 'utf-8')  # 发送者
    message['Subject'] = Header(f"{headers}", 'utf-8')
    server = smtplib.SMTP_SSL(smtp_server, 465)

    # 输入转换
    if to_ == 'self':
        to_ = set(sender, )
    if isinstance(to_, str):
        to_ = [to_, ]
    if isinstance(to_, list):
        to_ = set(to_)
    if not isinstance(to_, set):
        return False

    try:
        server.login(sender, password)
        for to in to_:
            try:
                message['To'] = Header(to, 'utf-8')  # 接收者
                server.sendmail(sender, to, message.as_string())
                logger.success("发送成功->{}".format(to))
            except smtplib.SMTPRecipientsRefused:
                logger.warning('邮箱填写错误或不存在->{}'.format(to))
            except Exception as e:
                logger.error('>>> 发送失败 || {}'.format(e))
    finally:
        server.quit()


def sever_chan(title: str = None, message: str = None) -> bool:
    """
    调用SERVER酱微信提示
    @param title: 标题最大256
    @param message: 正文，支持markdown，最大64kb
    @return:
    """
    if not isinstance(title, str) or not isinstance(message, str):
        return False

    import requests

    url = f"http://sc.ftqq.com/{SERVER_CHAN_SCKEY}.send"
    params = {
        'text': title,
        'desp': message
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        if res.status_code == 200 and res.json().get("errmsg") == 'success':
            logger.success("Server酱设备通知已发送~")
            return True
    except requests.exceptions.HTTPError:
        err_ = "Server酱404！！！可能原因为您的SCKEY未填写或已重置，请访问 http://sc.ftqq.com/3.version 查看解决方案\n" \
               "工作流将保存此漏洞数据至error.log 并继续运行，希望您常来看看……"
        logger.error(err_)
        send_email(err_, to_='self')


def load_recent_log(mod: str = 'default', log_path: str = None):
    """

    @param mod: 读取模式，‘default’：读取最近12小时的运行日志（runtime）
    @param log_path: 日志路径
    @return:
    """
    import os
    if log_path is None:
        log_path = os.path.join(SERVER_DIR_DATABASE_LOG, 'runtime.log')

    with open(log_path, 'r', encoding='utf-8') as f:
        data = f.read()

    return data


if __name__ == '__main__':
    sever_chan("主人服务器又挂掉啦", '以下是保留的日志数据\n' + load_recent_log())
