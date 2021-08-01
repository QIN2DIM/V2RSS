import random

from src.BusinessLogicLayer.cluster.slavers import __entropy__
from src.BusinessLogicLayer.plugins.accelerator import booster

if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()
    booster(docker=random.choice(__entropy__), silence=True, power=5, assault=True)
