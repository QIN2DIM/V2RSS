# -*- coding: utf-8 -*-
# Time       : 2021/12/19 20:52
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from BusinessCentralLayer.middleware.redis_io import EntropyHeap
from BusinessCentralLayer.setting import logger
from BusinessLogicLayer.cluster.slavers.actions import __entropy__, __pending__
from BusinessLogicLayer.utils.sspanel_mining import SSPanelHostsClassifier


def update():
    """
    更新远程队列
    :return:
    """
    eh = EntropyHeap()
    eh.update(new_entropy=__entropy__)
    logger.success("<ScaffoldGuider> update remote tasks queue.")


def preview(remote: bool = False):
    """

    :param remote:
    :return:
    """
    eh = EntropyHeap()

    # 将要输出的摘要数据 <localQueue> or <remoteQueue>
    check_entropy = __entropy__ if not remote else eh.sync()

    # 当摘要数据非空时输出至控制台
    if check_entropy:
        for i, host_ in enumerate(check_entropy):
            print(f">>> [{i + 1}/{check_entropy.__len__()}]{host_['name']}")
            print(f"注入地址: {host_['register_url']}")
            print(f"存活周期: {host_['life_cycle']}天")
            print(
                f"运行参数: {', '.join([f'{j[0].lower()}={j[-1]}' for j in host_['hyper_params'].items() if j[-1]])}\n"
            )
    else:
        logger.warning("<ScaffoldGuider> empty entropy.")


@logger.catch()
def check(power: int = 16):
    """

    :param power:
    :return:
    """
    pending_actions = __entropy__ + __pending__

    urls = list({atomic["register_url"] for atomic in pending_actions})

    sug = SSPanelHostsClassifier(docker=urls, debug=False)
    sug.go(power=power)

    docker = sug.offload()
    for element in docker:
        _url = element["url"]
        _labels: list = element["label"].split(";")
        for atomic in pending_actions:
            if atomic["register_url"] != _url:
                continue
            _hyper_params = atomic["hyper_params"]
            _hypers = {
                "Email Validation": bool(_hyper_params.get("anti_email")),
                "Google reCAPTCHA": bool(_hyper_params.get("anti_recaptcha")),
                "GeeTest Validation": bool(_hyper_params.get("anti_slider"))
            }
            if "Normal" in _labels:
                if len(_labels) != 1:
                    logger.error("错误标签 - labels={}".format(_labels))
                elif True in _hypers.values():
                    logger.error("过时标签 - url={} name=[{}-->{}] label=`Normal` _hypers={} ".format(
                        _url,
                        atomic["name"],
                        "__entropy__" if atomic in __entropy__ else "__pending__",
                        {i[0]: i[-1] for i in _hypers.items()},
                    ))
                continue

            for _label in _labels:
                if _label not in _hypers.keys():
                    logger.warning("意外标签 - name={} label={} url={}".format(
                        atomic["name"], _label, _url
                    ))
                elif _hypers[_label] is False:
                    logger.error("过时标签 - url={} name=[{}-->{}] label=`Normal` _hypers={} ".format(
                        _url,
                        atomic["name"],
                        "__entropy__" if atomic in __entropy__ else "__pending__",
                        {i[0]: i[-1] for i in _hypers.items()},
                    ))
