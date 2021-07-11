# [Document] Scaffold entropy指令

## 1 指令简介

打印当前主机活跃的采集队列，既当前采集器收到相关指令时会主动调用的任务实例。包含的信息段有`存活周期` `源链接` 以及`采集类型`。

## 2 demo

![12345](https://i.loli.net/2021/07/11/SzqZVYl1ecQ4N6o.gif)

## 3 使用说明

在`main.py`所在目录下运行以下编译指令

``` python
python main.py entropy
```

或根据具体情况运行，既确保运行的python版本 `py >= 3.6`

```python
python3 main.py entropy
```

