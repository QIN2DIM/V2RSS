"""
- 核心功能
    - 订阅池清洗维护
    - 识别不可用链接并剔除
"""
import warnings
from datetime import datetime
from typing import List

from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.setting import REDIS_SECRET_KEY, CRAWLER_SEQUENCE, logger, Fore
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

    def _del_subs(self, key_: str, subs: str, err_) -> None:
        self.rc.hdel(key_, subs)
        # logger.debug(f'>> Detach -> {subs} -- {err_}')
        print(Fore.BLUE, f"[{datetime.now()}] detach -> {subs} {err_}")

    def control_driver(self, sub_info: List[str], threshold: int = 4):
        """

        :param sub_info: [subs,key_secret_class]
        :param threshold: 解耦置信阈值 小于或等于这个值的订阅将被剔除
        :return:
        """
        try:
            # 针对指定订阅源进行清洗工作
            if self.kill_ and self.kill_ in sub_info[0]:
                self._del_subs(sub_info[-1], sub_info[0], "target active removal")
            else:
                # 解析订阅
                node_info: dict = subs2node(sub_info[0])
                # 订阅解耦
                if node_info['node'].__len__() <= threshold:
                    self._del_subs(sub_info[-1], sub_info[0], "decouple active removal")
                elif self.debug:
                    print(Fore.WHITE, f"[{datetime.now()}] valid -- {node_info['subs']} -- {len(node_info['node'])}")

        except (UnicodeDecodeError, TypeError) as e:
            # 对于已标记“解析错误”的订阅 更新其请求次数
            if self.temp_cache.get(sub_info[0]):
                self.temp_cache[sub_info[0]] += 1
            # 否则标记为“解析错误”的订阅
            else:
                print(Fore.YELLOW, f"[{datetime.now()}] recheck -- {sub_info[0]}")
                self.temp_cache[sub_info[0]] = 1
            # 若链接重试次数少于3次 重添加至任务队列尾部
            if self.temp_cache[sub_info[0]] <= 3:
                self.work_q.put_nowait(sub_info)
            # 若链接重试次数大于3次 剔除
            else:
                self._del_subs(sub_info[-1], sub_info[0], e)
        except SystemExit:
            warnings.warn("请关闭系统代理后部署订阅清洗任务")
        except Exception as e:
            logger.warning(f"{sub_info} -- {e}")
            self._del_subs(sub_info[-1], sub_info[0], e)
