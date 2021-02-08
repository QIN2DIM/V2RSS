# V2Ray云彩姬<开发者文档>

> 更新日期：2021/02/08
>
> 由于开发版（Private）与稳定版（Open）代码相差巨大，本篇技术文档仅供参考，帮助开发者部署供私人使用的单机项目。

核心技术栈 ：`Python3`||`GoLand`||`Linux`||`Redis`||`MySQL`||`Selenium`||`Flask`||`Docker`||`Ngnix`

[TOC]

## 一、环境复现

> `Tos`：该项目基于`Windows`环境开发测试，`CentOS7`环境调试部署，`Mac`用户~~可能~~无法正常使用。
>
> `Tip`：`v_5.u.r-beta` 版本项目基`Python3`开发，暂未涉及`go(micro-service)`。
>
> `Help`： [环境配置说明][1]

|      项目名       |                           参考软件                           |           备注           |
| :---------------: | :----------------------------------------------------------: | :----------------------: |
|     操作系统      |                 `Windows 家庭版` 、 `CentOS7`                 | / |
|     开发工具      |         `Pycharm 2019.3.3 专业版`  、`Goland 20.3.1`         | `Python3.7` 、`go 1.15.7` |
|    数据库管理     |         `RedisManagerDesktop` 、 `Navicat Premium 15`         | / |
|     远程登录      |                `Finalshell` 、 `Xshell/Xftp`                | / |
|     开发依赖      |                   `Chrome` 、 `Chromedrier`                   | / |
| 辅助工具(`Win64`) | `Anaconda Navigator`、`Typora + PigGo`、`Aaliyun SDK` |/|
| 辅助工具(`Linux`) |                       `pyenv`、`tmux`                       | 便于版本管理与项目调试 |

## 二、启动项目

### 2.1 打开冰箱门

> 此步骤帮助开发者配置服务器开发环境，尽可能降低项目运行时的宕机风险。

#### 2.1.1 初始化目录并上传项目文件

将`V2RaycSpider+版本号`的源码文件打包上传至服务器的`/qinse`目录下（在根目录下新建）。

#### 2.1.2 配置Redis

根据[环境配置说明][1]配置`redis`，若您初次为服务器配置`redis`，建议所有的操作都在`/qinse`工程目录下进行。

必须配置：远程访问&加密&开机自启&持久化，可选配置：主从复制||哨兵模式。

#### 2.1.3 配置Python3开发环境

根据[环境配置说明][1]配置`Python3`基础开发环境，并在`/qinse/V2RaycSpider<version>`目录下执行`pip`命令拉取项目依赖：

```bash
# 拉取依赖
pip install -r /qinse/V2RaycSpider1225/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

若启动项目后出现`ModuleNotFound`的报错，可能原因是部分第三方库并未放入`requirements.txt`中，缺啥补啥既可，参考代码如下：

```bash
# pip 安装第三方库 pip install <the name of missing package> ，如：
pip install pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2.1.4 配置chromedriver

根据[环境配置说明][1]安装`google-chrome`以及对应版本的`chromedriver`，在`Linux`服务器中需要给予`文件权限 -> [ √ ]执行`。

- 若您正在使用`Finalshell`l或`Xshell/Xftp`等服务器远程登录方案， <kbd>右键</kbd>目标文件 -><kbd>点击</kbd>`文件权限`既可给予**执行权限**；
- 将`ChromeDriver`文件放到指定目录下：
  - `Windows`:`X:/qinse/V2RaycSpider1225/BusinessCentralLayer/chromedriver.exe`
  - `Linux` or `Mac`:`/qinse/V2RaycSpider1225/BusinessCentralLayer/chromedriver`

### 2.2 将李芬特装入冰箱

> 此步骤解读配置文件中的参数含义，帮助开发者根据不同的使用场景区别调试。

#### 2.2.1 `config.yaml`参数配置

> [YAML 语言教程][5]

工程目录下自带[`config-sample.yaml`][2]模板配置文件，在初次启动项目时，系统会拷贝一份`config.yaml`放到根目录下，并自主中断程序运行。此时开发者需要根据实际情况配置`config.yaml`后重启项目。值得注意的是，`config-sample.yaml`不起作用但请不要将其移出根目录。

