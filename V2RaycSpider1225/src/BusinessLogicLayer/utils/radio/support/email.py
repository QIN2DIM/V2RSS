import smtplib
from email.header import Header
from email.mime.text import MIMEText
from typing import List


def send_email(msg, to_: List[str] or str or set, smtp_account: dict, headers: str = None):
    """
    发送运维信息，该函数仅用于发送简单文本信息
    :param smtp_account: {‘email’: "", 'sid': ""}
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
    sender = smtp_account.get('email')
    password = smtp_account.get('sid')
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
                message['To'] = Header(to, 'utf-8')
                server.sendmail(sender, to, message.as_string())
                # logger.success("发送成功->{}".format(to))
                return "发送成功->{}".format(to)
            except smtplib.SMTPRecipientsRefused:
                # logger.warning('邮箱填写错误或不存在->{}'.format(to))
                return '邮箱填写错误或不存在->{}'.format(to)
    finally:
        server.quit()
