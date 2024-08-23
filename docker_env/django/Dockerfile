# 构建阶段
FROM python:3.12-alpine as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 复制必要文件
COPY requirements.txt .

# 安装构建依赖
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache \
        bash \
        git \
        freetds-dev \
        jpeg-dev \
        linux-headers \
        mysql-client \
        mariadb-dev \
        build-base \
        libffi-dev \
        openssl-dev \
        zlib-dev \
        bzip2-dev \
        pcre-dev \
        ncurses-dev \
        readline-dev \
        tk-dev \
        postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt

# 最终阶段
FROM python:3.12-alpine as final

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 从构建阶段复制 Python 环境
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制所有项目文件
COPY . .

# 修改配置文件并设置权限，安装必要的运行时依赖
RUN cp configs/.env.example configs/.env && \
    sed -i 's/DATABASE_HOST=.*/DATABASE_HOST=host.docker.internal/g' configs/.env && \
    sed -i 's/REDIS_HOST=.*/REDIS_HOST=djangox-redis/g' configs/.env && \
    apk add --no-cache bash mysql-client && \
    chmod +x start_service.sh && \
    mkdir -p logs static media && \
    chmod 777 logs static media && \
    # 清理缓存和不必要的文件
    find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + && \
    pip cache purge && \
    rm -rf /root/.cache /tmp/*

EXPOSE 8000

CMD ["./start_service.sh"]