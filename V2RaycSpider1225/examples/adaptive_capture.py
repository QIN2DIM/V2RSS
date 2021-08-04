import random

import gevent

from src.BusinessLogicLayer.cluster.prism import PrismV2
from src.BusinessLogicLayer.cluster.slavers.instances import ActionAaxCloud


def prism():
    with open('staff_arch_general.txt', 'r', encoding='utf8') as f:
        urls = [i for i in f.read().split('\n') if i]
    random.shuffle(urls)

    for url in urls:
        PrismV2(register_url=url, silence=False).run()
        input()


def super_go(x=1, silence=True):
    from gevent import monkey
    monkey.patch_all()
    gevent.joinall([gevent.spawn(ActionAaxCloud(silence=silence).run) for _ in range(x)])


if __name__ == '__main__':
    # prism()
    super_go()
