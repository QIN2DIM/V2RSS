__all__ = ['flexible_distribute', 'FlexibleDistribute']

import csv
import threading

from BusinessCentralLayer.middleware.redis_io import RedisClient
from config import SERVER_PATH_DATABASE_FETCH, REDIS_SECRET_KEY, NGINX_SUBSCRIBE


class FlexibleDistribute(object):
    """数据交换 弹性分发"""

    def __init__(self, subscribe, class_, life_cycle) -> None:
        self.key_name = REDIS_SECRET_KEY.format(class_)
        self.subscribe, self.class_, self.life_cycle = subscribe, class_, life_cycle

    def to_mysql(self) -> None: ...

    def to_mongo(self) -> None: ...

    def to_redis(self) -> None: ...

    def to_nginx(self) -> None:
        with open(NGINX_SUBSCRIBE.format(self.class_), 'w', encoding='utf-8') as f:
            f.write(self.subscribe)

    def push(self) -> None: ...


# TODO:该模块将被弃用 后续版本将引入多路IO模块，代码使用class封装
def flexible_distribute(subscribe, class_, life_cycle: str, driver_name=None):
    """

    @param subscribe:
    @param class_:
    @param life_cycle:
    @param driver_name:
    @return:
    """

    # data --> Database(Mysql)

    # data --> Database(MongoDB)

    # data --> Redis
    threading.Thread(target=RedisClient().add, args=(REDIS_SECRET_KEY.format(class_), subscribe, life_cycle)).start()

    # data --> csv
    with open(SERVER_PATH_DATABASE_FETCH, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 入库时间 subscribe 类型
        writer.writerow([f'{life_cycle}', f"{driver_name}", f'{subscribe}', class_])

    # data --> <Nginx> if linux or <Cache>
    try:
        with open(NGINX_SUBSCRIBE.format(class_), 'w', encoding='utf-8') as f:
            f.write(subscribe)
    except FileNotFoundError as e:
        print(e)
