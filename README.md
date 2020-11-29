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

## :loudspeaker: 更新日志

- #### 2020.11.24 v_1.0.2.11162350.11.beta

  > **Major Update**

  1. Further optimize the project engineering structure.
  2. Further optimize the program logic to reduce the difficulty of project deployment.
  3. Modify user permissions.

  > **Function Iteration**

  1. Overload the `TrojanCollectionModule(TCM)`.
  2. Expand the work queue to `150pieces/day`.
  3. Program the `ACM-CentralEngine` to counter the anti-crawler mechanism.

  > **Performance Tuning**

  1. Introduce the  `Type-SuperClass Elastic Scaling Solution(T-SC ESS)`.
  2. Introduce the `Goroutine-APSchedule Mode(G-APSM)`.

- #### **2020.10.20 v_4.5.2** 

  > **Major Update**

  1. These types of subscription links（ `Trojan`、`v2ray`、`ssr` ）are supported by multi-threaded federated collections.
  2. The document tree has been rewritten, and the old version of the software cannot run normally.
     -  :old_key: Update the `v2raycs Client` to the latest version.
  3. Add auto update function.

  > **Function Iteration** 

  1. Using `Redis` to take over the access business to improve distribution efficiency.
  2. Open get interface. Please refer to the manual for usage.
  3. `ConfinementTime` increased to `30s/e`.

## :eagle: 快速上手

- **【方案一】用户**

    - 软件获取：[**Windows10 64x <约17Mb>**](https://t.qinse.top/subscribe/v2ray云彩姬.zip) **||** [备用下载地址](https://yao.qinse.top/subscribe/v2ray云彩姬.zip)

    - 软件使用：运行`V2Ray云彩姬.exe` 既可启动本体

         [V2Ray云彩姬使用说明](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2Ray云彩姬使用说明.md)

- **【方案二】开发者**

    - 下载源码

![Snipaste_2020-11-25_12-19-45](https://i.loli.net/2020/11/25/P9Kyr1ZEG43obnD.png)

- 根据提示信息合理配置`config.py`后运行`main.py` 既可部署项目


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
