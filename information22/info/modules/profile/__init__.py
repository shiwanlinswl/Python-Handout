from flask import Blueprint
# 创建蓝图，并设置蓝图前缀
profile_bp = Blueprint("profile", __name__, url_prefix='/user')

# 方法一
from info.modules.profile.views import *
# 方法二
# from . import views