- `SINGLE_DEPLOYMENT` 部署模式

  当其为True时表示单机部署，既这个项目只用一台服务器跑。若为False则表示使用至少两台服务器运行项目。

- `ENABLE_DEPLOY` 定时任务设置集合

  - `global` 定时任务总开关

    当`global: False`时，服务器不会执行任何的定时任务（`collector`除外）。

  - `tasks` 定时任务

    若为单机部署场景，以下三个任务请务必都开启。若为多服务器集群部署，建议将采集任务和DDT任务分离。

    - `collector`采集器行为

      系统的**采集**操作分为`upload`、`download`、`force_run`三种行为模式。

      - 当系统处于单机部署(`SINGLE_DEPLOYMENT: True`)场景时，默认执行`force_run`，由主机自生成待行任务并自我消耗。
      - 当系统处于集群模式时，`collector:True`表示当前节点执行`download`操作，待执行任务经由`redis`队列同步至本机的协程队列当中，此同步过程受制约于`beat_sync`和`only-sync`机制（后文介绍）。同步后，将由协程引擎`vsu`并发消化待执行任务。
      - 当系统处于集群模式时，`collector:False`表示当前节点执行`upload`操作，本机生成待执行任务并同步至`redis`队列，此同步过程受制约于`beat_sync`和`only-sync`机制（后文介绍）。同步后不执行多余操作。

      可以发现，无论`collector`为何bool值，采集器都将生效并存在，只是根据部署模式的不同而执行不同的行为模式。值得一提的时，定时任务总开关`global`并不能限制`collector`的启用或关闭，只能影响其模式的切换。

    - `ddt_overdue`移除过期订阅

      采集的订阅都会加入到`redis`中，我们熟知`redis`自带消息过期机制，被标注“倒计时”的顶级key“过期”时会被删除，但本系统使用的`hash-feild`数据结构使得每个原子订阅都不是顶级键值对，故暂时无法通过`redis`的自有机制安全的移除过期订阅。

      而此任务将从Python的第三方API角度出发，定时遍历`redis`，进行日期数据比对，进而删除过期订阅。过期订阅删除存在`beyond`越时删除机制以及`ddt`（傻瓜式）主从拷贝机制（后文介绍）。

      关于“如何定义订阅过期时间”，“如何判断订阅过期”等问题，后文一并介绍。

    - `ddt_decouple` 解耦订阅

      此任务的核心目的是删除“不可用订阅”。我们知道订阅未过期但不一定可用，上文所述任务所定义的“过期时间点”是静态数据，若在此前出现因机场优惠调整、跑路或被攻击等问题导致的服务器高负荷运转甚至宕机的现象，`ddt_overdue`将出现严重的订阅漏检。故需要重新定义一个新的检测逻辑来发现这些暂时有问题的订阅，并将其移出`redis`。

      此任务的次级目的是“账号解耦”，我们知道一个机场可能支持多种订阅模式。如当前版本系统会主动采集机场的`v2ray`以及`ssr`订阅链接（若存在接口），但机场是账号制管理，无论什么类型的订阅都共享一个账号的数据流量并受限于同一个审计规则。而当前版本`panel`并未具备`v_5.u.r-beta`更新的`detach`机制，既前端用户获取某类型的链接，服务器将该链接从池中移出，而合理的做法是根据该链接定位出池中属于同一账号的所有订阅一并删去。在新版本的`panel`中理应带有此种机制。

      关于“如何定义机场故障”，“如何判断订阅失效”等问题后文一并介绍。

- `ENABLE_SERVER` 部署Flask

- `ENABLE_COROUTINE` 协程加速

  系统的通信方式以及`chromedriver`业务基于协程编写，如无特殊情况请开启协程加速。而当`ENABLE_COROUTINE: False`时并不意味着关闭协程，而是在协程状态下保持操作功率为1的行为。

- `ENABLE_REBOUND` 数据回弹

  请保持此功能为关闭状态，当前版本并未完善该参数所代表的机制。

  `ENABLE_REBOUND: True`时将反转`redis`的主从状态，既可在主机挂掉后，主动将slave中的数据清洗后回滚到master中。这里的“清洗”和“回滚”都需要开发者通过脚手架单步执行。

  由于`v_7.u.r-dev`等更高版本的项目中已经使用了基于`go-zero`的微服务架构，此时的`redis`工作是基于多服务器多哨兵模式的，“主从反转”的意义不大，故已弃用。

