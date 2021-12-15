"""
检测队列实例状态
"""
import urllib.request

from gevent import monkey

monkey.patch_all()
import os
import sys
import unittest

import requests
from loguru import logger
from requests.exceptions import ConnectionError, SSLError, HTTPError, Timeout
from src.BusinessLogicLayer.cluster.slavers.actions import __entropy__, __pending__, deprecated_actions

from src.BusinessLogicLayer.plugins.accelerator.core import CoroutineSpeedup

SILENCE = True if "linux" in sys.platform else False


class SpawnUnitGuider(CoroutineSpeedup):
    def __init__(self, task_docker: list = None):
        super(SpawnUnitGuider, self).__init__(task_docker=task_docker)
        logger.debug("本机代理状态 PROXY={}".format(urllib.request.getproxies()))

    @logger.catch()
    def control_driver(self, url):
        session = requests.session()
        try:
            response = session.get(url, timeout=5)

            if response.status_code > 400:
                logger.error(f"站点异常 status_code={response.status_code} url={url}")
                return False
            logger.success(f"实例正常 status_code={response.status_code} url={url}")
            return True
        except ConnectionError:
            logger.error(f"流量阻断 url={url}")
            return False
        except (SSLError, HTTPError):
            logger.warning(f"代理异常 - url={url}")
            return False
        except Timeout:
            logger.error(f"响应超时 - url={url}")
            return False


class SpawnUnitTest(unittest.TestCase):

    def test_atomic_heartbeat(self):
        # 拼接送测实例抽样对象
        pending_runner = __entropy__ + __pending__ + deprecated_actions
        url2atomic = {atomic["register_url"]: atomic for atomic in pending_runner}

        # 运行检测代码
        sug = SpawnUnitGuider(task_docker=list(url2atomic.keys()))
        sug.interface(power=os.cpu_count())

        self.assertNotEqual({}, sug.killer())


if __name__ == "__main__":
    unittest.main()
