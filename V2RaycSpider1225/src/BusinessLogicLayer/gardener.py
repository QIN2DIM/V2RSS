# -*- coding: utf-8 -*-
# Time       : 2021/8/2 19:11
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import base64
import csv
import os
import sys
from uuid import uuid4

from src.BusinessLogicLayer.plugins.accelerator.cleaner import subs2node


class GardenerServer:
    """多类型订阅节点的拆包组包，实现一对一，一对多的token用户订阅映射"""

    def __init__(self):
        self.field = None
        self.dns_host = None

        self.db_index_root = "/usr/share/nginx/html"
        self.db_index_usr = os.path.join(self.db_index_root, "v2rayc_users")

    @staticmethod
    def subscribe_unzip(subs: list or str, sub_type=None):
        if isinstance(subs, str):
            subs = [subs, ]
        for sub in subs:
            unzip_stream: dict = subs2node(sub)
            # 类型清洗，当传入的subs不确定类型时使用
            # 若使用，则仅会返回对应类型的链接
            if sub_type:
                info_tags = unzip_stream.get("info")
                if info_tags and info_tags.get("class_") == sub_type:
                    yield [sub, unzip_stream['node']]
                else:
                    yield [sub, []]
            else:
                yield [sub, unzip_stream['node']]

    @staticmethod
    def subscribe_clearing(node_unzip_stream: list or str):
        """

        :param node_unzip_stream: List[utf-8 str, ...]
        :return:
        """
        if isinstance(node_unzip_stream, str):
            node_unzip_stream = [node_unzip_stream, ]
        for desc in node_unzip_stream:
            return csv.DictReader(base64.b64decode(desc.split("://")[-1]))

    def create_memory(self, db_token, db_type, nodes: list):
        if 'linux' in sys.platform.lower():
            proxy_token = os.path.join(self.db_index_usr, db_token)
            proxy_type = os.path.join(proxy_token, f"{db_type}.txt")
            for path in [self.db_index_usr, proxy_token]:
                if not os.path.exists(path):
                    os.mkdir(path)
            with open(proxy_type, 'w', encoding="utf8") as f:
                for node in nodes:
                    f.write(f"{node}\n")

    @staticmethod
    def delete_memory(db_token, db_type):
        pass

    def embed_token(self, sub_type: str, dns_host: str, sub_group: dict):
        """
        :param sub_type:
        :param dns_host:
        :param sub_group:
        :return:
        """
        self.field = sub_type
        self.dns_host = dns_host

        _token = sub_group.get("token")
        _token_init = _token.format(dns_host, sub_type)
        sub_group.update(
            {
                'token': _token_init,
                _token_init: sub_group.get("nodes"),
                'sub_type': sub_type,
                'dns_host': dns_host,
            }
        )
        return sub_group

    def node_splicer(self, sub2node_group: list) -> dict:
        """

        :param sub2node_group:
        :return:
        """
        if isinstance(sub2node_group[0], str):
            sub2node_group = [sub2node_group, ]

        primary_token, _path = self._generate_token()
        primary = {
            'token': primary_token,
            'subs': [],
            'nodes': [],
            'path': _path.upper()
        }
        for url, nodes in sub2node_group:
            primary.update({url: nodes})
            primary['subs'].append(url)
            for node in nodes:
                primary['nodes'].append(node)
        # primary.update({primary_token: primary.get("nodes")})
        primary.update({'nodes_size': len(primary.get("nodes"))})
        return primary

    def rule_translate(self):
        pass

    @staticmethod
    def _generate_token():
        # format: DNS-HOST and SubscribeType
        _path = F"SEQ_{uuid4().hex}"
        return "https://{}/" + _path + "/{}", _path