- `SINGLE_TASK_CAP`队列容载

  此参数将限制`redis`中某一类订阅的最大存储数量（此操作并非最高优先级的中断点，仅限制主程序的定时采集行为）。

  为何需要限制数量？上文所述的定时任务会涉及到密集的`IO`行为，池内过多的订阅会限制整机性能。

  `redis`中某一类的订阅数量并非不会超过`SINGLE_TASK_CAP`所订阅的阈值，其存在`offload`以及`beat_sync`机制，后文一并介绍。

- `LAUNCH_INTERVAL` 定时任务间隔

  此参数对应于`tasks`中的任务，除`collector`外，其余参数若在``ENABLE_DEPLOY` `被置为False，则此处的参数是不生效的。

  若为集群部署，建议master和slaves的`collector`执行间隔保持一致。

- `REDIS_MASTER` 

  核心配置！不填或填写有误将无法启动项目。

- `REDIS_SLAVER_DDT`

  若为单机部署，请开启至少两个进程的`redis`并配置此项。若为集群部署，则照常填写即可。如不打算使用此功能，将此配置中的`host`、`password`、`port`保持与主机一致，并分开放在不同的`db`中。

- `API_PORT`

  项目的外部通信模式为HTTP，此项为Flask的API外网端口

- `SMTP_ACCOUNT`

  可选。使用SMTP发送邮件，默认使用[QQ邮箱][4]，如若使用其他厂商邮箱，可能需要修改STMP端口号。

- `SERVER_CHAN_SCKEY`

   可选。使用[<SERVER酱>][3]推送，填写`SERVER_CHAN_SCKEY`。

- `MYSQL_CONFIG`

  当前版本可不填写。

- `REC_PORT`

  当前版本可不填写。

- `ENABLE_KERNEL`

  当前版本可不填写。

#### 2.2.1 guider脚手架调试接口

#### 2.2.2 高级配置

- 微服务
- 消息队列
- 单元测试
- 前后端分离开发

### 2.2 关闭冰箱门

[程序全局接口](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2RaycSpider1225/main.py) || 通过脚手架调试/启动/部署项目。

根据[环境配置说明][1] || 查看`argv`参数的运行逻辑。

```python
# main.py 程序全局接口
from sys import argv

from BusinessCentralLayer.scaffold import scaffold

"""欢迎使用V2Ray云彩姬"""
if __name__ == '__main__':
    scaffold.startup(driver_command_set=argv)
```

- 在`Terminal`中执行接口指令运行`main.py`（脚手架接口）查看可用指令，如：

```shell
# 当前目录 /qinse/V2RaycSpider1225/
python main.py 
```

- 在`Terminal`中执行指令部署项目，如：

```shell
# 当前目录 /qinse/V2RaycSpider1225/
python main.py deploy
```

- 使用`deploy`指令将在当前会话窗口启动一个双进程+多线程+多协程的阻塞任务，若不使用`后台挂起`指令或诸如`tmux`的会话管理工具，当前会话将无法进行其他操作，且当远程登陆软件退出后任务进程将被终止。

  - （推荐）搭配`tmux`使用，详见[Tmux 使用教程][1]；
  - 使用`centOS 7`原生指令执行挂起后台任务，如：

```shell
# 当前目录 /qinse/V2RaycSpider1225/
# nohup 和 & 缺一不可
nohup python main.py deploy &
```

## 三、其他设置

> - 若无特殊需求或安全性漏洞，本项目`master`分支的前端`panel`将不再升级/更新，其余项目进度将在[Projects](https://github.com/QIN2DIM/V2RayCloudSpider/projects)中公示；
> - 更多<u>关于本项目的</u>bug请在`issue`中留言，欢迎二次开发。

（更新中...）

[1]: https://shimo.im/docs/5bqnroJYDbU4rGqy/	"环境配置说明"
[2]: https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2RaycSpider1225/config-sample.yaml	"全局配置文件"
[3]: http://sc.ftqq.com/3.version	"SERVER酱"
[4]: https://service.mail.qq.com/cgi-bin/help?subtype=1&amp;&amp;id=28&amp;&amp;no=1001256	"SMTP QQ"
[5]: http://www.ruanyifeng.com/blog/2016/07/yaml.html	"YAML 语言教程"

