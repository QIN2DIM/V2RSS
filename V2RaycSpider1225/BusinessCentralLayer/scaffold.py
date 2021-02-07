__all__ = ['scaffold']

from gevent import monkey

monkey.patch_all()
import csv
import gevent
from typing import List

from BusinessCentralLayer.setting import *

command_set = {

    # ---------------------------------------------
    # 部署接口
    # ---------------------------------------------
    'deploy': "部署项目（定时任务/Flask 开启与否根据yaml配置文件）",
    # ---------------------------------------------
    # 调试接口
    # ---------------------------------------------
    "decouple": "立即唤醒一次subs_ddt链接解耦任务",
    "overdue": "立即执行一次过时链接清洗任务",
    "run": "立即执行一次采集任务（强制使用协程加速）",
    "force_run": "强制执行采集任务",
    "remain": "读取剩余订阅数量",
    "ping": "测试数据库连接",
    # ---------------------------------------------
    # 调用示例
    # ---------------------------------------------
    "example": "python main.py ping"
}


class _ConfigQuarantine(object):
    def __init__(self):

        self.root = [
            SERVER_DIR_CLIENT_DEPORT, SERVER_PATH_DEPOT_VCS,
            SERVER_DIR_DATABASE_CACHE, SERVER_DIR_CACHE_BGPIC
        ]
        self.flag = False

    def set_up_file_tree(self, root):
        """
        --/qinse/V2RaycSpider{verNum}
            --BCL
            --BLL
            --BVL
            --Database
                --client_depot
                    --vcs.csv
                --logs
                    --*error.log
                    --*runtime.log
                --temp_cache
                    --*AnyTempCacheFile...
                --*CrawlFetchHistory.txt
                --fake_useragent_0.1.11.json
            --*tests
        """

        # 检查默认下载地址是否残缺 深度优先初始化系统文件
        for child_ in root:
            if not os.path.exists(child_):
                self.flag = True
                try:
                    # 初始化文件夹
                    if os.path.isdir(child_) or not os.path.splitext(child_)[-1]:
                        os.mkdir(child_)
                        logger.success(f"系统文件链接成功->{child_}")
                    # 初始化文件
                    else:
                        if child_ == SERVER_PATH_DEPOT_VCS:
                            try:
                                with open(child_, 'w', encoding='utf-8', newline='') as fpx:
                                    csv.writer(fpx).writerow(['version', 'title'])
                                logger.success(f"系统文件链接成功->{child_}")
                            except Exception as ep:
                                logger.exception(f"Exception{child_}{ep}")
                except Exception as ep:
                    logger.exception(ep)

    @staticmethod
    def check_config():
        if not all(SMTP_ACCOUNT.values()):
            logger.warning('您未正确配置<通信邮箱>信息(SMTP_ACCOUNT)')
        if not SERVER_CHAN_SCKEY:
            logger.warning("您未正确配置<Server酱>的SCKEY")
        if not all([REDIS_SLAVER_DDT.get("host"), REDIS_SLAVER_DDT.get("password")]):
            logger.warning('您未正确配置<Redis-Slave> 本项目的部分功能将毫无意义')
        if not all([REDIS_MASTER.get("host"), REDIS_MASTER.get("password")]):
            logger.error("您未正确配置<Redis-Master> 此配置为“云彩姬”的核心组件，请配置后重启项目！")
            exit()

    def run(self):
        try:
            if [cq for cq in reversed(self.root) if not os.path.exists(cq)]:
                logger.warning('系统文件残缺！')
                logger.debug("启动<工程重构>模块...")
                self.set_up_file_tree(self.root)
            self.check_config()

        finally:
            if self.flag:
                logger.success(">>> 运行环境链接完成，请重启项目")
                logger.warning(">>> 提醒您正确配置Chrome及对应版本的ChromeDriver")
                exec("if self.flag:\n\texit()")


_ConfigQuarantine().run()


