# V2RayCloudSpider
### Intro

- 运行`V2Ray云采姬.exe` 即可启动云端爬虫采集VMess订阅连接
- `main.py`为单节点爬虫，垂(自)直(杀)设计的selenium脚本，可供参考。

### Quick start

#### 快速使用VMess教程（以Windows为例）

- 下载项目
  - ![image-20200603082931751](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603082931751.png)
- 解压文件
  - ![image-20200603083200572](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603083332469.png)
- 如果开启了**防火墙**，会弹出提示
  - ![image-20200603083409156](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603083443714.png)
  - ![image-20200603083459425](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603083459425.png)
- 如果运行正常，应该会弹出主界面
  - ![image-20200603083534702](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603083559698.png)
- 点击<kbd>OK</kbd> 运行脚本，抓取过程约3s，因本地网络状况有所波动。
  - 如果运行正常，脚本会**弹出提示框**，显示VMess订阅连接。
    - ![image-20200603084125537](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603084125537.png)
  - 如果运行正常，脚本会**自动向剪贴板中写入VMess订阅连接**，<kbd>Ctrl</kbd> + <kbd>V</kbd> 即可粘贴文本。
  - 如果运行正常，脚本会自动在`C://V2Rray云采姬//`文件夹中**生成记事本文件**。
    - ![记事本](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603083718415.png)

抓取得VMess订阅连接往往仅**24小时有效**，重复运行脚本即可。

#### 如何使用VMess订阅连接？（以Windows为例）

- 使用**V2rayN-Core**[->点击下载](https://shimo.im/docs/68xjTGW8cdYV98Kk/ )
- 解压后，打开`.exe客户端`
  - ![ ](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603084745322.png)
- 在图形界面菜单栏，点击`订阅`、`订阅设置`。在弹出的`订阅设置面板`中，将`VMess订阅连接`填入**地址 (url)**中
  - ​        ![img](https://uploader.shimo.im/f/WJBHwn9V7mkQtMvY.png!thumbnail)              ![img](https://uploader.shimo.im/f/KtegDQ4avdQMVC0P.png!thumbnail)      
- 保存设置后，点击第3步的`更新订阅`,等待节点刷新。刷新成功后可能会显示以下节点
  - ![image-20200603085245707](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603085245707.png)
- 随便选中一个，<kbd>Enter</kbd>激活节点。（节点也许不可用，多试几个）
  - ![image-20200603085440370](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603085440370.png)
- 选中后<kbd>右键</kbd> 客户端缩略图，开启`Http代理`，选择`代理模式`，优先选择`PAC模式`
  - ![image-20200603085637063](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603085637063.png)
    - **全局代理(自动配置系统代理)**：所有网络统一使用混淆指令（确信）
    - **PAC代理(自动配置系统代理)**：只有在访问zh大陆无法访问的网站时才使用代理。（可能）
- 如果到此一切顺利，**即可顺利访问 Google Scholar**
  - ![image-20200603090008269](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603090008269.png)

#### 问题总结

- 下载V2RayN-客户端后，先更新客户端
  - ![image-20200603090138564](C:\Users\47159\AppData\Roaming\Typora\typora-user-images\image-20200603090138564.png)
- 选择节点代理后**无法访问网站**，选其他的节点试试。
- 退出程序时记得**关闭Http代理**，否则重启后不打开这个软件就没法上网了。



#### [其他系统使用V2Ray](https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%90%84%E5%B9%B3%E5%8F%B0%E5%9B%BE%E6%96%87%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B)

