from flask import current_app, jsonify, g
from flask import session
import functools

# 过滤器本质是函数
# 1. 使用python的函数实现业务逻辑
from info.response_code import RET


def do_index_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


# 使用装饰器封装登陆成功获取用户对象
# view_func：被装饰的视图函数
def get_user_data(view_func):
    """
    问题：装饰器会改变函数的名称及内部备注
    解决：1.导入functools
         2.用functools装饰内部函数
    """
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 1.实现装饰器的业务逻辑

        # ---------1.用户登陆成功,查询用户基本信息展示---------
        # 1.获取用户的id
        user_id = session.get("user_id")
        # 先声明,防止局部变量不能访问
        user = None
        # 数据库存在循环导入的问题，解决：在哪里需要用到数据库数据再导入
        from info.models import User
        if user_id:
            # 2.根据user_id查询当前登陆的用户对象
            try:

                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

        g.user = user
        # 2.实现被装饰函数原有功能
        return view_func(*args, **kwargs)

    return wrapper

