# for windows scaffold ash
__all__ = ['app']

from flask import Flask

app = Flask(__name__)


@app.route("/V2Ray云彩姬", methods=['GET'])
def virtual_station():
    from src.BusinessLogicLayer.plugins.breaker import clash_adapter
    with open(clash_adapter.api.load_clash_config_yaml_path()['info'], 'rb') as f:
        response = f.read()
    return response


if __name__ == '__main__':
    app.run(port=8847)
