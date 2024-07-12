# At the top of your settings.py file
import os
from dotenv import load_dotenv
from django.conf import settings

# Load the .env file
load_dotenv()

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ================================================= #
# ************** mysql数据库 配置  ************** #
# ================================================= #
# 数据库地址
DATABASE_ENGINE = "django.db.backends.mysql"
# 数据库地址
DATABASE_HOST = "127.0.0.1"
# 数据库端口
DATABASE_PORT = 3306
# 数据库用户名
DATABASE_USER = "root"
# 数据库密码
DATABASE_PASSWORD = "root"
# 数据库名
DATABASE_NAME = "lyadmin_db"
# 数据库编码
DATABASE_CHARSET = "utf8mb4"
# 数据库长连接时间（默认为0，单位秒）即每次请求都重新连接,debug模式下该值应该写为0 ，mysql默认长连接超时时间为8小时
DATABASE_CONN_MAX_AGE = 0  # 推荐120（2分钟），使用 None 则是无限的持久连接（不推荐）。

# ================================================= #
# ************** redis 配置  ************** #
# ================================================= #

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:{REDIS_PORT}'

# ================================================= #
# ************** 服务器基本 配置  ************** #
# ================================================= #
DEBUG = True  # 是否调试模式
IS_DEMO = False  # 是否演示模式（演示模式只能查看无法保存、编辑、删除、新增）
IS_SINGLE_TOKEN = False  # 是否只允许单用户单一地点登录(只有一个人在线上)(默认多地点登录),只针对后台用户生效
ALLOW_FRONTEND = True  # 是否关闭前端API访问
DOMAIN_HOST = os.getenv('DOMAIN_HOST', "http://127.0.0.1:8000")

# ================================================= #
# **************   日志基本 配置  ************** #
# ================================================= #
# loguru
lOG_FOLDER = "logs/"
LOG_ROTATION = "100 MB"
LOG_RETENTION = "30 days"
LOG_ENCODING = "utf-8"
LOG_BACKTRACE = True
LOG_DIAGNOSE = True
LOG_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> ' \
             '| <magenta>{process}</magenta>:<yellow>{thread}</yellow> ' \
             '| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<yellow>{line}</yellow> - <level>{message}</level>'
