# V2Ray云彩姬使用说明

> **声明：该脚本仅供内部测试，严禁对外传播

项目简介：科学上网，从娃娃抓起！

版本号：V0817-第02阶段封测

推荐搭配：[qv2ray](https://qv2ray.net/)、[越过高墙](https://github.com/Alvin9999/new-pac/wiki)



[TOC]

## [1] Quick Start

- 运行根目录中的`main.py`即可启动脚本主程序
- 该脚本部分功能需联网使用，部分局域网可能无法正常使用部分功能
- 若环境初始化模块启动失败，请自行配置开发环境或重启脚本

![image-20200820230131687](https://i.loli.net/2020/08/20/SUE7cRsaQoudLTk.png)

### 1.1 获取v2ray订阅链接

- 在MAIN首页下，依次选择`[2]获取订阅链接`->`[1]v2ray订阅链接`，即可抓取链接；本功能需联网使用。如图为获取成功的界面，点击【OK】后，即可自动复制订阅链接

![image-20200820224557899](https://i.loli.net/2020/08/20/iJpkxCUF9noW7Vt.png)

### 1.2 获取SSR订阅链接

- 在MAIN首页下，依此选择`[2]获取订阅链接`->`[2]ssr订阅链接`，后续流程如上。

  ![image-20200820224959892](https://i.loli.net/2020/08/20/7gZ96nzHx2TuysQ.png)

### 1.3 查询池内可用链接

- 在MAIN首页下，依次选择`[2]获取订阅链接`->`[4]查询可用链接`，即可查看池内可用高质量链接。[v0817客户端不支持选中获取，所有链接由Master统一分发]
- 【新版本改动】：为链接添加**生命倒计时**以及**可用流量**，并依托`uuid_token`**分发链接**

![image-20200820225023578](https://i.loli.net/2020/08/20/KSPwNEU2GaxHAl1.png)

### 1.4 打开本地文件

- 在MAIN首页下，依次选择`[2]获取订阅链接`->`[3]打开本地连接`，即可打开本地缓存文件，查看历史访问记录。

  ```python
  file_name = 'log_VMess.txt'
  ```

  ![image-20200820225500393](https://i.loli.net/2020/08/20/S84kquJiTRUtrCj.png)

### 1.5 查看分布式爬虫消息队列

- 在MAIN首页下，选择`[1]查看机场生态`->`[any]`->`[1]查看`，即可查看`free-VIP-ALL`三个层级的信息，选中即可使用默认浏览器访问网站；部分网站需要科学上网才能访问。

  - 访问时间：2020/08/20

  - 访问类型：FREE

    ![image-20200820230259641](https://i.loli.net/2020/08/20/UNsGA89b5QRXBOx.png)

    - **选中目标机场，OK。**

    ![image-20200820230358140](https://i.loli.net/2020/08/20/xXbUEJjsfe6dylt.png)

    - **自动打开目标网站**

    ![image-20200820230426321](https://i.loli.net/2020/08/20/cgNeRo5wBAXQPqV.png)

## [2] 注意事项

- `进程冻结`。Master会限制客户端的**链接获取**频率，为`1次/min`，其余功能不作限制。该进程锁函数将综合<u>本地时区</u>与<u>分布式服务器时区残差</u>以及<u>请求IP段</u>等多种因素锁死进程。

![image-20200808023546540](https://i.loli.net/2020/08/20/AQvIyKTFLg8ERO7.png)

- 在V0817封测版本中，桌面前端使用`easygui`速成，该模块不兼容进程通信与多线程并发，链接请求延迟较高；并在选中部分功能后，框体会自动跳入静默状态(**正常现象，没有崩溃**)

## **[3] 需求表**

- [ ] 添加{邮件发送模块}，支持开发者账号群发订阅链接
- [ ] 合并V2ray和SSR的订阅链接消息队列，PC端可查看最新可用的3条链接，并择一获取
  - [x] 合并队列
  - [x] 查看链接
  - [ ] 择一获取
- [ ] 逐渐停用easyGUI前端模块，移植web操作平台，兼容跨平台访问(手机，电脑，嵌入式系统)
  - [ ] 加入客户端逆向工程加密模组
- [ ] 添加JS脚本代码，支持一键配置翻墙环境（仅win10：获取链接+打开本地代理软件+更新订阅+选择节点+打开PAC代理）
- [ ] 加入机场打分模块，引入机器学习方案，智能排序+分发链接



## [4] 目录树

```python
#文档树
V2Ray云彩姬0817
 ├── config.ini
 ├── dataBase
 │   ├── log_infomations.csv
 │   ├── ssr机场.txt
 │   └── v2ray机场.txt
 ├── funcBase
 │   ├── func_avi_num.py
 │   ├── get_ssr_link.py
 │   ├── get_v2ray_link.py
 │   └── __init__.py
 ├── main.py
 ├── MiddleKey
 │   ├── VMes_IO.py
 │   ├── __init__.py
 │   └── __pycache__
 ├── Panel
 │   ├── all_airPort.py
 │   ├── GUI_Panel.py
 │   ├── main_panel.py
 │   ├── NetCheck_panel.py
 │   ├── reball.py
 │   └── __pycache__
 ├── requirements.txt
 ├── spiderNest
 │   ├── 1.txt
 │   ├── preIntro.py
 │   ├── SNIF_dog.py
 │   ├── SSRcS_xjcloud.py
 │   ├── V2Ray_vms.py
 │   ├── __init__.py
 │   └── __pycache__
 ├── V2Ray云彩姬使用说明.md
 └── 统计项目代码行数.py
```