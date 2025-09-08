FROM python:3.11-slim

# 安装 uv
RUN pip install --no-cache-dir uv

# 运行用户与工作目录
WORKDIR /app

# 先拷贝依赖清单，利用缓存层
COPY requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt

# 再拷贝代码与测试
COPY app ./app
COPY tests ./tests
COPY pytest.ini ./pytest.ini

# 对外端口（API/Flower）
EXPOSE 8000 5555

# 默认命令让 compose 覆盖；单容器运行可直接起 uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]