from redis import StrictRedis
import logging


class Config(object):
    """自定义配置类,进爱过你配置信息以属性的方式罗列即可"""
    DEBUG = True

    # mysql数据库配置信息
    # 连接mysql数据库的配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"

    # 开启数据库跟踪模式
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 开启数据库自动提交功能
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # redis数据库配置:绑定redis数据库ip地址和端口
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 使用session记得添加加密字符串对session_id进行加密处理
    SECRET_KEY = "safgtyuifasdghggfgsdf"

    # 将falsk中的session存储到redis数据库的配置信息
    # 添加存储的数据库类型
    SESSION_TYPE = "redis"

    # session存储的数据产生后的session_id需要加密
    SESSION_USE_SIGNER = True

    # 具体将session数据存储到哪个redis数据库对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)

    # 设置过期市场,默认时长为31天
    PERMANENT_SESSION_LIFETIME = 86400


class DevelopmentConfig(Config):
    """开发模式的配置类"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """线上模式的配置类"""
    DEBUG = False
    LOG_LEVEL = logging.ERROR

# 给外界使用提供一个接口
# 使用：config_dict["development"] ---> DevelopmentConfig
# 定义配置字典:
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}