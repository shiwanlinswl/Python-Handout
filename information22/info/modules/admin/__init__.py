from flask import Blueprint
# 1.创建蓝图对象
admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

# 3.将蓝图对象和视图函数建立关系
from info.modules.admin.views import *


@admin_bp.before_request
def is_admin_user():
    """判断是否是管理员"""

    if request.url.endswith("/admin/login"):
        # 不拦截
        pass
    else:
        # 如果用户是管理员 -->/admin/管理员首页，不拦截直接进入
        user_id = session.get("user_id")
        is_admin = session.get("is_admin", False)

        # 要么用户未登录&要么不是管理员
        if not user_id or not is_admin:
            # 1.如果是普通用户访问 -->/admin/管理员首页，拦截并且引导到新闻首页
            # 1.如果用户未登录 -->/admin/管理员首页，拦截并且引导到新闻首页
            return redirect("/")