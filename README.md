# DjangoX 🚀

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/tao-xiaoxin/DjangoX/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-%3E=3.8.x-green.svg)](https://python.org/)
[![Django Version](https://img.shields.io/badge/django%20versions-%3E=5.1-blue)](https://docs.djangoproject.com/zh-hans/)
[![GitHub stars](https://img.shields.io/github/stars/tao-xiaoxin/DjangoX.svg?style=social&label=Star)](https://github.com/tao-xiaoxin/DjangoX)
[![GitHub forks](https://img.shields.io/github/forks/tao-xiaoxin/DjangoX.svg?style=social&label=Fork)](https://github.com/tao-xiaoxin/DjangoX)

DjangoX 是一个强大的 Django 项目模板，旨在加速 Django Web 应用程序的开发过程。支持 **Python 3.8** 及以上版本，DjangoX 为您的项目提供了坚实的基础和一系列预配置的常用组件。

## 🌟 特性

- ✅ Pytest 单元测试
- ✅ 全局自定义时区时间
- 🚧 Celery 异步任务 (开发中)
- 🚧 Docker / Docker-compose 部署 (开发中)
- 🚧 CI/CD 集成 (开发中)

## 🛠️ 内置功能

1. ✅ 登录认证：图形验证码认证登录
2. ✅ 接口文档：自动生成在线交互式 API 接口文档
3. ✅ 操作日志：系统正常和异常操作的日志记录与查询
4. ✅ 登录日志：用户正常和异常登录的日志记录与查询
5. ✅ 单点登录：JWT 中间件单点登录认证
6. 🚧 服务监控：服务器硬件设备信息与状态 (开发中)
7. 🚧 定时任务：自动化任务，异步任务，支持函数调用 (开发中)
8. ✅ 反爬验证：强悍的反爬签名验证算法，防止爬虫

## 🖥️ 本地开发环境要求

* 💻 Python 3.10+
* 🗄️ MySQL 8.0+
* 🚀 Redis (推荐最新稳定版)
* 🎨 Django 4.0+

## 🚀 快速开始

### 安装

1. 克隆仓库:
   ```bash
   git clone https://github.com/tao-xiaoxin/DjangoX.git
   ```
2. 进入项目目录:
   ```bash
   cd DjangoX
   cp configs/.env.example configs/.env
   ```
3. 安装依赖包:
   ```bash
   pip install -r requirements.txt
   ```
4. 应用数据库迁移:
   ```bash
   python manage.py migrate
   ```
5. 运行开发服务器:
   ```bash
   python manage.py runserver
   ```

### 自定义脚本

#### 快速生成用户token
```bash
python manage.py runscript generate_token --script-args <用户ID>
```

#### 在APPS下创建APP
```bash
python manage.py runscript create_app --script-args <app_name>
```

## ⚙️ 配置

- **密钥**: 请确保更改 `settings.py` 中的 `SECRET_KEY` 以用于生产环境。
- **数据库**: 在 `settings.py` 和 `.env` 文件中的 "数据库" 部分配置数据库设置。
- **静态和媒体文件**: 为生产环境设置静态和媒体文件的路径和存储方式。

## 📘 文档

详细的文档正在编写中。敬请期待！

## 🤝 贡献

我们欢迎所有形式的贡献！无论是新功能、bug 修复还是文档改进。请按照以下步骤提交您的贡献：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 将您的改动推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### Commit 指南

我们使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 规范来使 commit 信息更加规范和易读。每个 commit 消息都应该遵循以下格式：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

类型可以是以下之一：

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式修改，不影响代码含义的更改（空格、格式化、缺少分号等）
- `refactor`: 代码重构（既不修复错误也不添加功能）
- `perf`: 性能优化
- `test`: 添加缺失的测试或更正现有的测试
- `chore`: 对构建过程或辅助工具和库的更改（例如文档生成）

例如：

```
feat(auth): 添加用户登录功能

实现了基于 JWT 的用户登录系统，包括：
- 用户名和密码验证
- JWT token 生成
- 刷新 token 机制

Closes #123
```

请确保您的 commit 消息清晰、简洁，并准确描述了您所做的更改。这将帮助其他贡献者更好地理解您的工作，并使项目维护变得更加容易。

更多详细信息，请查看我们的 [贡献指南](CONTRIBUTING.md)。

## 📄 许可证

本项目遵循 [MIT 许可证](https://github.com/tao-xiaoxin/DjangoX/blob/main/LICENSE) 的条款进行许可。

## 📊 项目统计

[![Stargazers over time](https://starchart.cc/tao-xiaoxin/DjangoX.svg?variant=adaptive)](https://starchart.cc/tao-xiaoxin/DjangoX)

## 📞 联系我们

如果您有任何问题或建议，请随时 [创建一个 issue](https://github.com/tao-xiaoxin/DjangoX/issues) 或通过 [我的 GitHub 主页](https://github.com/tao-xiaoxin) 联系我。

---

💖 感谢使用 DjangoX！如果您觉得这个项目有帮助，请考虑给它一个星标 ⭐️