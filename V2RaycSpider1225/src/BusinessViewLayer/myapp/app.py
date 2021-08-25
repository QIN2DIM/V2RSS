__all__ = ['app']

from flask import request, Flask, jsonify, redirect

from src.BusinessCentralLayer.setting import ROUTE_API
from src.BusinessViewLayer.myapp.apis import apis_capture_subscribe, apis_version_manager, apis_get_subs_num, \
    apis_admin_get_subs, apis_admin_get_subs_v2, apis_admin_get_subs_v2_debug, apis_admin_get_entropy

app = Flask(__name__)


# ===========================================================
# Public Interface
# ===========================================================
@app.route(ROUTE_API['capture_subscribe'], methods=['POST'])
def capture_subscribe():
    """
    > 将Redis缓冲区链接作为备用链接返回
    @return: AnyType subscribe
    """
    return jsonify(apis_capture_subscribe(dict(request.form)))


@app.route(ROUTE_API['version_manager'], methods=['GET', 'POST'])
def version_manager():
    """
    > 版本管理,检查更新
        1.管理文档树，记录各个版本文件的服务器路径
        2.检查更新，记录最新版本号及最新版本文件存放地址
    @return:
        --GET:str
            --response = 'latest version'
        --POST:dict
            --response.keys=[msg:str, version-server:str, version-usr:str, url:str, need_update:bool]
    """
    if request.method == 'GET':
        return jsonify(apis_version_manager())
    if request.method == 'POST':
        return jsonify(apis_version_manager(usr_version=dict(request.form).get('local_version', False)))


@app.route("/", methods=['GET'])
def redirect_to_my_blog():
    return redirect("https://github.com/QIN2DIM/V2RayCloudSpider")


@app.route(ROUTE_API['get_subs_num'], methods=['GET'])
def get_subs_num():
    return jsonify(apis_get_subs_num())


# ===========================================================
# Admin Interface
# ===========================================================
from uuid import uuid4

_private_interface = "Fill in your own private interface"


# ----------------------------------
# 随机获取某个类型的订阅 v1
# ----------------------------------
@app.route(f"/super_admin/{uuid4()}/<command_>", methods=['GET'])
def admin_get_subs(command_):
    return jsonify(apis_admin_get_subs(command_))


# ----------------------------------
# 获取指定netloc/domain的订阅 v1
# ----------------------------------
@app.route(f"/super_admin/{uuid4()}/debug/<_entropy_name>", methods=['GET'])
def admin_get_subs_v2_debug(_entropy_name):
    """获取/debug"""
    return jsonify(apis_admin_get_subs_v2_debug(entropy_name=_entropy_name, _debug=True))


@app.route(f"/super_admin/{uuid4()}/<_entropy_name>", methods=['GET'])
def admin_get_subs_v2(_entropy_name):
    """获取/general"""
    return jsonify(apis_admin_get_subs_v2(entropy_name=_entropy_name))


@app.route(f"/super_admin/{uuid4()}", methods=['GET'])
def admin_select_subs():
    """查询/general"""
    return jsonify(apis_admin_get_subs_v2_debug(entropy_name=None))


# ----------------------------------
# 获取正在活动的任务队列
# ----------------------------------
@app.route(f"/super_admin/{uuid4()}", methods=['GET'])
def admin_get_entropy():
    return jsonify(apis_admin_get_entropy())

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=6500, debug=True)
