# 生产(上线)模式下使用

import datetime
import os,sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(os.path.abspath(__file__))  # 当前文件的绝路路径

# print(BASE_DIR)  # 当前应用的路径
# /home/python/Desktop/meiduo_sz/meiduo_mall/meiduo_mall

# print(sys.path)  # 返回python解释器搜索路径，结果是列表

# 在列表中添加拼接路径，追加导包路径
# sys.path.append(os.path.join(BASE_DIR, 'apps'))   # 优化：append --> insert
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))  # 好处：将拼接的路径放在导包路径的最前面，防止在末尾追加，每次都要从头到尾找一遍

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nx!qndk5d7s^0#yu61+9_1@1ksw6u(-$#9jtcv1mz#&^8gv&3)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

# 允许那些域名来访问django
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'www.meiduo.site', 'api.meiduo.site', '192.168.192.137']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',  # DRF
    'corsheaders',
    'ckeditor',  # 富文本编辑器
    'ckeditor_uploader',  # 富文本编辑器上传图片模块
    'django_crontab',  # 定时器
    'haystack',  # 搜索

    # 以下三个都是Xadmin的子应用
    'xadmin',
    'crispy_forms',
    'reversion',


    'users.apps.UsersConfig',  # 注册用户的子应用
    # 'verifications.apps.VerificationsConfig',
    'oauth.apps.OauthConfig',  # 注册qq登录数据子应用
    'areas.apps.AreasConfig',  # 省市区
    'goods.apps.GoodsConfig',  # 商品
    'contents.apps.ContentsConfig',  # 广告
    'orders.apps.OrdersConfig',  # 订单

]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 最外层的中间件

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    'default': {  # 主
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.192.137',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'meiduo',  # 数据库.用户名
        'PASSWORD': 'meiduo',  # 数据库.用户密码
        'NAME': 'meiduo_mall'  # 数据库名字
    },
    'slave': {  # 从
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.192.137',  # 数据库主机
        'PORT': 8306,  # 数据库端口
        'USER': 'root',  # 数据库.用户名
        'PASSWORD': 'mysql',  # 数据库.用户密码
        'NAME': 'meiduo_mall'  # 数据库名字
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'


# 配置redis数据库作为缓存后端
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.192.137:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.192.137:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_codes": {  # 存储验证码
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.192.137:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {  # 存储浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.192.137:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "cart": {  # 购物车存储
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.192.137:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# 日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}


# DRF配置项
REST_FRAMEWORK = {
    # 自定义异常捕获
    'EXCEPTION_HANDLER': 'meiduo_mall.utils.exceptions.exception_handler',

    'DEFAULT_AUTHENTICATION_CLASSES': (  # 配置全局认证类(验证登录用户是不是本网站用户)
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',  # JWT认证(默认认证方案)
        'rest_framework.authentication.SessionAuthentication',  # session认证
        'rest_framework.authentication.BasicAuthentication',  # 基础认证
    ),

    # 全局分页
    'DEFAULT_PAGINATION_CLASS': 'meiduo_mall.utils.paginations.StandardResultsSetPagination',
}


# 修改用户模型类
# String model references must be of the form 'app_label.ModelName'-->修改用户模型类的导包路径必须是：子应用名.模型类名  的这种格式
# AUTH_USER_MODEL = "meiduo_mall.apps.users.models.User"  # 格式存在问题
AUTH_USER_MODEL = "users.User"


# CORS  追加白名单
CORS_ORIGIN_WHITELIST = (
    '127.0.0.1:8080',
    'localhost:8080',
    'www.meiduo.site:8080',
    'api.meiduo.site:8000',
    '192.168.192.137',
    'www.meiduo.site',
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie


# JWT配置项
JWT_AUTH = {
    # 'JWT_EXPIRATION_DELTA':指明token的有效期
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 修改jwt登录后响应体函数
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler'
}

# 修改默认的认证后端
AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',  # 修改django认证后端类
]

# QQ登录参数
QQ_CLIENT_ID = '101474184'
QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'


# 设置邮箱的配置信息
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25


#发送邮件的邮箱
# EMAIL_HOST_USER = 'shiwanlin930718@163.com'
# #在邮箱中设置的客户端授权密码
# EMAIL_HOST_PASSWORD = 'python123'
# #收件人看到的发件人
# EMAIL_FROM = 'python<shiwanlin930718@163.com>'

# 教学账号
EMAIL_HOST_USER = 'itcast99@163.com'
EMAIL_HOST_PASSWORD = 'python99'
EMAIL_FROM = 'python<itcast99@163.com>'


# DRF扩展
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}

# django⽂文件存储
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fdfs_storage.FastDFSStorage'

# FastDFS
FDFS_BASE_URL = 'http://192.168.192.137:8888/'
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')

# django⽂件存储
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fdfs_storage.FastDFSStorage'

# 富文本编辑器ckeditor配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        # 'width': 300,  # 编辑器宽
    },
}

CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''

# 生成的静态html文件保存目录
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')

# 定时任务
CRONJOBS = [
    # 每5分钟执行一次生成主页静态文件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> /home/python/Desktop/meiduo_sz/meiduo_mall/logs/crontab.log')
]

# 解决crontab中文问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.192.137:9200/',  # 此处为elasticsearch运行的服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo',  # 指定elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 配置读写分离
DATABASE_ROUTERS = ['meiduo_mall.utils.db_router.MasterSlaveDBRouter']

# 配置静态⽂文件收集之后存放的⽬目录
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc/static')