import sys
from BusinessCentralLayer.control import Interface as app

# TODO 请在运行程序前确保已正确config.py运行参数
"""欢迎使用V2Ray云彩姬"""
if __name__ == '__main__':
    # TODO 推荐的执行方式 -> 外部传参
    #  在project根目录下执行
    #  >>> python3 main.py [args_1] [args_2]
    #  >>> python main.py [args_1] [args_2]
    #       --args_1 = deploy
    #       --args_2 = speed_up
    #  >>> 例如：python3 main.py deploy speed_up //表示 部署定时任务 + flask + 使用协程
    #  >>> 例如：python3 main.py deploy //表示 部署部署定时任务+flask 但任务执行方式为顺序执行(但节点间互不干扰)
    #  >>> 例如：python3 main.py speed_up //表示 不开启定时任务以及flask 但使用协程运行
    #  >>> 例如：python3 main.py //表示使用内置默认值
    #       --默认:deploy = True if 'linux' in platform else False
    #       --默认:coroutine_speed_up = False
    # app.run(sys.argv)

    # TODO 也可以手动传参
    # app.run(deploy_=False, coroutine_speed_up=False)

    # TODO 以开发者方式打开前端（~也许~仅Windows可用）
    app.__window__()

    # TODO 开启一次数据迁移
    # app.ddt()

    # FIXME 更多启动方案有待暴露
    ...
