[中文](https://github.com/QIN2DIM/V2RayCloudSpider) **||** [English](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/README_us.md)

# V2Ray云彩姬

**科学上网 从娃娃抓起** **||** **运行脚本 开箱即用**

## :carousel_horse: 项目简介

> 1. 本项目软件及源码禁止在国内网络环境大范围传播；
>
> 2. 本项目开源免费，请不要滥用接口；
>
> 3. 禁止任何人使用本项目及其分支提供任何形式的收费服务。

- 针对全球范围内基于[STAFF原生架构](https://github.com/Anankke/SSPanel-Uim)产出的机场进行垂直挖掘；
- 从`Youtube`、`SONA-TechnologyForum` 等平台获取`RegisteUrl & HitTarget`；
- 综合`LifeCycle`、`RemainingFlow `、`NodeQuality`等参数进行联合采集；
- 理论上支持所有类型订阅的采集；
- 更多项目细节请访问[李芬特小窝Blog](https://www.qinse.top/v2raycs/) :smirk:

## :eagle: 快速上手

- **【方案一】用户**

    - 软件获取：[**Windows10 64x <约17Mb>**](https://t.qinse.top/subscribe/v2ray云彩姬.zip) **||** [备用下载地址](https://yao.qinse.top/subscribe/v2ray云彩姬.zip)

    - 软件使用：运行`V2Ray云彩姬.exe` 既可启动本体

         [V2Ray云彩姬使用说明](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2Ray云彩姬使用说明.md)

- **【方案二】开发者**

    1. Clone项目；
    2. 根据提示信息合理配置`config.py`后运行`main.py` 既可部署项目。

![Snipaste_2020-11-25_12-19-45](https://i.loli.net/2020/11/25/P9Kyr1ZEG43obnD.png)

## :video_game: 进阶玩法

> `Tos`：该项目基于`Windows10`环境开发，`Mac`用户~~可能~~无法正常使用
>
> `Help`： [环境配置说明](https://shimo.im/docs/5bqnroJYDbU4rGqy/)

1. **打开冰箱门**
    - 请将`V2RaycSpider+版本号`的源码文件上传至服务器的`/qinse`文件夹（若没有就新建一个或者改动源码）
    - 请确保部署环境已安装`redis`并开放远程访问权限
    - 请确保部署环境已配置`Python3`开发环境且已安装第三方包

```powershell
# 拉取第三方包
pip install -r /qinse/V2RaycSpider1125/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

2. **将李芬特装入冰箱**
    - 全局配置文件：[V2RayCloudSpider/config.py at master · QIN2DIM/V2RayCloudSpider (github.com)](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2RaycSpider1125/config.py)

3. **关闭冰箱门**
    - 程序全局接口：[V2RayCloudSpider/main.py at master · QIN2DIM/V2RayCloudSpider (github.com)](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2RaycSpider1125/main.py)

### :balance_scale: 参数设置

1. **`ChromeDriver`** 

    请确保服务器安装`google-chrome`，并配置了对应版本的`ChromeDriver`并设置`文件权限 -> [ √ ]执行`

    - 若您正在使用`Finalshell`l或`Xshell`等服务器远程登录方案， <kbd>右键</kbd>目标文件 -><kbd>点击</kbd>`文件权限`即可给予**执行权限**
    - 项目预装的`ChromeDriver`对应的`Chrome`版本号为`v85.0.4183.102`。若版本不同，请根据`config.py`中的提示替换目录中的对应文件

```python
# Windows Chromedriver文件路径
if 'win' in platform:
    CHROMEDRIVER_PATH = dirname(__file__) + '/BusinessCentralLayer/chromedriver.exe'
# Linux Chromedriver文件路径
else:
    CHROMEDRIVER_PATH = dirname(__file__) + '/BusinessCentralLayer/chromedriver'
```

2. **`AppRun`**

    - 运行`main.py`既可启动项目，详细操作说明请看`main.py`源码

    - 服务器后台运行

        推荐搭配`tmux`使用，详见[Tmux 使用教程 - 阮一峰的网络日志 (ruanyifeng.com)](http://www.ruanyifeng.com/blog/2019/10/tmux.html)

```powershell
# CentOS7 部署
nohup python3 /qinse/V2RaycSpider1125/main.py deploy &
```

3. **`HyperParams`**

    以上设置均在`main.py`以及`config.py`文件中有详细说明，遇到问题请自行检索或通过`issue/email`给作者留言

### :zap: 其他设置

- 使用`GET`请求，访问以下接口，既可获取`CrawlerSeq subscribe_link`（该资源来自`Redis`数据交换的分发缓存接口，作者会在未来版本将此类玩法拓展为基于垂直网络的数据挖掘模块并暴露更多的`API`）。
- 注：使用该方法获取的链接并不一定可用

```python
# Python3.8
# quickGet API
import requestsS

subs_target = 'https://t.qinse.top/subscribe/{}.txt'

subs_ssr = requests.get(subs_target.format('ssr')).text
subs_trojan = requests.get(subs_target.format('trojan')).text
subs_v2ray = requests.get(subs_target.format('v2ray')).text

print("subs_ssr: {}\nsubs_: {}\nsubs_v2ray: {}\n".format(subs_ssr,subs_trojan,subs_v2ray))
```

![image-20201020112752998](https://i.loli.net/2020/10/20/XaJc4qA1ehPUM5V.png)

##  :small_red_triangle: 注意事项

- **防火墙警告**

  ​	首次运行可能会弹出提示



![MhwiZfOz3VdDPU5](https://i.loli.net/2020/11/25/ImlKL3x68YfHQJi.png)

![2](https://i.loli.net/2020/11/25/nGk1XiaYVc2zAZp.png)

## :loudspeaker: 更新日志

- #### 2020.01.01 v_4.5.3.beta

    > **重要更新**

    1. 容器集成，支持项目打包成镜像部署到任意服务器上运行

    2. 架构微调，更好地兼容分布式节点任务

        主子的1G内存VPS实在难以长期稳定运行这个对服务器资源消耗巨大的项目。也许是采集方案有待优化，但就目前的服务器配置而言，弹性失去了意义。。。目前针对本项目的最优性能微服务架构（基于`Go` + `Python`）已调教完毕，本人会在期末考后完成最后的开发任务:haircut:，并把采集任务部署到集群节点上。
    
- #### 2020.12.01 v_1.0.3.12162350.11.beta

    > **重要更新**

    1. （beta）我们为`iOS`用户提供了一种基于`捷径指令` + `URL Scheme`  的订阅链接瞬时获取解决方案

        - 该方案API接口暂未开放，待功能完善后会暴露在技术文档中

        - [x] `Shadowrocket` + `shortcut command` 
        - [ ] `Quantumult` + `shortcut command`

    2. 采集架构优化，引入基于`exec` + `with`的节点动态嗅探加载策略

- #### 2020.11.24 v_1.0.2.11162350.11.beta

    > **重要更新**

    1. 强化工程鲁棒性并进一步优化采集工作流
    2. 优化工程逻辑，降低部署难度
    3. 引入用户鉴权

    > **功能迭代**

    1. 重载模块并暂时停用`TrojanCollectionModule(TCM)`
    2. 拓展队列容量至 `200pieces`.
    3. 编写 `ACM-CentralEngine`学习拟人行为

    > **性能调优**

    1. 引入  `Type-SuperClass Elastic Scaling Solution(T-SC ESS)`.
    2. 引入 `Goroutine-APSchedule Mode(G-APSM)`.

- #### **2020.10.20 v_4.5.2** 

    > **重要更新**

    1. 支持当前热门类型（ `Trojan`、`v2ray`、`ssr`）订阅链接的多任务并发采集
    2. 重写文档树，旧版软件已弃用，请将PC客户端升级至最新版本
    3. 添加自动更新功能

    > **功能迭代** 

    1. 使用`Redis`接管链接分发业务以提高程序整体的运行效率
    2. 暴露部分链接请求接口，详细食用方法请看技术文档
    3. `ConfinementTime` 增加至 `30s/e`.

## :world_map: 开源计划

- [ ] 为`iOS`用户提供一种基于`捷径指令` + `URL Scheme`  的订阅链接瞬时获取解决方案
    - [ ] `云彩姬` + `Shadowrocket`
    - [ ] `云彩姬` + `Quantumult`
- [ ]  兼容所有`Subclass`订阅
    - [x] `Trojan-go`、`Trojan-gfw`
    - [x] `V2ray`、`ShadowSocksR`
    - [ ] `Surge 3` 、`Quantumult`、`Kitsunebi`
- [x] 合并订阅链接消息队列，PC端可查看目前在库的`Subscribe Link`并择一获取
  - [x] 合并队列
  - [x] 查看链接
  - [x] 择一获取
- [ ] 前后端分离，使用Flask包装中间件
    - [ ] 逐渐停用`easygui`前端模块，开发跨平台视图交互模块
    - [ ] 引入`呼吸节拍`中间件，让任务行为拟人化
    - [ ] 加入自下而上的代码自动化生成模块、引入智能识别及数据挖掘生态

## :email: 联系我们

> 本项目由海南大学机器人与人工智能协会数据挖掘小组(`A-RAI.DM`)提供维护

- [**Email**](mailto:RmAlkaid@outlook.com?subject=CampusDailyAutoSign-ISSUE) **||** [**Home**](https://a-rai.github.io/)

###  
