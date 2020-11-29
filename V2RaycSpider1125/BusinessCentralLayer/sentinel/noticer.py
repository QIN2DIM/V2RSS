__all__ = ['send_email']

from config import SMTP_ACCOUNT, logger


# 邮件发送模块
def send_email(text_body, to, headers='<V2Ray云彩姬>运维日志'):
    """
    写死管理者账号，群发邮件
    :param text_body: 正文内容
    :param to: 发送对象
    :param headers:
    :return:
    """
    # 发送邮件通知
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header

    sender = SMTP_ACCOUNT.get('email')
    password = SMTP_ACCOUNT.get('sid')
    if to == 'self':
        to = sender

    if to != '':
        message = MIMEText(text_body, 'plain', 'utf-8')
        message['From'] = Header(sender, 'utf-8')  # 发送者
        message['To'] = Header(to, 'utf-8')  # 接收者
        message['Subject'] = Header("{}".format(headers), 'utf-8')
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        try:
            server.login(sender, password)
            server.sendmail(sender, to, message.as_string())
            logger.info('发送成功')
            return True
        except smtplib.SMTPRecipientsRefused:
            logger.exception('邮箱填写错误或不存在')
            return False
        except Exception as e:
            logger.exception(e)
            return False
        finally:
            server.quit()