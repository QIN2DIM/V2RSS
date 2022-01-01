from os.path import join, dirname
from typing import Dict, Union
from uuid import uuid4

import pytz

from services.utils import ToolBox

"""
================================================ ʕ•ﻌ•ʔ ================================================
                            (·▽·)欢迎使用 V2RSS云彩姬，请跟随提示合理配置项目启动参数
================================================ ʕ•ﻌ•ʔ ================================================
[√]核心配置 [※]边缘参数
"""
config_ = ToolBox.check_sample_yaml(
    path_output=join(dirname(__file__), "config.yaml"),
    path_sample=join(dirname(__file__), "config-sample.yaml")
)
# --------------------------------
# [√]Redis node configuration
# --------------------------------
REDIS_NODE: Dict[str, Union[str, int]] = config_["REDIS_NODE"]

# --------------------------------
# [√]Subscription pool capacity
# --------------------------------
POOL_CAP: int = config_["POOL_CAP"]

# --------------------------------
# [√]Scheduled task configuration
# --------------------------------
SCHEDULER_SETTINGS: Dict[str, Union[int, bool]] = config_["scheduler"]

# --------------------------------
# [√]External API interface
# --------------------------------
_ROUTER_UUID: str = config_["router"]["uuid"]
ROUTER_API: Dict[str, str] = config_["router"]["apis"]
ROUTER_NAME: str = config_["router"]["name"]
ROUTER_HOST: str = config_["router"]["host"]
ROUTER_PORT: int = config_["router"]["port"]
"""
================================================== ʕ•ﻌ•ʔ ==================================================
                        如果您并非 - V2RSS云彩姬 - 项目开发者 请勿修改以下变量的默认参数
================================================== ʕ•ﻌ•ʔ ==================================================

                                            Enjoy it -> ♂ main.py
"""
# 时区
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")
TIME_ZONE_NY = pytz.timezone("America/New_York")

# 自动替换外部接口UUID的默认值
_ROUTER_UUID = str(uuid4()) if _ROUTER_UUID in ["", "v0"] else _ROUTER_UUID
# 将UUID嵌入到路由路径中
ROUTER_API = {ft: ROUTER_API[ft].format(_ROUTER_UUID) for ft in ROUTER_API.keys()}
