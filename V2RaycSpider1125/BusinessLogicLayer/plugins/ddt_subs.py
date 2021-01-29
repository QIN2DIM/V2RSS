__all__ = ['SubscribesCleaner', 'scl_deploy']

# 独立使用的链接清理插件，还未并入系统，请勿调用，正确的做法是使用单独的进程运行该脚本
import time
import schedule
from BusinessCentralLayer.coroutine_engine import lsu
from BusinessCentralLayer.middleware.redis_io import RedisClient
from BusinessLogicLayer.plugins.subs2node import subs2node
from config import REDIS_SECRET_KEY, CRAWLER_SEQUENCE, logger


class SubscribesCleaner(lsu):
    """解耦清洗插件：国内IP调用很可能出现性能滑坡"""
    def __init__(self, debug=False):
        super(SubscribesCleaner, self).__init__()
        self.debug = debug
        self.keys = [REDIS_SECRET_KEY.format(s) for s in CRAWLER_SEQUENCE]
        self.rc = RedisClient().get_driver()

    def offload_task(self):
        for key_ in self.keys:
            for sub, _ in self.rc.hgetall(key_).items():
                self.work_q.put_nowait([sub, key_])

    def control_driver(self, sub_info):
        try:
            node_info: dict = subs2node(sub_info[0], False)
            if self.debug:
                print(node_info['subs'], node_info['node'].__len__())

            if node_info['node'].__len__() <= 3:
                self.rc.hdel(sub_info[-1], sub_info[0])
                logger.debug(f'>> Detach -> {sub_info[0]}')
        except UnicodeDecodeError or TypeError as e:
            logger.debug(f"Retry put the subscribe({sub_info}) to work queue -- {e}")
            self.work_q.put_nowait(sub_info)
        except Exception as e:
            logger.warning(f"{sub_info} -- {e}")


def scl_deploy(docker=SubscribesCleaner):
    """

    @param docker: Python 类对象
    @return:
    """
    logger.success(f'<GeventSchedule>启动成功 -- {docker.__name__}')

    def release_docker(interface: str = 'interface'):
        """
        由接口解压容器主线功能
        @param interface: 接口函数名
        @return:
        """
        logger.info(f'>> Do {docker.__name__}')
        exec(f'docker().{interface}()')

    schedule.every(1).minute.do(release_docker)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # 作为单独脚本运行时需要打上补丁
    exec("from gevent import monkey\nmonkey.patch_all(ssl=False)")
    scl_deploy(SubscribesCleaner)
