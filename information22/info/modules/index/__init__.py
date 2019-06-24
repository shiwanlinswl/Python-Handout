from flask import Blueprint
# 1.创建蓝图对象
index_bp = Blueprint("index", __name__)

# 3.将蓝图对象和视图函数建立关系
from info.modules.index.views import *

