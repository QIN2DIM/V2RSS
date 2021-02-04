# `V2Ray`云彩姬<使用指南>

- 版本号：`v4.5.3-stable`

- 推荐搭配：[qv2ray](https://qv2ray.net/) || [v2fly](https://www.v2fly.org/)

## 一、服务说明

> 若您为`V2Ray云彩姬`项目用户，请您自觉遵守以下约定：
>
> 1. 禁止使用本项目及其分支提供任何形式的收费代理服务；
> 2. 禁止在某些“特殊的局域网环境”下启动程序；
> 3. 禁止在国内网络环境下大范围传播。

## 二、快速上手

运行`V2Ray云彩姬`启动程序本体。

### 2.1 获取订阅链接

- **`v2ray`**

    在`Home`首页下，依次选择`[2]获取订阅链接` -- `[1]v2ray订阅链接`既可获取`subscribe`；本功能需联网使用。如图为获取成功的界面，点击<kbd>OK</kbd>后，即可自动复制``subscribe``。

![image-20200820230131687](https://i.loli.net/2020/11/29/JC25v8qd6wzPjXY.png)

![image-20200820224959892](https://i.loli.net/2020/10/06/SpYkGOtm5JoCIdH.png)

![5](https://i.loli.net/2020/10/06/dLpg64V5yJnqRc3.png)

- **`ssr`**

    在`Home`首页下，依次选择`[2]获取订阅链接`->`[2]ssr订阅链接`，后续流程如上。

- **`any`**

    云彩姬高度集成订阅请求流程，后续添加的订阅获取方案都会大致如上垂直简约。


### 2.2 查询链接队列

在`Home`首页下，依次选择`[2]获取订阅链接`->`[4]查询可用链接`，即可查看队列中的~~可用的高质量~~订阅链接。

![Snipaste_2020-11-29_07-58-14](https://i.loli.net/2020/11/29/Oz5hxQudwS2Pvrt.png)

### 2.3 查看访问历史

在`Home`首页下，依次选择`[2]获取订阅链接`->`[3]打开本地连接`打开本地仓库，查看历史访问记录。

![1](https://i.loli.net/2020/11/29/twn6GHjk85SQdYT.png)

![image-20200820225500393](https://i.loli.net/2020/08/20/S84kquJiTRUtrCj.png)			

### 2.4 查看机场生态

> `v2ray云彩姬` 内置高性能网络爬虫模块，使用本机资源采集~~全网~~机场生态（因不可抗力因素不再开源/更新此模块）。

- **获取数据**

    在`Home`首页下，依次选择`[1]查看机场生态`->`[any]`->`[1]查看`，既可查看`free-vip-all`三个层级的数据，选中项目并敲下<kbd>Enter</kbd>既可使用默认浏览器访问机场（部分网站需要代理访问）。

![Snipaste_2020-11-29_08-02-08](https://i.loli.net/2020/11/29/q9sIONvtymjdF8r.png)

![Snipaste_2020-11-29_08-02-19](https://i.loli.net/2020/11/29/wuyBETxZ7q8rg4m.png)

![Snipaste_2020-11-29_08-02-26](https://i.loli.net/2020/11/29/vgsSKzoI9iC2upZ.png)

![Snipaste_2020-11-29_08-05-16](https://i.loli.net/2020/11/29/QHWiO2qguFlrREz.png)

![6](https://i.loli.net/2020/10/06/2QoPy7dVbNe3qpf.png)

- **保存数据**

    在`Home`首页下，选择`[1]查看机场生态`->`[any]`->`[2]保存`，即可保存`free-vip-all`三个层级的对应信息。

![image-20201006030442474](https://i.loli.net/2020/10/06/irVUoXcjaf82CAx.png)

![image-20201006030832332](https://i.loli.net/2020/10/06/oqG2nMLfuQavZ9m.png)

## 三、注意事项

### 3.1 权限冻结

`V2Ray云彩姬`**会主动限制用户的请求频率**，其他功能不做限制。软件内置的进程锁函数将综合<u>本地时区</u>与<u>分布式服务器时区残差</u>、<u>请求`IP`段</u>等多种因素锁死进程。

![image-20200808023546540](https://i.loli.net/2020/08/20/AQvIyKTFLg8ERO7.png)

### 3.2 其他

- 当前版本的桌面前端基于`easygui`开发，该模块在多线程应用场景下极其！麻瓜，故仅作`Panel`使用；若您在使用过程中遇到响应迟钝或请求**延迟高等问题**（触发功能后程序框体消失等灵异现象），请检查您当前的网络状况，若等待数秒后仍无响应请重启软件；
- 若无特殊需求或安全性漏洞，本项目前端`panel`将不再升级/更新，其余项目进度将在[Projects](https://github.com/QIN2DIM/V2RayCloudSpider/projects)中公示；
- 更多关于本项目的bug请在`issue`中留言。