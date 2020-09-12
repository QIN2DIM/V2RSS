# REDIS快速入门——常用函数笔记

## Quick Start

```python
import redis

# 建立连接池
pool = redis.ConnectionPool(
	host=,
	port=,
	decode_responses=,
	db=,
)
# 基于连接池 创建Redis实例
r = StrictRedis(connection_pool=pool)

# 设立键值对，设置过期时间为3s
r.set(name='KEY', value='suo_ha', ex=3)

# 获取value, get方法当key不存在不会报错
# “查”方法类似python-dict
resp = r.get(name='KEY')
print(resp)
```

## Redis-List

### 增

- `lpush(name, values)` 左入列

- `rpush(name, values)` 右入列

  ```python
  r.rpush('test_list', 11, 22, 33)
  # [11, 22, 33]
  
  r.lpush('test_list2', 11, 22, 33)
  # [33, 22, 11]
  ```

  

### 删

- `lrem(name, value, num)`指定值删除，在name对应的list中，删除指定值value。
  - **num >0** , 从"前"到"后"，删除num个value
  - **num = 0**， 删除所有
  - **num < 0** ， 从"前"到"后"，删除num个value
- `lpop(name)` 从左出队，删除一个值，并将其返回。
- `ltrim(name, start, end)` 在name对应的list中，移除没有在**[strat,end]**中的value
- 

### 改

- `lset(name, index, value)`指定索引修改，对redis-list实例name，从左开始数索引号，对index位置的元素，将value重新赋值给它
- `rpoplpush(src, dst)`移动，元素从一个列表移动到另外一个列表
  - **src**：要出队的name
  - **dst**：要入队的name
- `brpoplpush(stc: str, dst: str, timeout: float)` 移动，同理，可以设置超时
  - 当要出队的list中没有元素时，会阻塞系统timeout秒，等待元素出现
  - 当timeout = 0时，表示系统永远阻塞

### 查

- `llen(name)` 查看列表长度
- `lrange(name, index1, index2)` 切片取值
- `lindex(name, index)`根据索引查看value
- 

