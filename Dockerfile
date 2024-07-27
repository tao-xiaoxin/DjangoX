FROM python:3.10.12-bookworm as builder

WORKDIR /app

# 复制应用程序文件和requirements.txt并安装Poetry等依赖包
COPY . /app/
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple && \
    pip3 install --upgrade pip && \
    pip wheel --wheel-dir=/app/wheelhouse -r requirements.txt && \
    pip3 install poetry && \
    cd /app/lib/funcaptcha-challenger && \
    poetry build && \
    cp /app/lib/funcaptcha-challenger/dist/*.whl /app/wheelhouse/ && \
    cd /app && \
    pip3 install /app/wheelhouse/*.whl

# "运行"阶段，从"编译"阶段复制依赖文件，然后运行应用
FROM python:3.10.12-slim-bookworm as final

WORKDIR /app

# 复制应用程序文件到容器中
COPY --from=builder /app /app
COPY --from=builder /app/wheelhouse /wheelhouse

# 安装依赖包
RUN pip install -r /app/requirements.txt --no-index --find-links /app/wheelhouse && \
    rm -rf /wheelhouse

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8181
EXPOSE 8181

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]
