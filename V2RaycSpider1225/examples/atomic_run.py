"""
指定运行实例
"""
from gevent import monkey

monkey.patch_all()
from src.BusinessLogicLayer.plugins.accelerator import booster
from loguru import logger


@logger.catch()
def demo():
    from src.BusinessLogicLayer.cluster.slavers.actions import ActionAzIcoCloud
    booster(docker=ActionAzIcoCloud, silence=True, power=1, assault=True)


if __name__ == '__main__':
    demo()
