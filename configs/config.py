# At the top of your settings.py file
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ================================================= #
# ******************** 动态配置 ******************** #
# ================================================= #
DEBUG = eval(os.getenv("DEBUG", 'True'))
ALLOWED_HOSTS = eval(os.getenv("ALLOWED_HOSTS", '["*"]'))
table_prefix = os.getenv("TABLE_PREFIX", "djangox_")  # 数据库表名前缀
DOMAIN_HOST = "http://127.0.0.1:8000"

# ================================================= #
# ************** mysql数据库 配置  ************** #
# ================================================= #
# 数据库地址
DATABASE_ENGINE = os.getenv("MYSQL_ENGINE", "django.db.backends.mysql")
# 数据库地址
DATABASE_HOST = os.getenv("DATABASE_HOST", "127.0.0.1")
# 数据库端口
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")
# 数据库用户名
DATABASE_USER = os.getenv("DATABASE_USER", "root")
# 数据库密码
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "UhKEh97+t35'N?m")
# 数据库名
DATABASE_NAME = os.getenv("DATABASE_NAME", "django_db")
# 数据库编码
DATABASE_CHARSET = os.getenv("DATABASE_CHARSET", "utf8mb4")
# 数据库长连接时间（默认为0，单位秒）即每次请求都重新连接,debug模式下该值应该写为0 ，mysql默认长连接超时时间为8小时
DATABASE_CONN_MAX_AGE = os.getenv("DATABASE_CONN_MAX_AGE", "0")  # 推荐120（2分钟），使用 None 则是无限的持久连接（不推荐）。

# ================================================= #
# ************** redis 配置  ************** #
# ================================================= #

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:{REDIS_PORT}'

# ================================================= #
# **************   日志基本 配置  ************** #
# ================================================= #
# log 文件夹
LOG_FOLDER = os.getenv('LOG_FOLDER', 'logs')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(levelname)s %(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d]'
                                     '[%(module)s:%(funcName)s] [%(levelname)s]- %(message)s')
# log file size,日志文件的最大值,这里我们设置300M
max_bytes = eval(os.getenv('LOG_MAX_BYTES', "1024 * 1024 * 300"))
# 备份份数
backup_count = os.getenv('LOG_BACKUP_COUNT', 10)

# ================================================= #
# ************** swagger 配置  ************** #
# ================================================= #
openapi_title = os.getenv("OPENAPI_TITLE", "DjangoX API")

# ================================================= #
# ************** 验证码 配置  ************** #
# ================================================= #
# 验证码有效时间
CAPTCHA_EXPIRE_TIME = eval(os.getenv("CAPTCHA_EXPIRE_TIME", 5))

# ================================================= #
# ****************** simplejwt配置 ***************** #
# ================================================= #

access_token_time = eval(os.getenv('ACCESS_TOKEN_LIFETIME', '7'))
refresh_token_time = eval(os.getenv('REFRESH_TOKEN_LIFETIME', '15'))

# ================================================= #
# ************** 其他配置  ************** #
# ================================================= #
API_LOG_ENABLE = eval(os.getenv('API_LOG_ENABLE', 'True'))
# API_LOG_METHODS = 'ALL' # ['POST', 'DELETE']
API_LOG_METHODS = ['POST', 'UPDATE', 'DELETE', 'PUT']  # ['POST', 'DELETE']
API_MODEL_MAP = {
    "/token/refresh/": "刷新token",
    "/captcha/refresh/": "刷新验证码",
    "/login/": "登录",
    "/signup/": "注册",
}
IS_SINGLE_TOKEN = eval(os.getenv("IS_SINGLE_TOKEN", 'False'))  # 是否开启单用户单一地点登录(只有一个人在线上)(默认多地点登录)
