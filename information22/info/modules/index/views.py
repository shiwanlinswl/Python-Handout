from info.models import User
from info.modules.index import index_bp
import logging
from flask import current_app, session, jsonify
from flask import render_template, request
from info.models import User, News, Category
from info import constants
from info.response_code import RET


# get请求地址：/news_list?cid=1&p=1&per_page=10
@index_bp.route('/news_list')
def get_news_list():
    """获取首页新闻列表数据"""
    """
    1.获取参数
        1.1 cid：分类id , p:当前页码 , 默认值：1表示第一页数据 , per_page:每一页多少条数据 , 默认值：10
    2.校验参数
        2.1 cid非空判断
        2.2 将int强制类型转换
    3.逻辑处理
        3.1 根据cid作为查询条件，新闻的时间降序排序，进行分页查询
        3.2 将新闻对象列表转换成字典对象列表
    4.返回值
    """
    # 1.1cid：分类id, p: 当前页码, 默认值：1表示第一页数据, per_page: 每一页多少条数据, 默认值：10
    cid = request.args.get("cid")
    p = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    # 2.1cid非空判断
    if not cid:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 2.2将int强制类型转换
    try:
        cid = int(cid)
        p = int(p)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")

    news_list = []
    current_page = 1
    total_page = 1

    """
    # 查询的是最新的分类新闻数据,最新新闻查询只需要按时间降序排序即可
    if cid == 1:
        paginate = News.query.filter().order_by(News.create_time.desc()).paginate(p,per_page,False)

        # 获取所有数据
        news_list = paginate.items
        # 获取当前页码
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages

    # 查询其他分类新闻，需要加上这个条件：News.category_id == cid
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(p, per_page,False)

        # 获取所有数据
        news_list = paginate.items
        # 获取当前页码
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    """

    # 查询条件的列表
    # 默认查询条件：News.status == 0 查询审核通过的这一类新闻
    filter_list = [News.status == 0]
    if cid != 1:
        # 将查询条件添加到列表中
        filter_list.append(News.category_id == cid)

    # 3.1根据cid作为查询条件，新闻的时间降序排序，进行分页查询
    # paginate():参数1：当前页码， 参数2：每一页多少条数据 参数3：不需要错误数据，使用try捕获
    try:
        paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(p, per_page, False)

        # 获取所有数据
        news_list = paginate.items
        # 获取当前页码
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻列表数据异常")
    # 3.2将新闻对象列表转换成字典对象列表
    news_dict_list = []
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_dict())

    # 4.组织返回的数据
    data = {
        "news_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }

    return jsonify(errno=RET.OK, errmsg="查询新闻列表成功", data = data)


# 2.将蓝图对象和视图函数绑定在一起
@index_bp.route('/')
def index():
    # ---------1.用户登陆成功,查询用户基本信息展示---------

    # 1.获取用户的id
    user_id = session.get("user_id")
    # 先声明,防止局部变量不能访问
    user = None
    if user_id:
        # 2.根据user_id查询当前登陆的用户对象
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 3.将用户对象转换成字典
    user_dict = user.to_dict() if user else None
    """
    if user:
        user_dict = user.to_dict()
    """

    # ---------2.查询新闻点击排行数据显示---------
    # news_rank_list:[news_obj1, news_obj2,,,]
    try:
        news_rank_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 新闻对象列表转化成字典列表
    news_dict_list = []
    """
    if news_rank_list:
        for news in news_rank_list:
            news_dict = news.to_dict()
            news_rank_list.append(news_dict)
    """
    for news in news_rank_list if news_rank_list else []:
        news_dict_list.append(news.to_dict())

    # ---------3.查询分类数据展示---------
    # categories:[分类对象列表]
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询分类数据异常")
    # 分类对象列表转换成字典列表
    category_dict_list = []
    for category in categories if categories else []:
        category_dict_list.append(category.to_dict())
    # 4.组织响应数据
    """
    data = {
            "user_info":{
                "id":self.id,
                "nick_name":self.nick_name,
            }
    }
    前端使用方式：data.user_info.nick_name
    """
    data = {
        "user_info": user_dict,
        "click_news_list": news_dict_list,
        "categories": category_dict_list
    }

    return render_template('news/index.html', data=data)


# 网页图标展示的视图函数
@index_bp.route('/favicon.ico')
def favicon():
    """
    返回网站图标
    Function used internally to send static files from the static
    folder to the browser
    内部用来发送静态文件到浏览器的方法
    """
    # send_static_file:是系统访问静态文件所调用的方法
    return current_app.send_static_file('news/favicon.ico')


