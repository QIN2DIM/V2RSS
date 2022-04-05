# -*- coding: utf-8 -*-
# Time       : 2022/1/1 3:34
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: Telegram Bot 历史性对话

"""
STEP01: 拉取依赖
----------------------------------
``pip install telethon python_socks async_timeout``
"""
from telethon import TelegramClient, events

"""
STEP02: 获取 API-ID 以及 API-HASH
----------------------------------
访问 https://my.telegram.org/auth 依据页面提示进行操作既可
"""
api_id: int = 00000000
api_hash: str = "xxx"

"""
STEP03: 设置本地代理
----------------------------------
proxy_type within ["http", "socks5"] http==3 socks5==2
"""
proxy = {"proxy_type": 3, "addr": "127.0.0.1", "port": 10809}

"""
STEP04: 获取Bot API-TOKEN
----------------------------------
通过 The BotFather 申请一个机器人，并获取其 API-TOKEN。程序运行前会要求输入【Your Phone / Bot Token】
"""

"""
STEP05: 完成 Telegram Bot 的历史性对话
----------------------------------
此段代码的效果是，你向机器人发送包含「hello」（大小写不敏感）的字符串，它会回复你「Hey!」
> human: hello --> relay: Hey!
> human: Hello --> relay: Hey!
> human: OjbkhElLo --> relay: Hey!
"""
with TelegramClient("name", api_id, api_hash, proxy=proxy) as client:
    client.send_message("me", "Hello, myself!")
    print(client.download_profile_photo("me"))

    @client.on(events.NewMessage(pattern="(?i).*Hello"))
    async def handler(event):
        await event.reply("Hey!")

    client.run_until_disconnected()
