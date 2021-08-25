__all__ = ['api']

import base64
import json
import os

import requests
import yaml

from src.BusinessCentralLayer.setting import logger, SERVER_DIR_DATABASE_CACHE


class _ClashAdaptationInterface:
    """https://docs.cfw.lbyczf.com/"""

    def __init__(self, subscribe: list = None, debug: bool = False):
        self._rss_pool: list = subscribe
        self._debug: bool = debug
        self._PROXIES: dict = {"http": None, "https": None}

        # clash://install-config?url=<encoded URI>
        self.CLASH_URL_SCHEME = "clash://install-config?url={}"
        self.DEFAULT_CONFIG_URL = "https://cdn.jsdelivr.net/gh/Celeter/convert2clash@main/config.yaml"
        self.LOCAL_CONFIG_PATH = os.path.join(SERVER_DIR_DATABASE_CACHE, 'clash_config_temple.yaml')
        self.CLASH_CONFIG_YAML = os.path.join(SERVER_DIR_DATABASE_CACHE, 'clash_config.yaml')

    def _load_local_config(self, path: str) -> dict:
        try:
            with open(path, 'r', encoding='utf8') as f:
                local_config: dict = yaml.safe_load(f.read())
            return local_config
        except FileNotFoundError:
            self._debug_printer('配置文件加载失败')

    def _load_startup_config(self, url: str, path: str) -> dict:
        try:
            raw = requests.get(url, timeout=5, proxies=self._PROXIES).content.decode('utf-8')
            template_config = yaml.safe_load(raw)
        except requests.exceptions.RequestException:
            self._debug_printer('网络获取规则配置失败,加载本地配置文件')
            template_config = self._load_local_config(path)
        self._debug_printer('已获取规则配置文件')
        return template_config

    def _v2ray_to_yaml(self, arr: list) -> dict:
        self._debug_printer('v2ray节点转换中...')
        proxies = {
            'proxy_list': [],
            'proxy_names': []
        }
        for item in arr:
            if item.get('ps') is None and item.get('add') is None and item.get('port') is None \
                    and item.get('id') is None and item.get('aid') is None:
                continue
            obj = {
                'name': item.get('ps').strip() if item.get('ps') else None,
                'type': 'vmess',
                'server': item.get('add'),
                'port': int(item.get('port')),
                'uuid': item.get('id'),
                'alterId': item.get('aid'),
                'cipher': 'auto',
                'udp': True,
                # 'network': item['net'] if item['net'] and item['net'] != 'tcp' else None,
                'network': item.get('net'),
                'tls': True if item.get('tls') == 'tls' else None,
                'ws-path': item.get('path'),
                'ws-headers': {'Host': item.get('host')} if item.get('host') else None
            }
            for key in list(obj.keys()):
                if obj.get(key) is None:
                    del obj[key]
            if obj.get('alterId') is not None and not obj['name'].startswith('剩余流量') and not obj['name'].startswith(
                    '过期时间'):
                proxies['proxy_list'].append(obj)
                proxies['proxy_names'].append(obj['name'])
        self._debug_printer('可用v2ray节点{}个'.format(len(proxies['proxy_names'])))
        return proxies

    def _ssr_to_yaml(self, arr: list) -> dict:
        self._debug_printer('ssr节点转换中...')
        proxies = {
            'proxy_list': [],
            'proxy_names': []
        }
        for item in arr:
            obj = {
                'name': item.get('remarks').strip() if item.get('remarks') else None,
                'type': 'ssr',
                'server': item.get('server'),
                'port': int(item.get('port')),
                'cipher': item.get('method'),
                'password': item.get('password'),
                'obfs': item.get('obfs'),
                'protocol': item.get('protocol'),
                'obfs-param': item.get('obfsparam'),
                'protocol-param': item.get('protoparam'),
                'udp': True
            }
            for key in list(obj.keys()):
                if obj.get(key) is None:
                    del obj[key]
            if (
                    obj.get('name')
                    and not obj['name'].startswith('剩余流量')
                    and not obj['name'].startswith('过期时间')
            ):
                proxies['proxy_list'].append(obj)
                proxies['proxy_names'].append(obj['name'])
        self._debug_printer('可用ssr节点{}个'.format(len(proxies['proxy_names'])))
        return proxies

    def _generate_yaml(self, cache_path: str, config_content: dict) -> None:
        clash_yaml = yaml.dump(data=config_content, sort_keys=False, default_flow_style=False, encoding='utf-8',
                               allow_unicode=True)
        self._capture_yaml(cache_path=cache_path, cache_yaml=clash_yaml)
        self._debug_printer(f"成功更新{config_content['proxies']}个节点")

    @staticmethod
    def _capture_yaml(cache_path: str, cache_yaml: bytes) -> None:
        with open(cache_path, 'wb') as f:
            f.write(cache_yaml)

    def _debug_printer(self, msg: str) -> None:
        if self._debug:
            logger.debug(f"<ClashAdapter> | {msg}")

    @staticmethod
    def url_decode(url: str) -> bytes:
        num = len(url) % 4
        if num:
            url += '=' * (4 - num)
        return base64.urlsafe_b64decode(url)

    def _analyze_ssr(self, nodes: list) -> list:
        proxy_list = []
        for node in nodes:
            decode_proxy = node.decode('utf-8')[6:]
            if not decode_proxy or decode_proxy.isspace():
                self._debug_printer('ssr节点信息为空，跳过该节点')
                continue
            proxy_str = self.url_decode(decode_proxy).decode('utf-8')
            parts = proxy_str.split(':')
            if len(parts) != 6:
                logger.error('该ssr节点解析失败，链接:{}'.format(node))
                continue
            info = {
                'server': parts[0],
                'port': parts[1],
                'protocol': parts[2],
                'method': parts[3],
                'obfs': parts[4]
            }
            password_params = parts[5].split('/?')
            info['password'] = self.url_decode(password_params[0]).decode('utf-8')
            params = password_params[1].split('&')
            for p in params:
                key_value = p.split('=')
                info[key_value[0]] = self.url_decode(key_value[1]).decode('utf-8')
            proxy_list.append(info)
        return proxy_list

    def _analyze_v2ray(self, nodes: list) -> list:
        proxy_list = []
        for node in nodes:
            decode_proxy = node.decode('utf-8')[8:]
            if not decode_proxy or decode_proxy.isspace():
                self._debug_printer('vmess节点信息为空，跳过该节点')
                continue
            proxy_str = base64.b64decode(decode_proxy).decode('utf-8')
            proxy_dict = json.loads(proxy_str)
            proxy_list.append(proxy_dict)
        return proxy_list

    @logger.catch()
    def _analyze_rss(self) -> dict:
        headers = {'User-Agent': 'Clash For Python'}
        proxy_list = {
            'proxy_list': [],
            'proxy_names': []
        }
        for run_entity in self._rss_pool:
            self._debug_printer(run_entity)
            res = requests.get(url=run_entity, headers=headers, timeout=5, proxies=self._PROXIES)
            try:
                b64code_: bytes = base64.b64decode(res.text)
            except Exception as r:
                logger.exception(r)
                continue
            node_list = b64code_.splitlines()
            v2ray_urls = []
            ss_urls = []
            ssr_urls = []
            for node in node_list:
                if node.startswith(b'vmess://'):
                    v2ray_urls.append(node)
                elif node.startswith(b'ss://'):
                    ss_urls.append(node)
                elif node.startswith(b'ssr://'):
                    ssr_urls.append(node)
                else:
                    pass

            clash_node = {}
            if v2ray_urls.__len__() > 0:
                decode_proxy: list = self._analyze_v2ray(nodes=v2ray_urls)
                clash_node: dict = self._v2ray_to_yaml(arr=decode_proxy)
            elif ssr_urls.__len__() > 0:
                decode_proxy: list = self._analyze_ssr(nodes=ssr_urls)
                clash_node: dict = self._ssr_to_yaml(arr=decode_proxy)

            proxy_list['proxy_list'].extend(clash_node['proxy_list'])
            proxy_list['proxy_names'].extend(clash_node['proxy_names'])

        self._debug_printer(f"共发现:{proxy_list['proxy_names'].__len__()}个节点")
        return proxy_list

    def _generate_model(self, data: dict, model: dict) -> dict:
        self._debug_printer("正在生成配置文件...")

        try:
            # 参数清洗
            if model.get('proxies') is None:
                model['proxies'] = data.get('proxy_list')
            else:
                model['proxies'].extend(data.get('proxy_list'))
            # 更新模具
            for group in model.get('proxy-groups'):
                if group.get('proxies') is None:
                    group['proxies'] = data.get('proxy_names')
                else:
                    group['proxies'].extend(data.get('proxy_names'))
            return model
        except AttributeError as e:
            logger.exception(e)

    def url_scheme(self, mode: str = 'download'):
        if mode == 'download':
            return self.CLASH_URL_SCHEME
        if mode == 'quick':
            return "clash://quit"

    def run(self) -> None:
        # --------------------------------------------
        # 接口参数清洗
        # --------------------------------------------
        if not self._rss_pool:
            self._debug_printer("可解析参数为空")
            return None

        # --------------------------------------------
        # 执行核心业务
        # --------------------------------------------

        # 解析订阅源
        rss_pool = self._analyze_rss()

        # 获取Clash配置写法模板
        default_config = self._load_startup_config(url=self.DEFAULT_CONFIG_URL, path=self.LOCAL_CONFIG_PATH)
        response_config = self._generate_model(rss_pool, default_config)

        # 生成并缓存模板文件
        self._generate_yaml(cache_path=self.CLASH_CONFIG_YAML, config_content=response_config)

        # --------------------------------------------
        # 调试日志打印
        # --------------------------------------------
        # self._debug_printer(f"配置文件已导出 -- {self.CLASH_CONFIG_YAML}")
        logger.success(f"配置文件已导出 -- {self.CLASH_CONFIG_YAML}")

        return


class _Interface:

    @staticmethod
    def run(subscribe: list or str, debug=False) -> dict:
        if isinstance(subscribe, str):
            subscribe = [subscribe, ]
        _ClashAdaptationInterface(subscribe=subscribe, debug=debug).run()

        return {"msg": "success"}

    @staticmethod
    def url_scheme_download() -> dict:
        return {"msg": "success", "info": _ClashAdaptationInterface().url_scheme(mode='download')}

    @staticmethod
    def url_scheme_quick() -> dict:
        return {"msg": "success", "info": _ClashAdaptationInterface().url_scheme(mode='quick')}

    @staticmethod
    def load_clash_config_yaml_path():
        path: str = _ClashAdaptationInterface().CLASH_CONFIG_YAML
        if os.path.exists(path):
            return {"msg": "success", 'info': path}
        return {"msg": "failed"}


api = _Interface()
