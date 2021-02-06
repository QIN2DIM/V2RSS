__all__ = ['app']

from flask import request, Flask, jsonify, redirect

from BusinessCentralLayer.setting import ROUTE_API
from BusinessViewLayer.myapp.apis import *

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
        return jsonify(apis_version_manager())
    elif request.method == 'POST':
        return jsonify(apis_version_manager(usr_version=dict(request.form).get('local_version', False)))


@app.route("/", methods=['GET'])
def redirect_to_my_blog():
    return redirect("https://www.qinse.top/v2raycs/")


# 该接口用于<iOS捷径>订阅瞬时获取服务，暂不对Windows客户端开放
# 该接口用于<团队管理员>自取链接，不对外开放使用
@app.route("/super_admin/10963426-69f4-4495-96ba-de51e2b2036c/<command_>", methods=['GET'])
def admin_get_subs(command_):
    return jsonify(apis_admin_get_subs(command_))


@app.route(ROUTE_API['get_subs_num'], methods=['GET'])
def get_subs_num():
    return jsonify(apis_get_subs_num())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6500, debug=True)
