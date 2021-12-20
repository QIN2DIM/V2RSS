"""
> 检测本地执行队列的状态
    Queue:__entropy__ + __pending__ + deprecated_actions
> Status
    实例正常，限制注册，拒绝注册，危险通信，流量阻断，代理异常，检测失败，响应超时
"""

from gevent import monkey

monkey.patch_all()
import os
import unittest

from src.BusinessLogicLayer.cluster.slavers.actions import __entropy__, __pending__, deprecated_actions
from src.BusinessLogicLayer.apis.scaffold_api import mining


class SpawnUnitTest(unittest.TestCase):

    def test_atomic_heartbeat(self):
        # 拼接送测实例抽样对象
        pending_runner = __entropy__ + __pending__ + deprecated_actions
        url2atomic = {atomic["register_url"]: atomic for atomic in pending_runner}

        # 运行检测代码
        sug = mining.SSPanelHostsClassifier(docker=list(url2atomic.keys()))
        sug.go(power=os.cpu_count())

        self.assertNotEqual({}, sug.offload())


if __name__ == "__main__":
    unittest.main()
