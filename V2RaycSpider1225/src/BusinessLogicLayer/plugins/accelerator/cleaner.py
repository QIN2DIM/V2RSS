"""
- 核心功能
    - 订阅池清洗维护
    - 识别不可用链接并剔除
"""
from typing import List

from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.setting import REDIS_SECRET_KEY, CRAWLER_SEQUENCE, logger
from src.BusinessLogicLayer.plugins.accelerator.core import CoroutineSpeedup
from src.BusinessLogicLayer.plugins.breaker.subs_parser import subs2node


class SubscribesCleaner(CoroutineSpeedup):
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

    def _del_subs(self, key_: str, subs: str, err_: str = '') -> None:
        self.rc.hdel(key_, subs)
        logger.debug(f'>> Detach -> {subs} -- {err_}')

    def control_driver(self, sub_info: List[str]):
        """

        @param sub_info: [subs,key_secret_class]
        @return:
        """
        try:
            # 解耦指定簇
            if self.kill_ and self.kill_ in sub_info[0]:
                self._del_subs(sub_info[-1], sub_info[0], "target")
            else:
                # 解析订阅
                node_info: dict = subs2node(sub_info[0])
                # 打印debug信息
                if self.debug:
                    print(f"check -- {node_info['subs']} -- {node_info['node'].__len__()}")
                # 订阅解耦
                if node_info['node'].__len__() <= 4:
                    self._del_subs(sub_info[-1], sub_info[0], "decouple")
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
                self._del_subs(sub_info[-1], sub_info[0], e)
        except SystemExit:
            logger.critical("请关闭系统代理后再执行订阅清洗操作")
        except Exception as e:
            logger.warning(f"{sub_info} -- {e}")
            self._del_subs(sub_info[-1], sub_info[0])
