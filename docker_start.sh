#!/bin/bash

set -e

# 设置变量
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DOCKER_ENV_DIR="$PROJECT_DIR/docker_env"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
ENV_FILE="$PROJECT_DIR/configs/.env"
ENV_EXAMPLE="$PROJECT_DIR/configs/.env.example"

# 创建必要的目录结构
mkdir -p "$DOCKER_ENV_DIR/mysql/data" "$DOCKER_ENV_DIR/mysql/conf.d" "$DOCKER_ENV_DIR/mysql/logs"
mkdir -p "$DOCKER_ENV_DIR/redis/data"

# 检查 Redis 配置文件是否存在
REDIS_CONF="$DOCKER_ENV_DIR/redis/redis.conf"
if [ ! -f "$REDIS_CONF" ]; then
    echo "Error: Redis configuration file not found at $REDIS_CONF"
    echo "Please create the Redis configuration file before running this script."
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install it first."
    exit 1
fi

# 检查 docker-compose.yml 文件是否存在
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: docker-compose.yml file not found at $COMPOSE_FILE"
    exit 1
fi

# 检查并创建 .env 文件
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "Created .env file from .env.example. Updating configuration..."

        # 更新数据库和 Redis 配置
        sed -i 's/DATABASE_HOST=.*/DATABASE_HOST="djangox-mysql"/g' "$ENV_FILE"
        sed -i 's/REDIS_HOST=.*/REDIS_HOST="djangox-redis"/g' "$ENV_FILE"

        # 设置固定的 MySQL 密码和空的 Redis 密码
        sed -i 's/DATABASE_PASSWORD=.*/DATABASE_PASSWORD="456123"/g' "$ENV_FILE"
        sed -i 's/REDIS_PASSWORD=.*/REDIS_PASSWORD=""/g' "$ENV_FILE"

        echo "Updated DATABASE_HOST, REDIS_HOST, and set passwords in .env file."
        echo "MySQL password: 456123"
        echo "Redis password: [empty]"
    else
        echo "Error: .env.example file not found at $ENV_EXAMPLE. Please create this file with the necessary configuration."
        exit 1
    fi
fi

# 加载环境变量
set -a
# 使用 Python 来处理复杂的环境变量格式
python3 - <<END
import os
import re

env_file = "$ENV_FILE"
with open(env_file, 'r') as f:
    content = f.read()

# 使用正则表达式匹配键值对
pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)$', re.MULTILINE | re.DOTALL)

for match in pattern.finditer(content):
    key, value = match.groups()
    # 去除值两端的引号（如果存在）
    value = value.strip().strip('\'"')
    # 对于列表类型的值，保持其格式
    if value.startswith('[') and value.endswith(']'):
        value = value.replace('\n', ' ')  # 移除换行符
    os.environ[key] = value

print("Environment variables loaded successfully.")
END
set +a

# 确保关键环境变量已设置
export MYSQL_PASSWORD="456123"
export REDIS_PASSWORD=""

# 停止并删除所有相关的容器
echo "Stopping and removing existing containers..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans

# 删除所有相关的镜像
echo "Removing existing images..."
docker-compose -f "$COMPOSE_FILE" config --services | xargs -I {} docker rmi {}:latest || true

# 构建新的镜像
echo "Building new images..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

# 启动所有服务
echo "Starting all services defined in docker-compose.yml..."
docker-compose -f "$COMPOSE_FILE" up -d

# 检查服务是否成功启动
if [ $? -eq 0 ]; then
    echo "All services have been started successfully."
    echo "Running containers:"
    docker-compose -f "$COMPOSE_FILE" ps

    echo ""
    echo "Connection Information (for internal container communication):"
    echo "MySQL: djangox-mysql:3306"
    echo "Redis: djangox-redis:6379"
    echo "Django Server: djangox-server:8000"

    echo ""
    echo "To access services from your host machine:"
    echo "MySQL: localhost:3306"
    echo "Redis: localhost:6379"
    echo "Django Server: localhost:8000"

    echo ""
    echo "Database Credentials:"
    echo "MySQL password: 456123"
    echo "Redis password: [empty]"
else
    echo "Error: Failed to start services. Check the logs for more information."
    exit 1
fi

# 显示容器日志
echo "Showing container logs (press Ctrl+C to exit):"
docker-compose -f "$COMPOSE_FILE" logs -f