class _ScaffoldGuider(object):
    # __slots__ = list(command_set.keys())

    def __init__(self):
        # 脚手架公开接口
        self.scaffold_ruler = [i for i in self.__dir__() if i.startswith('_scaffold_')]

    @logger.catch()
    def startup(self, driver_command_set: List[str]):
        """
        仅支持单进程使用
        @param driver_command_set: 在空指令时列表仅有1个元素，表示启动路径
        @return:
        """
        # logger.info(f">>> {' '.join(driver_command_set)}")

        # -------------------------------
        # TODO 优先级0：预处理指令集
        # -------------------------------
        # CommandId or List[CommandId]
        driver_command: List[str] = []

        # 未输入任何指令 列出脚手架简介
        if len(driver_command_set) == 1:
            print("\n".join([f">>> {menu[0].ljust(20, '-')}|| {menu[-1]}" for menu in command_set.items()]))
            return True
        # 输入立即指令 转译指令
        elif len(driver_command_set) == 2:
            driver_command = [driver_command_set[-1].lower(), ]
        # 输入指令集 转译指令集
        elif len(driver_command_set) > 2:
            driver_command = list(set([command.lower() for command in driver_command_set[1:]]))

        # 捕获意料之外的情况
        if not isinstance(driver_command, list):
            return True
        # -------------------------------
        # TODO 优先级1：解析运行参数
        # -------------------------------

        # TODO --help 帮助菜单（继续完善相关功能）
        # 使用该参数时系统不解析运行指令
        if '--help' in driver_command:
            logger.info(f">>>GuiderHelp || 帮助菜单")
            driver_command.remove("--help")
            for command_ in driver_command:
                introduction = command_set.get(command_)
                if introduction:
                    print(f"> {command_.ljust(20, '-')}|| {introduction}")
                else:
                    print(f"> {command_}指令不存在")
            return True

        # -------------------------------
        # TODO 优先级2：运行单线程指令
        # -------------------------------

        # 协程任务队列
        task_list = []

        # 测试数据库连接
        while driver_command.__len__() > 0:
            _pending_command = driver_command.pop()
            try:
                task_list.append(gevent.spawn(eval(f"self._scaffold_{_pending_command}")))
            except Exception as e:
                logger.warning(f'脚手架暂未授权指令<{_pending_command}> {e}')
        else:
            # 并发执行以上指令
            gevent.joinall(task_list)

        # -------------------------------
        # TODO 优先级3：自定义参数部署（阻塞线程）
        # -------------------------------

        if 'deploy' in driver_command:
            self._scaffold_deploy()

    @staticmethod
    def _scaffold_deploy():
        logger.info(f"<ScaffoldGuider> Deploy || MainProcess")
        from BusinessCentralLayer.middleware.interface_io import SystemInterface as app
        app.run(deploy_=True)

    @staticmethod
    def _scaffold_decouple():
        logger.info(f"<ScaffoldGuider> Decouple || General startup")

        from BusinessLogicLayer.plugins.ddt_subs import SubscribesCleaner
        SubscribesCleaner(debug=True).interface()

    @staticmethod
    def _scaffold_overdue():
        logger.info(f"<ScaffoldGuider> Overdue || Redis DDT")
        from BusinessCentralLayer.middleware.interface_io import SystemInterface as app
        app.ddt()

    @staticmethod
    def _scaffold_run():
        logger.info(f"<ScaffoldGuider> Run || MainCollector")
        from BusinessCentralLayer.middleware.interface_io import SystemInterface as app
        app.run(deploy_=False)

    @staticmethod
    def _scaffold_force_run():
        logger.info(f"<ScaffoldGuider> ForceRun || MainCollector")
        from BusinessCentralLayer.middleware.interface_io import SystemInterface as app
        app.run(deploy_=False, force_run=True)

    @staticmethod
    def _scaffold_remain():
        from BusinessCentralLayer.middleware.redis_io import RedisClient
        logger.info(f"<ScaffoldGuider> Remain || {RedisClient().subs_info()}")

    @staticmethod
    def _scaffold_ping():
        from BusinessCentralLayer.middleware.redis_io import RedisClient
        logger.info(f"<ScaffoldGuider> Ping || {RedisClient().test()}")


scaffold = _ScaffoldGuider()
if __name__ == '__main__':
    print(scaffold.scaffold_ruler)
