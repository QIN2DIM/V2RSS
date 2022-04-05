"""
> 检测本地执行队列的状态
    Queue:__entropy__ + __pending__
> Status
    实例正常，限制注册，拒绝注册，危险通信，流量阻断，代理异常，检测失败，响应超时
"""

from gevent import monkey

monkey.patch_all()
import unittest

from apis.scaffold import entropy


class SpawnUnitTest(unittest.TestCase):
    def test_atomic_heartbeat(self):
        self.assertNotEqual({}, entropy.check())


if __name__ == "__main__":
    unittest.main()
