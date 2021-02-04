# V2Ray云彩姬<开发者文档>

> 更新日期：2021/02/04
>
> 由于开发版（Private）与稳定版（Open）代码相差巨大，本篇技术文档仅供参考，帮助开发者部署供私人使用的单机项目。

核心技术栈 ：`Python3`||`GoLand`||`Linux`||`Redis`||`MySQL`||`Selenium`||`Flask`||`Docker`||`Ngnix`

## 一、环境复现

> `Tos`：该项目基于`Windows`环境开发测试，`CentOS7`环境调试部署，`Mac`用户~~可能~~无法正常使用。
>
> `Help`： [环境配置说明](https://shimo.im/docs/5bqnroJYDbU4rGqy/)

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

> 请根据[环境配置说明](https://shimo.im/docs/5bqnroJYDbU4rGqy/)进行运行环境的适配

### 2.1 打开冰箱门

#### 2.1.1 初始化目录并上传项目文件

将`V2RaycSpider+版本号`的源码文件打包上传至服务器的`/qinse`目录下（在根目录下新建）。

#### 2.1.2 配置Redis

根据[环境配置说明](https://shimo.im/docs/5bqnroJYDbU4rGqy/)配置`redis`，必须配置：远程访问&加密&开机自启&持久化，可选配置：主从复制||哨兵模式。

#### 2.1.3 配置Python3开发环境

根据[环境配置说明](https://shimo.im/docs/5bqnroJYDbU4rGqy/)配置`Python3`基础开发环境，并在`/qinse/V2RaycSpider<version>`目录下执行`pip`命令拉取项目依赖：

```bash
# 拉取依赖
pip install -r /qinse/V2RaycSpider1125/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

若启动项目后出现`ModuleNotFound`的报错，可能原因是部分第三方库并未放入`requirements.txt`中，缺啥补啥既可，参考代码如下：

```bash
# pip 安装第三方库 pip install <the name of missing package> ，如：
pip install pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2.1.4 配置chromedriver

根据[环境配置说明](https://shimo.im/docs/5bqnroJYDbU4rGqy/)安装`google-chrome`、对应版本的`chromedriver`，在`Linux`服务器中需要给予`文件权限 -> [ √ ]执行`。

- 若您正在使用`Finalshell`l或`Xshell/Xftp`等服务器远程登录方案， <kbd>右键</kbd>目标文件 -><kbd>点击</kbd>`文件权限`既可给予**执行权限**；
- 将`ChromeDriver`文件放到指定目录下：
  - `Windows`:`X:/qinse/V2RaycSpider1125/BusinessCentralLayer/chromedriver.exe`
  - `Linux` or `Mac`:`/qinse/V2RaycSpider1125/BusinessCentralLayer/chromedriver`

### 2.2 将李芬特装入冰箱

[全局配置文件](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2RaycSpider1125/config.py) || 配置项目启动参数以及服务器资源。

#### 2.2.1 guider脚手架调试接口

#### 2.2.2 高级配置

- 微服务
- 消息队列
- 单元测试
- 前后端分离开发

### 2.2 关闭冰箱门

[程序全局接口](https://github.com/QIN2DIM/V2RayCloudSpider/blob/master/V2RaycSpider1125/main.py) || 通过脚手架调试或启动项目。

- 运行`main.py`（脚手架接口）启动项目；

- 服务器后台运行；

  - （推荐）搭配`tmux`使用，详见[Tmux 使用教程 - 阮一峰的网络日志 (ruanyifeng.com)](http://www.ruanyifeng.com/blog/2019/10/tmux.html)
  - 使用原生机制部署

```bash
# CentOS7 部署
nohup python3 /qinse/V2RaycSpider1125/main.py deploy &
```

## 三、其他设置

> 以上设置均在`main.py`以及`config.py`文件中有详细说明，遇到问题请自行检索或通过`issue/email`给作者留言。

（更新中...）