import multiprocessing
import time
import webbrowser
from urllib.parse import urlparse

from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.middleware.subscribe_io import detach
from src.BusinessCentralLayer.setting import REDIS_SECRET_KEY, CRAWLER_SEQUENCE, logger
from src.BusinessLogicLayer.plugins.accelerator import SubscribesCleaner
from src.BusinessLogicLayer.plugins.breaker import clash_adapter
from src.BusinessViewLayer.myapp.virtual_station import app


class _ClashTaskAsh:
    def __init__(self, debug, decouple):
        self.debug = debug
        self.decouple = decouple

    @staticmethod
    def run_server():
        app.run(host='127.0.0.1', port=8847, debug=False)

    def run_business(self):
        # 1.清洗过期订阅
        if self.decouple:
            logger.info("<ClashTaskAsh> ash | 正在清洗订阅池...")
            SubscribesCleaner(debug=False).interface()
        # 2.拉取订阅池
        logger.info("<ClashTaskAsh> ash | 正在拉取订阅堆...")
        rc = RedisClient().get_driver()
        rss_pool = [subscribe for key_ in CRAWLER_SEQUENCE for subscribe, _ in
                    rc.hgetall(REDIS_SECRET_KEY.format(key_)).items()]
        # 2.1 筛选订阅防止重名
        rss_dict = {}
        for url in rss_pool:
            rss_dict.update({f"{urlparse(url).netloc}@{urlparse(url).query}": url})
        rss_pool = [i[-1] for i in rss_dict.items()]

        # 2.2 删除选中的订阅(取出)  debug模式下不删除
        if not self.debug:
            for subscribe in rss_pool:
                detach(subscribe=subscribe)
        # 3.订阅转换
        logger.info("<ClashTaskAsh> ash | 正在转换订阅模式...")
        # 4.执行订阅转换并缓存配置文件
        clash_adapter.api.run(subscribe=rss_pool)
        # 5.创建本地连接 启动Clash
        webbrowser.open(clash_adapter.api.url_scheme_download()['info'].format("http://127.0.0.1:8847/V2Ray云彩姬"))
        time.sleep(5)
        return True

    def startup(self):
        # --------------------------------------------------
        # 开辟进程
        # --------------------------------------------------
        try:
            # 部署flask
            process_server = multiprocessing.Process(target=self.run_server, name="VirtualStation")
            # 执行业务
            process_business = multiprocessing.Process(target=self.run_business, name="Adapter")
            # 执行多进程任务
            process_server.start()
            process_business.start()
            # 简单监测 主动回收进程
            while True:
                if not process_business.is_alive():
                    process_server.terminate()
                    return True

        except (TypeError, AttributeError) as e:
            logger.exception(e)
        finally:
            logger.success('<ScaffoldGuider> End the V2RayCloudSpider')
            print(">>> 程序執行結束 請手動關閉交互窗口")


class _Interface:

    @staticmethod
    def run(debug: bool = True, decouple: bool = True):
        return _ClashTaskAsh(debug=debug, decouple=decouple).startup()


api = _Interface()


def ash(debug: bool = True, decouple: bool = True):
    return _ClashTaskAsh(debug=debug, decouple=decouple).startup()
