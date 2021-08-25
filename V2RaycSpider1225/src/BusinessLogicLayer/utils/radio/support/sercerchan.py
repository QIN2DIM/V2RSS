def serverchan(title: str = None, message: str = None, serverchan_sckey: str = None):
    """

    :param title: 标题最大256
    :param message: 正文，支持markdown，最大64kb
    :param serverchan_sckey:
    :return:
    """
    if not isinstance(title, str) or not isinstance(message, str):
        return False

    import requests

    url = f"http://sc.ftqq.com/{serverchan_sckey}.send"
    params = {
        'text': title,
        'desp': message
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        if res.status_code == 200 and res.json().get("errmsg") == 'success':
            # logger.success("Server酱设备通知已发送~")
            return "Server酱设备通知已发送~"
    except requests.exceptions.HTTPError:
        err_ = "Server酱404！！！可能原因为您的SCKEY未填写或已重置，请访问 http://sc.ftqq.com/3.version 查看解决方案\n" \
               "工作流将保存此漏洞数据至error.log 并继续运行，希望您常来看看……"
        # logger.error(err_)
        return err_
