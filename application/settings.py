"""
Django settings for application project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import logging
import os, sys
from pathlib import Path
from configs.config import *
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# ================================================= #
# ******************** 动态配置 ******************** #
# ================================================= #
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bm_+x1ju4$%))h7e&on1(hd3@&!iafu7z6$5e0&g)lghfnp+ew'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG

ALLOWED_HOSTS = ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方插件
    "corsheaders",
    'rest_framework',
    'django_filters',
    'drf_yasg',  # 在线接口文档
    'captcha',  # 验证码

    # 自定义APP
    "apps.user",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 跨域中间件
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'application.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 放置前端页面的地方
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'application.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# ================================================= #
# ************** mysql数据库 配置  ************** #
# ================================================= #
# DATABASES = {
#     'default': {
#         'ENGINE': DATABASE_ENGINE,
#         'NAME': DATABASE_NAME,
#         'USER': DATABASE_USER,
#         'PASSWORD': DATABASE_PASSWORD,
#         'HOST': DATABASE_HOST,
#         'PORT': DATABASE_PORT,
#         'CONN_MAX_AGE':DATABASE_CONN_MAX_AGE,
#         'OPTIONS': {
#                     'charset':DATABASE_CHARSET,
#                     'init_command': 'SET default_storage_engine=INNODB', #innodb才支持事务
#                 }
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# ================================================= #
# ******************* redis缓存 ******************* #
# ================================================= #
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',  # 缓存后端 Redis
        # 连接Redis数据库(服务器地址)
        # 一主带多从(可以配置多个Redis，写走第一台，读走其他的机器)
        'LOCATION': [
            f'{REDIS_URL}/0',
        ],
        'KEY_PREFIX': 'lybbn',  # 项目名当做文件前缀
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # 连接选项(默认，不改)
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 512,  # 连接池的连接(最大连接)
            },
        }
    },
    'session': {  # 缓存session
        'BACKEND': 'django_redis.cache.RedisCache',  # 缓存后端 Redis
        # 连接Redis数据库(服务器地址)
        # 一主带多从(可以配置多个Redis，写走第一台，读走其他的机器)
        'LOCATION': [
            f'{REDIS_URL}/1',
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # 连接选项(默认，不改)
        }
    },
    'verify_codes': {  # 缓存短信验证码
        'BACKEND': 'django_redis.cache.RedisCache',  # 缓存后端 Redis
        # 连接Redis数据库(服务器地址)
        # 一主带多从(可以配置多个Redis，写走第一台，读走其他的机器)
        'LOCATION': [
            f'{REDIS_URL}/2',
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # 连接选项(默认，不改)
        }
    },
    "carts": {  # 登陆过的用户购物车的存储
        "BACKEND": "django_redis.cache.RedisCache",
        'LOCATION': [
            f'{REDIS_URL}/3',
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {'decode_responses': True},  # 添加这一行,防止取出的值带有b'' bytes
        },
    },
    "authapi": {  # 接口安全校验（验证接口重复第二次访问会拒绝）
        'BACKEND': 'django_redis.cache.RedisCache',  # 缓存后端 Redis
        # 连接Redis数据库(服务器地址)
        # 一主带多从(可以配置多个Redis，写走第一台，读走其他的机器)
        'LOCATION': [
            f'{REDIS_URL}/4',
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # 连接选项(默认，不改)
        }
    },
    "singletoken": {  # jwt单用户登录（确保一个账户只有一个地点登录，后一个会顶掉前一个）
        'BACKEND': 'django_redis.cache.RedisCache',  # 缓存后端 Redis
        # 连接Redis数据库(服务器地址)
        # 一主带多从(可以配置多个Redis，写走第一台，读走其他的机器)
        'LOCATION': [
            f'{REDIS_URL}/5',
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # 连接选项(默认，不改)
            'CONNECTION_POOL_KWARGS': {'decode_responses': True},  # 添加这一行,防止取出的值带有b'' bytes
        }
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False  # 设置为中国时间

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = "/media/"
# 项目中存储上传文件的根目录
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# 收集静态文件，必须将 MEDIA_ROOT,STATICFILES_DIRS先注释
# python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================================= #
# ********************* 日志配置 ******************* #
# ================================================= #
LOG_DIR = os.path.join(BASE_DIR, LOG_FOLDER)
os.makedirs(LOG_DIR, mode=0o775, exist_ok=True)
LOG_CLASS = "utils.logs.LoguruBaseRotatingHandler"
LOGFILTER = "utils.logs.LevelFilter"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": LOG_FORMAT,
            # 打日志的格式
            "datefmt": "%Y-%m-%d %H:%M:%S %z",  # 时间显示方法
            # "class": "logging.Formatter"
        },
        'simple': {  # 简单格式
            'format': '%(levelname)s %(message)s'
        },
    },
    # 这里是定义过滤器，需要注意的是，由于 'filters' 是 logging.config.dictConfig 方法要求在配置字典中必须给订的 key ,所以即使不使用过滤器也需要明确给出一个空的结构。
    "filters": {
        "error_filter": {"()": LOGFILTER, "level": logging.ERROR},
        "warn_filter": {"()": LOGFILTER, "level": logging.WARN},
        "info_filter": {"()": LOGFILTER, "level": logging.INFO},
        "debug_filter": {"()": LOGFILTER, "level": logging.DEBUG},
    },
    "handlers": {
        "error": {
            "level": "ERROR",
            "class": LOG_CLASS,
            "formatter": "standard",
            "filters": ["error_filter"],
            "filename": os.path.join(LOG_DIR, "error.log"),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
        },
        "warning": {
            "level": "WARNING",
            "class": LOG_CLASS,
            "formatter": "standard",
            "filters": ["warn_filter"],
            "filename": os.path.join(LOG_DIR, "waring.log"),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
        },
        "info": {
            "level": "INFO",
            "class": LOG_CLASS,
            "formatter": "standard",
            "filters": ["info_filter"],
            "filename": os.path.join(LOG_DIR, "info.log"),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
        },
        "debug": {
            "level": "DEBUG",
            "class": LOG_CLASS,
            "formatter": "standard",
            "filters": ["debug_filter"],
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "maxBytes": max_bytes,
            "backupCount": backup_count,
        },
        # 控制台输出
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "standard"},
    },
    "loggers": {
        # # default日志
        # '': {
        #     'handlers': ['error', 'info', "debug", "warning"],
        #     'level': 'INFO',
        # },
        "django": {
            "handlers": ["info", "warning", "debug", "error", ],
            "level": "INFO",
            "propagate": True
        },
        'scripts': {
            'handlers': ["info", "warning", "debug", "error", ],
            'level': 'INFO',
        },
        # 数据库相关日志
        'django.db.backends': {
            'handlers': ["info", "warning", "debug", "error", ],
            'propagate': False,
            'level': 'INFO',
        },
    },
}
# 使用自定义日志输出反射到默认logging上
# 如果是需要使用logging 替换为默认的日志输出则需要
LOGGING_CONFIG = "utils.logs.simple_log_injector"

# ================================================= #
# ******************* session配置 ******************* #
# ================================================= #
# session使用的存储方式
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 指明使用哪一个库保存session数据
SESSION_CACHE_ALIAS = "session"

# ================================================= #
# *************** REST_FRAMEWORK配置 *************** #
# ================================================= #
REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",  # 日期时间格式配置
    'DATE_FORMAT': "%Y-%m-%d",
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',

    ),
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.CustomPagination',  # 自定义分页
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # 限速设置
    # 'DEFAULT_THROTTLE_CLASSES': (
    #         'rest_framework.throttling.AnonRateThrottle',   #未登陆用户
    #         'rest_framework.throttling.UserRateThrottle'    #登陆用户
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '30/minute',                   #未登录用户每分钟可以请求30次，还可以设置'100/day',天数
    #     'user': '60/minute'                    #已登录用户每分钟可以请求60次
    # },
    'EXCEPTION_HANDLER': 'utils.exception.CustomExceptionHandler',  # 自定义的异常处理
    # #线上部署正式环境，关闭web接口测试页面
    # 'DEFAULT_RENDERER_CLASSES':(
    #     'rest_framework.renderers.JSONRenderer',
    # ),
}
# ================================================= #
# ****************** simplejwt配置 ***************** #
# ================================================= #
SIMPLE_JWT = {
    # token有效时长
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    # token刷新后的有效时间
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    # 设置header字段Authorization的值得前缀： JWT accesstoken字符串
    'AUTH_HEADER_TYPES': ('JWT',),
    'ROTATE_REFRESH_TOKENS': True
}

# ====================================#
# ****************swagger************#
# ====================================#
SWAGGER_SETTINGS = {
    # 基础样式
    'SECURITY_DEFINITIONS': {
        "basic": {  # 用户名密码cookie验证
            'type': 'basic'
        },
        'JWT': {  # 通过jwt验证
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
        # 'Query': {#通过query中auth变量验证
        #         'type': 'apiKey',
        #         'name': 'auth',
        #         'in': 'query'
        #     }
    },
    # 如果需要登录才能够查看接口文档, 登录的链接使用restframework自带的.
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
    # 'DOC_EXPANSION': None,
    # 'SHOW_REQUEST_HEADERS':True,
    # 'USE_SESSION_AUTH': True,
    # 'DOC_EXPANSION': 'list',
    # 接口文档中方法列表以首字母升序排列
    'APIS_SORTER': 'alpha',
    # 如果支持json提交, 则接口文档中包含json输入框
    'JSON_EDITOR': True,
    # 方法列表字母排序
    'OPERATIONS_SORTER': 'alpha',
    'VALIDATOR_URL': None,
    'AUTO_SCHEMA_TYPE': 1,  # 分组根据url层级分，0、1 或 2 层
    'DEFAULT_AUTO_SCHEMA_CLASS': 'utils.swagger.CustomSwaggerAutoSchema',
    # 'DEFAULT_PARSER_CLASSES': (
    #           'rest_framework.parsers.FormParser',
    #           'rest_framework.parsers.MultiPartParser',
    #           'rest_framework.parsers.JSONParser',
    #    ),
}

# ================================================= #
# **************** 验证码配置  ******************* #
# ================================================= #
CAPTCHA_STATE = True
CAPTCHA_IMAGE_SIZE = (160, 60)  # 设置 captcha 图片大小
CAPTCHA_LENGTH = 4  # 字符个数
CAPTCHA_TIMEOUT = 1  # 超时(minutes)
CAPTCHA_OUTPUT_FORMAT = '%(image)s %(text_field)s %(hidden_field)s '
CAPTCHA_FONT_SIZE = 42  # 字体大小
CAPTCHA_FOREGROUND_COLOR = '#409eff'  # 前景色
CAPTCHA_BACKGROUND_COLOR = '#FFFFFF'  # 背景色
CAPTCHA_NOISE_FUNCTIONS = (
    'captcha.helpers.noise_arcs',  # 线
    # 'captcha.helpers.noise_dots', # 点
)
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge' #字母验证码
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'  # 加减乘除验证码

# ================================================= #
# ******************** celery配置 ******************** #
# ================================================= #
CELERY_TIMEZONE = 'Asia/Shanghai'  # celery 时区问题
CELERY_BROKER_URL = f'{REDIS_URL}/10'  # Broker配置，使用Redis作为消息中间件(无密码)
# CELERY_BROKER_URL = 'redis://djangox:{}@127.0.0.1:6379/10'.format('123456')  #djangox 代表 账号（没有可省略）  {} 存放密码  127.0.0.1连接的 ip  6379端口  10 redis库
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/11' # 把任务结果存在了Redis
CELERY_RESULT_BACKEND = 'django-db'  # celery结果存储到数据库中django-db
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'  # Backend数据库
CELERY_RESULT_PERSISTENT = True
CELERY_RESULT_EXTENDED = True
DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_ENABLE_UTC = False
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}  # 连接超时
CELERY_TASK_SERIALIZER = 'json'  # 任务序列化和反序列化使json
CELERY_RESULT_SERIALIZER = 'json'
# CELERYD_CONCURRENCY = 2  #并发worker数量
CELERY_WORKER_CONCURRENCY = 2  # 并发数
CELERYD_FORCE_EXECV = True  # 防止死锁,应确保为True
CELERY_TASK_TIME_LIMIT = 60 * 30 * 5  # 限制celery任务执行时间，# 单个任务的运行时间限制，否则会被杀死
CELERYD_MAX_TASKS_PER_CHILD = 100  # worker执行100个任务自动销毁，防止内存泄露
CELERYD_TASK_SOFT_TIME_LIMIT = 6000  # 单个任务的运行时间不超过此值(秒)，否则会抛出(SoftTimeLimitExceeded)异常停止任务
CELERY_DISABLE_RATE_LIMITS = True  # 即使任务设置了明确的速率限制，也禁用所有速率限制。
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # 去除celery6.0启动时warning警告，确保在启动时进行代理连接重试

# ================================================= #
# ******************* 跨域的配置 ******************* #
# ================================================= #
# 如果为True，则将不使用白名单，并且将接受所有来源。默认为False
# 允许跨域
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True  # 新版 ACCESS_CONTROL_ALLOW_ORIGIN = '*' ,不能与CORS_ALLOW_CREDENTIALS一起使用
# 允许cookie
# CORS_ALLOW_CREDENTIALS = True  # 指明在跨域访问中，后端是否支持对cookie的操作
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'None'

# ================================================= #
# ******************* 其他配置 ******************* #
# ================================================= #
# 自定义用户模型
AUTH_USER_MODEL = 'user.Users'
USERNAME_FIELD = 'user_name'
ALL_MODELS_OBJECTS = []  # 所有app models 对象
table_prefix = table_prefix  # 数据库表名前缀
