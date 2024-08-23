#!/bin/sh
set -e

# 等待 MySQL 就绪
until nc -z djangox-mysql 3306; do
  echo "Waiting for MySQL to be ready..."
  sleep 2
done

# 等待 Redis 就绪
until nc -z djangox-redis 6379; do
  echo "Waiting for Redis to be ready..."
  sleep 2
done

echo "正在创建数据库迁移..."
python manage.py makemigrations

echo "正在应用数据库迁移..."
python manage.py migrate

echo "正在启动 Uvicorn 服务器..."
uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 4