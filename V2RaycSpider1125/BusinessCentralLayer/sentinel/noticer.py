__all__ = ['send_email', 'sever_chan']

from config import SMTP_ACCOUNT, SERVER_CHAN_SCKEY, SERVER_DIR_DATABASE_LOG, logger


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
        logger.error("Server酱404！！！可能原因为您的SCKEY未填写或已重置，请访问 http://sc.ftqq.com/3.version 查看解决方案")
        logger.debug('工作流将保存此漏洞数据至error.log 并继续运行，希望您常来看看……')


if __name__ == '__main__':
    sever_chan("主人服务器又挂掉啦", '以下是保留的日志数据\n')
