from flask import Flask, g, render_template
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session
from config import config_dict
import logging
from logging.handlers import RotatingFileHandler
from info.utils.common import do_index_class, get_user_data

# 只是申明db对象,此时数据库是没有数据的,并没有进行初始化的工作
db = SQLAlchemy()

# 将redis_store数据库对象申明为全局变量
# type:StrictRedis 提前申明redis_store数据库对象的类型
redis_store = None  # type:StrictRedis


def write_log(config_class):
    """记录日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config_class.LOG_LEVEL)  # 调试debug级

    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/logs", maxBytes=10, backupCount=10)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 将app封装起来,给外界使用提供一个接口
# development --- 返回的是开发模式的app对象
# production --- 返回的是线上模式的app对象
def create_app(config_name):
    """
    将与app相关联的配置封装到`工厂方法`中
     :return: app对象
    """

    # 1.创建app对象,加载配置类
    app = Flask(__name__)
    # 根据development键获取对应的配置类名
    config_class = config_dict[config_name]
    # DevelopmentConfig ---> 开发模式的app对象
    # ProductionConfig --->  线上模式的app对象
    app.config.from_object(config_class)

    # 1.1调用记录日志函数
    write_log(config_class)

    # 2.当SQLAlchemy有数据时,调用init_app属性
    # 延迟操作的思想,也叫懒加载当app有值的时候才真正进行数据库的初始化工作
    db.init_app(app)

    # 3.创建redis数据库对象
    global redis_store
    redis_store = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, decode_responses=True)
    # app.redis_store = redis_store

    # redis_store.set("age", 18)  ---->存储到redis ---0号数据库
    # session["name"] = "laowang" ---->存储到redis ---1号数据库

    # 4.开启后端csrf保护机制
    """
    # 底层：
    # 1.提取cookie中的csrf_token的值
    # 2.提取表单中的csrf_token的值，或者ajax请求的头中的X-CSRFToken键对应的值
    # 3.对比这两个值是否相等
    """

    CSRFProtect(app)

    # 在每一次请求之后，都设置csrf_token值
    @app.after_request
    def set_csrf_token(response):
        # 1.生成csrf_token随机值
        csrf_token = generate_csrf()
        # 2.借助响应对象将csrf_token保存到cookie中
        response.set_cookie("csrf_token", csrf_token)

        # 3.将响应对象返回
        return response

    # 捕获404异常，返回404统一页面
    @app.errorhandler(404)
    @get_user_data
    def handler_404_notfound(err):
        # 1.查询用户基本信息
        user = g.user

        data = {
            "user_info":user.to_dict() if user else None,
        }
        # 2.返回404模板数据，同时传入用户信息
        return render_template("news/404.html", data=data)

    # 添加自定义过滤器
    app.add_template_filter(do_index_class, "do_index_class")

    # 5.借助Session调整flask.session的存储位置到redis中存储
    Session(app)

    # 问题:在首行(程序前面)导入蓝图对象会出现循环导入问题
    # 解决:使用蓝图延迟导入;在需要注册蓝图的地方再导入蓝图对象

    # 导入首页蓝图对象
    from info.modules.index import index_bp
    # 哪里有app的地方在哪里注册,注册index_bp蓝图对象
    app.register_blueprint(index_bp)

    # 导入登陆注册蓝图对象
    from info.modules.passport import passport_bp
    # 注册passport_blu蓝图对象
    app.register_blueprint(passport_bp)

    # 导入新闻详情蓝图对象
    from info.modules.news import news_bp
    # 注册news_bp蓝图对象
    app.register_blueprint(news_bp)

    # 导入个人中心蓝图对象
    from info.modules.profile import profile_bp
    # 注册profile_bp蓝图对象
    app.register_blueprint(profile_bp)

    # 导入管理员后台蓝图对象
    from info.modules.admin import admin_bp
    # 注册admin_bp蓝图对象
    app.register_blueprint(admin_bp)

    return app




