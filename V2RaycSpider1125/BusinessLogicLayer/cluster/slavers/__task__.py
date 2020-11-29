__all__ = ['loads_task']
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

# TODO 替换<并行伸缩>执行方案
# Master-slavers ID
slaver = 'Action{}'

task_trojan = [
    # 对抗模块未开发，请不要再生产环境中运行（极低收益）
    # slavers.format('JiSuMax'),  # IP封禁
]

task_ssr = [

    # 无阻碍
    slaver.format('ZuiSuCloud'),
    slaver.format('TheSSR'),
    slaver.format('N95Cloud'),

    # 中风险高收益
    slaver.format('ReCloud'),  # 需要滑动验证
    slaver.format('MxCloud'),  # 需要滑动验证
    slaver.format('WgCloud'),  # 需要滑动验证 仅开放V2ray -->10.15新用户 153days 会员 20G流量<--

    # 对抗模块未开发，禁止运行
    # slavers.format('XjCloud')  # 需要邮箱验证；
]

task_v2ray = [

    # 仅开放v2ray
    slaver.format('UfoCloud'),
    slaver.format('JfCloud'),

    # 无阻碍
    slaver.format('ZuiSuCloud'),
    slaver.format('TheSSR'),
    slaver.format('N95Cloud'),

    # 中风险高收益
    slaver.format('ReCloud'),  # 需要滑动验证
    slaver.format('MxCloud'),  # 需要滑动验证

]


# Dynamic loading method but not coroutine solution
# TODO :enjoy coroutine ->
def loads_task(type_: str = '', use_plugin: bool = False):
    """
    加载任务
    @param type_: 任务类型,必须在 crawler seq内,如 ssr,v2ray or trojan
    @param use_plugin: 使用加速插件
    @return:
    """
    # check input
    from config import CRAWLER_SEQUENCE
    if type_ not in CRAWLER_SEQUENCE or not isinstance(type_, str):
        return False

    # 缓冲队列
    _ls_pending_ = []

    # 加载任务
    for task_name in eval("task_" + type_):
        expr = f'from BusinessLogicLayer.cluster.slavers.{task_name} import {task_name}\n{task_name}().run()'
        _ls_pending_.append(expr)

    # 如果使用插件加速，则调入speed_up封装方法（异步非阻塞）
    if use_plugin:
        from BusinessCentralLayer.coroutine_engine import V2rayCloudSpiderSpeedUp, PuppetCore
        V2rayCloudSpiderSpeedUp(core=PuppetCore(), user_cluster=_ls_pending_, interface='run').run()
    # 若不是用加速，则按list顺序执行（阻塞）
    else:
        for _ls_ in _ls_pending_:
            exec(_ls_)