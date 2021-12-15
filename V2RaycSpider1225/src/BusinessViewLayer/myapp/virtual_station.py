# for windows scaffold ash
__all__ = ["app"]

from flask import Flask, request, jsonify

from BusinessCentralLayer.setting import CHROMEDRIVER_PATH
from BusinessLogicLayer.utils.armour import apis_get_verification_code, apis_get_email_context

app = Flask(__name__)


@app.route("/get_email", methods=["GET"])
def get_email():
    context = apis_get_email_context(chromedriver_path=CHROMEDRIVER_PATH, silence=False)
    return jsonify({"status": "ok", "context": context})


@app.route("/get_email_code", methods=["POST"])
def get_email_code():
    context = dict(request.form)
    link = context.get("link", "")
    if link.startswith("https://"):
        driver = context.get("driver")
        verification_code = apis_get_verification_code(chromedriver_path=CHROMEDRIVER_PATH, link=link, driver=driver,
                                                       silence=True)
        context["email_code"] = verification_code
        return jsonify({"status": "ok", "context": context, "email_code": verification_code})
    return jsonify({"status": "failed", "context": context, "email_code": ""})


# if __name__ == "__main__":
#     app.run(port=8847)
