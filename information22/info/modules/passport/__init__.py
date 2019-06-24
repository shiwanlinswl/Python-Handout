from flask import Blueprint
# 创建蓝图，并设置蓝图前缀
passport_bp = Blueprint("passport", __name__, url_prefix='/passport')

# 方法一
from info.modules.passport.views import *
# 方法二
# from . import views