# 使用 Python 官方镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 拷贝当前目录下的所有文件到容器内的 /app 目录
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 ENTRYPOINT，指定容器启动时运行的命令
ENTRYPOINT ["python", "app/main.py"]
