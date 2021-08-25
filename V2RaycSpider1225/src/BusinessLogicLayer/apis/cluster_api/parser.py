# -*- coding: utf-8 -*-
# Time       : 2021/7/25 15:13
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

from .sspanel_parser import SSPanelParser


def parse_by_login(host, email, password, silence=None):
    """

    :param host:
    :param email:
    :param password:
    :param silence:
    :return:
    """
    silence = True if silence is None else silence

    return SSPanelParser(
        url=f"https://{host}/auth/login",
        silence=silence,
        assault=True,
        anti_slider=False
    ).parse_by_login(
        email=email,
        password=password
    )


def parse_by_register(host, silence=True, assault=True, anti_slider=True):
    """

    :param host:
    :param silence:
    :param assault:
    :param anti_slider:
    :return:
    """
    silence = True if silence is None else silence
    assault = True if assault is None else assault
    anti_slider = True if anti_slider is None else anti_slider

    return SSPanelParser(
        url=f"https://{host}/auth/register",
        silence=silence,
        assault=assault,
        anti_slider=anti_slider
    ).parse_by_register()
