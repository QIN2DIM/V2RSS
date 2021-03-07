actions_template = {
    # 使用机场register-url作为key
    "url_template": {
        # 行为超参用于描述机场的高级抽象
        'hyper_params': {
            'v2ray': True,
            'ssr': False,
            'trojan': False,
            # 是否有验证模块(滑块验证)
            'anti': True
        },

    }
}

actions_queue = {
    [
        ['http://hxlm.org/', '火星联盟', ''],
    ]
}

# TODO 建立“公园系统”，允许“园丁”订阅与同步工作内容
