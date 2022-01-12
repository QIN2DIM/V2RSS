# FOR: sspanel

# [√]顶部需求1：输入链接输出运行配置
# VIEW-INPUT
# [1] 接收一个链接 --> 清洗掉意外的输入 --> 纯净的域名

# MID-LAYER-LOGIC
# [2] 纯净的域名 --(拼接)--> 功能链接 --> 测试 --> 分类 --> is_sspanel or others
#       <<- 接口设计 ->>
#       测试，如：sspanel，拼接出链接后测试 /staff 脚页是否ping通
#       分类，假设为 sspanel-malio
# [3] 纯净的 sspanel 注册链接 --> 对抗模组分类
#       调用 mining 模块细粒度分类
# [4] 模拟登录 --> 用户界面解析，萃取价值数据
#       假设为 sspanel-malio，优先区分是否为 ``prism`` 实例
#       价值数据：Title，Telegram群组链接
# [5] 使用类成员保存运行缓存

# MID-LAYER-VIEW
# [6] 生成预览页面 web-view
#       包含可更改项：
#           > 站点标题[input];
#           > 渲染主题[select]
#           > 对抗模式[multi-choice]
#           > 会员时长[input/h]
#           > 试用流量[input/GB]
#           > 订阅通道[表格映射]
#           > 实体摘要[多行文本];
#               ① 根据站点主题或二级域名拼写自动补全 ``name``  Action[{}]Cloud
#               ② 根据渲染主题分类确定 ``nest``
#               ③ 根据对抗模式确定超参数 ``hyper_params`` （注意区分 ``prism`` 模式）
#               ④ 根据会员时长确定 ``lifecycle``
#               ⑤ 根据站点标题确定顶部注释 <<- Info | Plan ->>
#               ⑥ 根据补全链接确定 ``register_url``;

# VIEW-OUTPUT
# 提供导出按钮，生成实体摘要文件，可供下载的 `.txt`
# 提供下载按钮，生成分析表格，保存 webio 数据 `.csv`

# EXCEPTIONS
# 异常情况则抛出相关异常，导出失败，或由用户手动指定


# [x]顶部需求2：导入格式化文本，批量检测
