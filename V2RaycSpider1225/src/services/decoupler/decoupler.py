# -*- coding: utf-8 -*-
# Time       : 2021/12/24 11:38
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 清洗无效订阅
import base64
from typing import Optional

from cloudscraper import create_scraper
from cloudscraper.exceptions import CloudflareChallengeError
from requests.exceptions import SSLError, HTTPError, ProxyError, ReadTimeout

from services.middleware.subscribe_io import SubscribeManager
from services.utils import CoroutineSpeedup
from services.utils import ToolBox


class DecoupleBooster(CoroutineSpeedup):
    def __init__(self, debug: Optional[bool] = False):
        super().__init__()

        self.sm = SubscribeManager()
        self.debug = debug

    def preload(self):
        self.docker = self.sm.sync()

    def control_driver(self, url, *args, **kwargs):
        scraper = create_scraper()

        try:
            response = scraper.get(url, timeout=10)
            context = response.text if response else ""
            subscribe_group = base64.b64decode(response.text).decode("utf-8").split("\n")

            # 部分订阅会预留两条编码信息（剩余流量/剩余时长）以及一些引流标签
            if not context or subscribe_group.__len__() <= 4:
                self.sm.detach(subscribe=url, transfer=False)
                return False

            if self.debug:
                ToolBox.echo(
                    msg=ToolBox.runtime_report(
                        motive="CHECK",
                        action_name="DecoupleBooster",
                        message="Subscribe url is healthy.",
                        url=url,
                    ),
                    level=1,
                )
            return True
        except (SSLError, HTTPError, ProxyError):
            self.sm.detach(subscribe=url, transfer=False)
        except (CloudflareChallengeError, ReadTimeout, ConnectionError):
            pass


def decouple(debug: Optional[bool] = False):
    if not ToolBox.check_local_network():
        if debug:
            ToolBox.echo("The local network is abnormal and the decoupler is skipped.", 0)
        return False
    sug = DecoupleBooster(debug=debug)
    sug.preload()
    sug.go()
