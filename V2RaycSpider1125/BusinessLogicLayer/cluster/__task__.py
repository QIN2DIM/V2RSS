__all__ = ['loads_task', 'step']

# 请不要随意改变层文件命名

"""
> 调研笔记 Updated on <2020/11/20>
    1. 基于[STAFF架构]生产的机场特征
    （1）常见反爬虫形式：极验滑动验证、EmailToken
    （2）订阅链接规律：
        A.https://SLD/link/{userToken}?sub={subscribeType}
            a. userToken: 账号唯一UUID（可通过账户管理页面refresh token）
            b. subscribe Type: 
                1:ssr  3:v2ray
        B. https://SLD/link{userToken}?list={specialType}
            special Type: Quantumult,Surge ...
    2. 收费套餐-节点质量建模规则
    3. ...
"""

# Master-slavers ID
slaver = 'Action{}'

task_trojan = [
    # 对抗模块未开发，请不要再生产环境中运行（极低收益）
    # slavers.format('JiSuMax'),  # IP封禁
]

task_ssr = [

    # 无阻碍
    # slaver.format('ZuiSuCloud'),
    # slaver.format('TheSSR'),
    # slaver.format('N95Cloud'),

    # 中风险高收益
    # slaver.format('ReCloud'),  # 需要滑动验证
    # slaver.format('MxCloud'),  # 需要滑动验证 DDOS
    # slaver.format('WgCloud'),  # 需要滑动验证 仅开放V2ray -->10.15新用户 153days 会员 20G流量<--
    #
    # # 对抗模块未开发，禁止运行
    # # slavers.format('XjCloud')  # 需要邮箱验证；
]

task_v2ray = [

    # 仅开放v2ray
    # slaver.format('UfoCloud'),
    # slaver.format('JfCloud'),

    # 无阻碍
    # slaver.format('ZuiSuCloud'),
    # slaver.format('TheSSR'),
    # slaver.format('N95Cloud'),

    # 中风险高收益
    # slaver.format('ReCloud'),  # 需要滑动验证
    # slaver.format('MxCloud'),  # 需要滑动验证

]

from BusinessCentralLayer.coroutine_engine import vsu, PuppetCore
from BusinessCentralLayer.middleware.work_io import *


def read_actions():
    from BusinessLogicLayer.cluster.slavers import actions
    for class_ in CRAWLER_SEQUENCE:
        for slaver_ in actions.__all__:
            exec(f"if actions.{slaver_}().hyper_params[class_]:\n\t"
                 f"task_{class_}.append(slaver_)")


def loads_task(class_: str = '', use_plugin: bool = False, one_step=False, startup=True, loads_=True) -> bool:
    """
    加载任务
    @param loads_:
    @param startup:
    @param one_step:
    @param class_: 任务类型,必须在 crawler seq内,如 ssr,v2ray or trojan
    @param use_plugin: 使用加速插件
    @return:
    """

    # 检查输入
    if class_ not in CRAWLER_SEQUENCE or not isinstance(class_, str):
        return False

    # 加载任务
    if loads_:

        # 刷新节点
        read_actions()

        # 乱序入队
        exec("import random\nrandom.shuffle(eval('task_' + class_))")
        for task_name in eval("task_" + class_):
            expr = f'from BusinessLogicLayer.cluster.slavers.actions import {task_name}\n{task_name}().run()'
            Middleware.poseidon.put_nowait(expr)
            if one_step:
                break

    # 启动任务
    if startup:
        # 如果使用插件加速，则调入speed_up封装方法
        # 否则按list顺序执行
        vsu(core=PuppetCore(), docker=Middleware.poseidon).run(use_plugin)

    return True


def step(class_: str = '') -> bool:
    if class_ not in CRAWLER_SEQUENCE or not isinstance(class_, str):
        return False
    else:
        exec("import random\nrandom.shuffle(eval('task_' + class_))")

        task_name = eval("task_" + class_).pop()

        expr = f'from BusinessLogicLayer.cluster.slavers.{task_name} import {task_name}\n{task_name}().run()'

        Middleware.poseidon.put_nowait(expr)

        return True
