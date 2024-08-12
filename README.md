# Djangox

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/tao-xiaoxin/DjangoX/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-%3E=3.8.x-green.svg)](https://python.org/)
[![Django Version](https://img.shields.io/badge/django%20versions-%3E=5.1-blue)](https://docs.djangoproject.com/zh-hans/)

Djangox 是一个基于 Django 的项目模板，旨在快速开发 Django Web 应用程序开发，支持 **python3.8** 及以上版本。

预配置了基本设置和一组常用的 Django 开发组件，为您的项目提供坚实的基础。

它的目的是让你可以直接用它作为你新项目的基础架构，本仓库作为模板库公开，任何人或企业均可免费使用

## 特征

- [x] Pytest 单元测试
- [x] 全局自定义时区时间
- [ ] Celery 异步任务
- [ ] JWT 中间件白名单认证
- [ ] Docker / Docker-compose 部署

## 内置功能

1. [x] 登录认证：图形验证码认证登录
2. [x] 接口文档：自动生成在线交互式 API 接口文档
2. [x] 操作日志：系统正常和异常操作的日志记录与查询
3. [x] 登录日志：用户正常和异常登录的日志记录与查询
4. [ ] 服务监控：服务器硬件设备信息与状态
5. [ ] 定时任务：自动化任务，异步任务，支持函数调用

## 本地开发

* Python 3.10+
* Mysql 8.0+
* Redis 推荐最新稳定版
* Django 4.0+

## 安装

1. Clone the repository:
   ```
   git clone https://github.com/tao-xiaoxin/DjangoX.git
   ```
2. Navigate to the project directory:
   ```
   cd DjangoX
   cp configs/.env.example configs/.env
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Apply the migrations:
   ```
   python manage.py migrate
   ```
5. Run the development server:
   ```
   python manage.py runserver
   ```
## 自定义脚本

### 快速生成用户token
```bash
 python manage.py runscript generate_token --script-args <用户ID>
```

### 在APPS下创建APP 
```bash
python manage.py runscript  create_app --script-args <app_name>
```
## 配置

- **密钥**：确保更改“settings.py”中的“SECRET_KEY”以供生产使用。
- **数据库**：在“数据库”部分下的“settings.py”和“.env”中配置数据库设置。
- **静态和媒体文件**：设置静态和媒体文件的路径和存储以进行生产。

## 许可证

本项目由 [MIT](https://github.com/tao-xiaoxin/DjangoX/blob/main/LICENSE) 许可证的条款进行许可

[![Stargazers over time](https://starchart.cc/tao-xiaoxin/DjangoX.svg?variant=adaptive)](https://starchart.cc/tao-xiaoxin/DjangoX)