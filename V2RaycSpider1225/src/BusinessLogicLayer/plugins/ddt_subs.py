__all__ = ['SubscribesCleaner']

# 独立使用的链接清理插件，还未并入系统，请勿调用，正确的做法是使用单独的进程运行该脚本

from typing import List

from src.BusinessCentralLayer.coroutine_engine import lsu
from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.setting import REDIS_SECRET_KEY, CRAWLER_SEQUENCE, logger
from src.BusinessLogicLayer.plugins.subs2node import subs2node


class SubscribesCleaner(lsu):
    """解耦清洗插件：国内IP调用很可能出现性能滑坡"""

    def __init__(self, debug=False, kill_target: str = None):
        super(SubscribesCleaner, self).__init__()
        self.debug = debug
        self.keys = [REDIS_SECRET_KEY.format(s) for s in CRAWLER_SEQUENCE]
        self.rc = RedisClient().get_driver()
        self.kill_ = kill_target

    def offload_task(self):
        for key_ in self.keys:
            for sub, _ in self.rc.hgetall(key_).items():
                self.work_q.put_nowait([sub, key_])

    def killer(self):
        """
        @todo redis批量移除或移动hash
        @return:
        """
        if self.apollo:
            for kill_ in self.apollo:
                self.rc.hdel(kill_[0], kill_[-1])
                logger.debug(f'>> Detach -> {kill_[-1]}')

    def control_driver(self, sub_info: List[str]):
        """

        @param sub_info: [subs,key_secret_class]
        @return:
        """
        try:
            # 解耦指定簇
            if self.kill_ and self.kill_ in sub_info[0]:
                self.apollo.append([sub_info[-1], sub_info[0]])
            else:
                # 解析订阅
                node_info: dict = subs2node(sub_info[0], False)
                # 打印debug信息
                if self.debug:
                    print(f"check -- {node_info['subs']} -- {node_info['node'].__len__()}")
                # 订阅解耦
                if node_info['node'].__len__() <= 3:
                    self.apollo.append([sub_info[-1], sub_info[0]])
        except UnicodeDecodeError or TypeError as e:
            logger.debug(f"Retry put the subscribe({sub_info}) to work queue -- {e}")

            # 单个链接重试3次,标记超时链接
            if self.temp_cache.get(sub_info[0]):
                self.temp_cache[sub_info[0]] += 1
            else:
                self.temp_cache[sub_info[0]] = 1
            if self.temp_cache[sub_info[0]] <= 3:
                self.work_q.put_nowait(sub_info)
            else:
                self.apollo.append([sub_info[-1], sub_info[0]])

        except Exception as e:
            logger.warning(f"{sub_info} -- {e}")
            self.apollo.append([sub_info[-1], sub_info[0]])