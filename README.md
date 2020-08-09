# V2RayCloudSpider
## Intro

- 运行`V2Ray云采姬.exe` 即可启动云端爬虫采集VMess订阅连接
- `main.py`为单节点爬虫源码，垂(自)直(杀)设计的selenium脚本，可供参考。

## Quick start

如果**图片无法正常显示**，[点击跳转](https://shimo.im/docs/68xjTGW8cdYV98Kk/ )附件仓库

- V2ray接口已关闭，点击跳转查看SSR接口使用方案

### 快速使用VMess教程（以Windows为例）

- 下载项目

  [![tU8Gy6.md.png](https://s1.ax1x.com/2020/06/03/tU8Gy6.md.png)](https://imgchr.com/i/tU8Gy6)

- 解压文件

  ![tU8hfs.png](https://s1.ax1x.com/2020/06/03/tU8hfs.png)

- 如果开启了**防火墙**，会弹出提示

  [![tU8TXV.png](https://s1.ax1x.com/2020/06/03/tU8TXV.png)](https://imgchr.com/i/tU8TXV)	

  [![tU8o60.png](https://s1.ax1x.com/2020/06/03/tU8o60.png)](https://imgchr.com/i/tU8o60)

- 如果运行正常，应该会弹出主界面

  [![tU8q7F.png](https://s1.ax1x.com/2020/06/03/tU8q7F.png)	](https://imgchr.com/i/tU8q7F)

- 点击<kbd>OK</kbd> 运行脚本，抓取过程约3s，因本地网络状况有所波动。
  - 如果运行正常，脚本会**弹出提示框**，显示VMess订阅连接。

    [![t2sKP0.png](https://s1.ax1x.com/2020/06/07/t2sKP0.png)](https://imgchr.com/i/t2sKP0)
  - 如果运行正常，脚本会**自动向剪贴板中写入VMess订阅连接**，<kbd>Ctrl</kbd> + <kbd>V</kbd> 即可粘贴文本。
  - 如果运行正常，脚本会自动在`C://V2Rray云采姬//`文件夹中**生成记事本文件**。

    [![tU8Ok4.md.png](https://s1.ax1x.com/2020/06/03/tU8Ok4.md.png)](https://imgchr.com/i/tU8Ok4)

抓取得VMess订阅连接往往仅**24小时有效**，重复运行脚本即可。

### 如何使用VMess订阅连接？（以Windows为例）

- 使用**V2rayN-Core**[->点击下载](https://shimo.im/docs/68xjTGW8cdYV98Kk/ )
- 解压后，打开`.exe客户端`

  [![tU8z11.md.png](https://s1.ax1x.com/2020/06/03/tU8z11.md.png)](https://imgchr.com/i/tU8z11)
- 在图形界面菜单栏，点击`订阅`、`订阅设置`。在弹出的`订阅设置面板`中，将`VMess订阅连接`填入**地址 (url)**中

  ​        ![img](https://uploader.shimo.im/f/WJBHwn9V7mkQtMvY.png!thumbnail)              ![img](https://uploader.shimo.im/f/KtegDQ4avdQMVC0P.png!thumbnail)      
- 保存设置后，点击第3步的`更新订阅`,等待节点刷新。刷新成功后可能会显示以下节点

  [![tU8jh9.md.png](https://s1.ax1x.com/2020/06/03/tU8jh9.md.png)](https://imgchr.com/i/tU8jh9)
- 随便选中一个，<kbd>Enter</kbd>激活节点。（节点也许不可用，多试几个）

  [![tUGS6x.md.png](https://s1.ax1x.com/2020/06/03/tUGS6x.md.png)](https://imgchr.com/i/tUGS6x)
- 选中后<kbd>右键</kbd> 客户端缩略图，开启`Http代理`，选择`代理模式`，优先选择`PAC模式`

  [![tUGpX6.png](https://s1.ax1x.com/2020/06/03/tUGpX6.png)](https://imgchr.com/i/tUGpX6)	

  - **全局代理(自动配置系统代理)**：所有网络统一使用混淆指令（确信）
  - **PAC代理(自动配置系统代理)**：只有在访问zh大陆无法访问的网站时才使用代理。（可能）
- 如果到此一切顺利，**即可顺利访问 Google Scholar**

  [![tUGCnK.md.png](https://s1.ax1x.com/2020/06/03/tUGCnK.md.png)](https://imgchr.com/i/tUGCnK)

### 问题总结

- 下载V2RayN-客户端后，先更新客户端

  [![tUGP0O.md.png](https://s1.ax1x.com/2020/06/03/tUGP0O.md.png)](https://imgchr.com/i/tUGP0O)
- 选择节点代理后**无法访问网站**，选其他的节点试试。
- 退出程序时记得**关闭Http代理**。



### [其他系统使用V2Ray](https://www.v2ray.com/)

