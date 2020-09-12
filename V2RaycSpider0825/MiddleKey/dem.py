import redis, time, random
from MiddleKey.setting import *

pool = redis.ConnectionPool()

r = redis.StrictRedis(
    host=REDIS_HOST_NAME,
    port=REDIS_PORT,
    db=1,
    decode_responses=REDIS_DECODE_RESPONSES,
    connection_pool=pool

)
# for _ in range(100):
#     r.rpush('list1', random.randint(1, 2))


r.set('ka', 'qwe')
resp = r.get('1')
print(resp)
