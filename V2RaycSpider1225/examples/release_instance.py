from gevent import monkey

monkey.patch_all(ssl=False)


def demo1():
    import random
    from src.BusinessLogicLayer.cluster.slavers import __entropy__
    from src.BusinessLogicLayer.plugins.accelerator import booster

    booster(docker=random.choice(__entropy__), silence=True)


def demo2():
    from src.BusinessLogicLayer.cluster.slavers import ActionPPForSSRCloud
    from src.BusinessLogicLayer.plugins.accelerator import booster

    booster(docker=ActionPPForSSRCloud, silence=True, power=1, assault=True)


if __name__ == '__main__':
    demo2()
