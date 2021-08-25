# -*- coding: utf-8 -*-
# Time       : 2021/8/2 22:30
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from datetime import datetime
from urllib.parse import urlparse

from src.BusinessCentralLayer.middleware.redis_io import RedisClient
from src.BusinessCentralLayer.setting import GARDENER_HOST, REDIS_SECRET_KEY, TIME_ZONE_CN
from src.BusinessLogicLayer.gardener import GardenerServer


class GardenerAPI:
    def __init__(self, debug=True, secret_key=None):
        self.debug = debug
        self.gardener = GardenerServer()
        self.dns_host = GARDENER_HOST
        # 限权
        self.permission = {
            'create': True,
            'read': False,
            'update': False,
            'survive': False,
            'delete': None
        }
        self.SCKEY_PATH_ROOT = "v2rayc_users:{}"
        self.secret_key = "main" if secret_key is None else secret_key
        self._check_permission(self.secret_key)

    def _check_permission(self, sckey):
        sckey_path = self.SCKEY_PATH_ROOT.format(sckey)
        rc = RedisClient().get_driver()
        if rc.exists(sckey_path):
            if rc.hget(sckey, key="SURVIVE") == "True":
                self.permission['crate'] = False
                self.permission['read'] = True
                self.permission['update'] = True
                self.permission['survive'] = True
                self.permission['delete'] = True
            else:
                self.permission['delete'] = False
        else:
            self.permission['delete'] = False

    def register_auth(self, sckey):
        """

        :param sckey: db_token
        :return:
        """
        sckey_path = self.SCKEY_PATH_ROOT.format(sckey)
        driver = RedisClient().get_driver()
        driver.hset(sckey_path, key="CREATE", value=str(datetime.now(TIME_ZONE_CN)))
        driver.hset(sckey_path, key="READ", value="None")
        driver.hset(sckey_path, key="UPDATE", value="None")
        driver.hset(sckey_path, key="DELETE", value="True")
        driver.hset(sckey_path, key="SURVIVE", value="True")

    @staticmethod
    def remove_auth(sckey):
        RedisClient().get_driver().hset(sckey, key="SURVIVE", value="False")

    def load_subs_set(self, sub_type):
        subs_mapping = {}
        for sub, _ in RedisClient().sync_remain_subs(REDIS_SECRET_KEY.format(sub_type)):
            subs_mapping.update({urlparse(sub).netloc: sub})
            # not debug 移除池中订阅
            if not self.debug:
                RedisClient().get_driver().hdel(REDIS_SECRET_KEY.format(sub_type, sub))
        subs = list(subs_mapping.values())
        return subs

    def create_gardener(self, sub_type):
        """
        v2ray-subs --拆包--> 节点列表  --清洗--> new节点列表 --↓
        ssr-subs --拆包--> 节点列表  --清洗--> new节点列表 --> 组包 --生成Token--> 返回节点集群
        :return:
        """

        # subs --parse--> nodes
        subs = self.load_subs_set(sub_type)
        node_group = [feature for feature in self.gardener.subscribe_unzip(subs, sub_type) if feature[-1]]
        # Sub[SubNodes1[...], SubNodesN[...], ...] --splicer--> Sub[Nodes[...]]
        sub_classic = self.gardener.node_splicer(node_group)
        # Sub[Nodes[...]] --embed--> Gardener[Nodes[...]]
        sub_gardener = self.gardener.embed_token(sub_type=sub_type, dns_host=self.dns_host, sub_group=sub_classic)

        # Linux 系统下创建代理路径
        _path = sub_gardener.get("path")
        nodes = sub_gardener.get("nodes")
        self.gardener.create_memory(db_token=_path, db_type=sub_type, nodes=nodes)

        return sub_gardener
