# -*- coding: utf-8 -*-
# Time       : 2021/7/29 3:48
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
# > 调研笔记 Updated on <2020/11/20>
#     1. 基于[STAFF架构]生产的机场特征
#     （1）常见反爬虫形式：极验滑动验证、EmailToken
#     （2）订阅链接规律：
#         A.https://SLD/link/{userToken}?sub={subscribeType}
#             a. userToken: 账号唯一UUID（可通过账户管理页面refresh token）
#             b. subscribe Type:
#                 1:ssr  3:v2ray
#         B. https://SLD/link{userToken}?list={specialType}
#             special Type: Quantumult,Surge ...
#     2. 收费套餐-节点质量建模规则
#     3. ...
from .actions import *
from .actions import __entropy__
