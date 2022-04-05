# -*- coding: utf-8 -*-
# Time       : 2022/1/9 14:12
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import sys

sys.path.append("src")
from services.app.server.app import app

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=6505,
        debug=True,
        auto_reload=False,
        access_log=True,
        workers=os.cpu_count(),
    )
