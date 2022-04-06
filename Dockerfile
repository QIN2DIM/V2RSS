FROM python:3.10-slim as builder

WORKDIR /home/v2rss

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update -y \
    && apt install -y wget ffmpeg

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y ./google-chrome-stable_current_amd64.deb \
    && rm ./google-chrome-stable_current_amd64.deb

COPY src ./

# -------------------------------------------------------------
# 删除中间缓存
# -------------------------------------------------------------
# docker container prune && docker image prune && docker images

# -------------------------------------------------------------
# 推送
# -------------------------------------------------------------
# 登陆账号
# docker login
# 清空本地镜像
# docker container prune && docker image rm -f $(docker image ls -aq) && docker images
# 创建镜像并打上标签
# docker build -t v2rss:daddy . && docker tag v2rss:daddy ech0sec/v2rss:daddy
# 推送至   Docker Hub
# docker push ech0sec/v2rss:daddy

# 一键推送
# docker container prune && docker image rm -f ech0sec/v2rss:daddy && docker build -t v2rss:daddy . && docker tag v2rss:daddy ech0sec/v2rss:daddy && docker push ech0sec/v2rss:daddy

# 一键部署
# ssh-keygen -t ed25519 -C "your_email@example.com"
# git clone git@github.com:QIN2DIM/v2rss-alpha.git && cd ./v2rss-alpha/src && chmod +x ./BusinessCentralLayer/chromedriver && python3 main.py synergy