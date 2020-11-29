__all__ = ['app']

from flask import request, Flask, jsonify, redirect
from BusinessViewLayer.myapp.apis import *
from config import ROUTE_API, SERVER_PATH_DEPOT_VCS

app = Flask(__name__)


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
        return "{}".format(apis_version_manager(SERVER_PATH_DEPOT_VCS)).encode("utf8")
    elif request.method == 'POST':
        return jsonify(apis_version_manager(SERVER_PATH_DEPOT_VCS, dict(request.form).get('local_version', False)))


@app.route('/spider', methods=['GET'])
def parse_header():
    return jsonify({'ip': request.environ.get('HTTP_X_REAL_IP', request.remote_addr)}), 200


@app.route("/", methods=['GET'])
def redirect_to_my_blog():
    return redirect("https://www.qinse.top/v2raycs/")
