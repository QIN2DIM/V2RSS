FROM python:3.9-slim as runner

# 设置 container 工作目录，若不存在自动初始化
WORKDIR /qinse

# 拷贝依赖文件并为虚拟环境安装依赖
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 拷贝源码，将 src 目录下的文件拷贝到 docker:/qinse
COPY src ./

# 拼写脚手架前缀
ENTRYPOINT [ "python", "./main.py"]

# 删除中间缓存
# docker container prune && docker image prune && docker images

# 清空本地镜像
# docker container prune && docker image rm -f $(docker image ls -aq) && docker images