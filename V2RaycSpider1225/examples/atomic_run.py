"""
指定运行实例
"""
from gevent import monkey

monkey.patch_all()
from src.BusinessLogicLayer.plugins.accelerator import booster
from loguru import logger


def demo():
    from src.BusinessLogicLayer.cluster.slavers.actions import ActionFETVCloud
    try:
        booster(docker=ActionFETVCloud, silence=True, power=1, assault=True)
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    demo()
