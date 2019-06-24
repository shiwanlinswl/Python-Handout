from flask import Blueprint
# 创建蓝图，并设置蓝图前缀
news_bp = Blueprint("news_bp", __name__, url_prefix='/news')

# 方法一
from info.modules.news.views import *
# 方法二
# from . import views