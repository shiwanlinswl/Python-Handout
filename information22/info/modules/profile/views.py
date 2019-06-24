from info.models import User, Category, News
from info import constants
from info import db
from info.response_code import RET
from . import profile_bp
from flask import render_template, g, request, jsonify, session, current_app
from info.utils.common import get_user_data
from info.utils.pic_storage import pic_storage


# 127.0.0.1:5000/user/user_follow?p=1
@profile_bp.route('/user_follow')
@get_user_data
def user_follow():
    """新闻列表数据展示"""

    user = g.user
    # 用户登录才查询用户发布的新闻列表
    # 注意：第一次跳转的时候没有携带p页码，使用默认值
    p = request.args.get("p", 1)

    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    user_list = []
    current_page = 1
    total_page = 1
    if user:
        """
        user.followed：当前登录用户的关注列表
        犹豫被修饰成dynamic属性
        user.followed如果真是用到数据返回是一个'列表'
        user.followed只是去查询了返回一个'查询对象'
        """
        try:
            paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
            # 当前页码所有数据
            user_list = paginate.items
            # 当前页码
            current_page = paginate.page
            # 总页数
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 用户对象列表转换成字典列表
    user_dict_list = []
    for user in user_list if user_list else []:
        user_dict_list.append(user.to_dict())

    # 组织返回数据
    data = {
        "users": user_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }

    return render_template("profile/user_follow.html", data=data)


#127.0.0.1:5000/user/news_list?p=1 --查询用户我的收藏
@profile_bp.route("/news_list")
@get_user_data
def news_list():
    """查询用户的发布新闻列表数据(分页)"""
    """
    1.获取参数
        1.1 P：查询的页码， 默认值：1 表示查询第一页的数据
    2.参数检验
        2.1 页码的数据类型判断
    3.逻辑处理
        3.1 根据新闻对象new进行分页查询
        3.2 将查询到的新闻对象转换为字典列表
    4.返回值
    """
    # 1.1 P：查询的页码， 默认值：1 表示查询第一页的数据
    p = request.args.get("p", 1)
    user = g.user
    # 2.1 页码的数据类型判断
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    # 3.1 根据新闻对象new进行分页查询

    news_list = []
    current_page = 1
    total_page = 1

    # 查询用户收藏只有用户已经登录的情况才查询用户收藏的数据
    if user:
        try:
            # 进行分页数据查询
            paginate = News.query.filter(News.user_id == user.id).order_by(News.create_time.desc())\
                .paginate(p, constants.USER_NEWS_PAGE_MAX_COUNT, False)
            # 当前页码的所有数据
            news_list = paginate.items
            # 当前页码
            current_page = paginate.page
            # 总页数
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询用户发布新闻对象异常")

    # 3.2 将查询到的新闻对象转换为字典列表
    news_dict_list = []
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_review_dict())

    # 4.返回值
    data = {
        "news_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("profile/user_news_list.html", data=data)

#127.0.0.1:5000/user/news_release --查询用户我的收藏
@profile_bp.route("/news_release", methods=["GET", "POST"])
@get_user_data
def news_release():
    """发布新闻的页面显示&发布新闻的逻辑处理"""
    # GET请求：发布新闻的页面展示，同时将分类数据返回
    if request.method == "GET":

        # 1.查询所有分类的数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询分类对象异常")

        # 2. 分类列表对象转换成字典对象
        category_dict_list = []
        for category in categories if categories else []:
            category_dict_list.append(category.to_dict())

        # 移除'最新'分类
        category_dict_list.pop(0)

        return render_template("profile/user_news_release.html", data={"categories": category_dict_list})

    # POST请求：发布新闻逻辑处理
    """
    1.获取参数(表单请求数据)
        1.1 title:新闻标题,cid:新闻分类，digest:新闻的摘要，index_image:新闻主图片，
            content：新闻的内容，user:当前用户对象
    2.参数检验
        2.1 非空判断
    3.逻辑处理
        3.1 新闻主图片保存到七牛云
        3.2 创建新闻对象，给各个属性赋值，保存会收据库
    4.返回值
    """
    # 1.1 title:新闻标题,cid:新闻分类，digest:新闻的摘要，index_image:新闻主图片，
    #         content：新闻的内容，user:当前用户对象
    param_dict = request.form
    title = param_dict.get("title")
    cid = param_dict.get("category_id")
    digest = param_dict.get("digest")
    content = param_dict.get("content")
    index_image = request.files.get("index_image")
    user = g.user
    source = "个人发布"

    # 2.1 非空判断
    if not all([title, cid, content, index_image]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    try:
        cid = int(cid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="分类id格式错误")

    # 3.1 新闻主图片保存到七牛云
    pic_data = None
    try:
        pic_data = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取图片数据异常")

    try:
        pic_name = pic_storage(pic_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片到七牛云异常")

    # 3.2 创建新闻对象，给各个属性赋值，保存会收据库
    news = News()
    # 新闻标题
    news.title = title
    # 新闻分类
    news.category_id = cid
    # 新闻摘要
    news.digest = digest
    # 新闻内容
    news.content = content
    # 新闻主图片的url
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + pic_name
    # 新闻来源
    news.source = source
    # 新闻id
    news.user_id = user.id
    # 新发布的新闻处于审核中
    news.status = 1

    # 保存数据回数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存新闻对象异常")

    return jsonify(errno=RET.OK, errmsg="新闻发布成功")


#127.0.0.1:5000/user/collection?p=1 --查询用户我的收藏
@profile_bp.route("/collection")
@get_user_data
def get_collection():
    """查询用户的收藏新闻列表数据(分页)"""
    """
    1.获取参数
        1.1 P：查询的页码， 默认值：1 表示查询第一页的数据
    2.参数检验
        2.1 页码的数据类型判断
    3.逻辑处理
        3.1 根据user.collection_news查询对象进行分页查询
        3.2 将查询到的新闻对象转换为字典列表
    4.返回值
    """
    # 1.1 P：查询的页码， 默认值：1 表示查询第一页的数据
    p = request.args.get("p", 1)
    user = g.user
    # 2.1 页码的数据类型判断
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    # 3.1 根据user.collection_news查询对象进行分页查询
    """
    user.collection_news使用了lazy="dynamic"修饰
    1.如果是真是用到数据：user.collection_news返回的是新闻对象列表的数据
    2.如果只是查询：user.collection_news返回是查询对象
    """

    news_list = []
    current_page = 1
    total_page = 1

    # 查询用户收藏只有用户已经登录的情况才查询用户收藏的数据
    if user:
        try:
            # 进行分页数据查询
            paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
            # 当前页码的所有数据
            news_list = paginate.items
            # 当前页码
            current_page = paginate.page
            # 总页数
            total_page = paginate.pages
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询用户收藏新闻列表异常")

    # 3.2 将查询到的新闻对象转换为字典列表
    news_dict_list = []
    for news in news_list if news_list else []:
        news_dict_list.append(news.to_review_dict())

    # 4.返回值
    data = {
        "collections": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("profile/user_collection.html", data=data)


#127.0.0.1:5000/user/pass_info --展示修改密码&密码提交修改
@profile_bp.route("/pass_info", methods=["GET", "POST"])
@get_user_data
def pass_info():
    """展示修改密码&密码提交修改"""
    # GET请求：返回密码修改页面
    if request.method == "GET":
        return render_template("profile/user_pass_info.html")

    #POST请求：提交新旧密码并进行修改保存到数据库

    """
     1.获取参数
         1.1 old_password:旧的密码,new_password:新的密码,user:当前登陆的用户对象
     2.参数校验
         2.1 非空判断
     3.逻辑处理
         3.1 对就密码进行校验：调用user对象上的check_password方法
         3.2 将密码赋值给user对象的password属性，内部会自定加密
         3.3 将赋值的属性保存到数据库
     4.返回值
    """

    # 1.1 old_password:旧的密码,new_password:新的密码,user:当前登陆的用户对象
    params_dict = request.json
    old_password = params_dict.get("old_password")
    new_password = params_dict.get("new_password")
    user = g.user

    # 2.1 非空判断
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 3.1 对就密码进行校验：调用user对象上的check_password方法
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="密码输入错误")

    # 3.2 将密码赋值给user对象的password属性，内部会自定加密
    user.password = new_password

    # 3.3 将赋值的属性保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户密码异常")
    # 4.返回值
    return jsonify(errno=RET.OK, errmsg="修改密码成功")


#127.0.0.1:5000/user/pic_info --展示修改头像页面&头像数据修改
@profile_bp.route("/pic_info", methods=["GET", "POST"])
@get_user_data
def pic_info():
    """展示用户头像后端接口"""
    """
    GET请求方式:返回修改用户头像页面
    POST请求方式：
         1.获取参数
             1.1 user:当前登陆的用户对象，avatar:上传的图片数据
         2.参数检验
             2.1 非空判断
         3.逻辑处理
             3.1 调用工具类将图片数据上传到骑牛云
             3.2 将返回的图片名称给予avatar_url赋值，并保存回数据库
             3.3 将图片的完整url返回
         4.返回值
    """
    # GET请求方式:返回修改用户头像页面
    if request.method == "GET":
        return render_template("profile/user_pic_info.html")

    # POST请求：提交头像数据并修改保存
    """
        1.获取参数
            1.1 avatar:上传的图片数据，user:当前用户对象
        2.参数检验
            2.1 非空判断
        3.逻辑处理
            3.1 调用工具类将图片数据上传到七牛云
            3.2 将返回的图片名称给予avatar_urlfuzhi ,并保存到数据库
            3.3 将图片的完整url返回
        4.返回值
    """
    # 1.1 avatar:上传的图片数据，user:当前用户对象
    avatar = request.files.get("avatar")

    avatar_data = None
    try:
        # 获取图片的二进制格式数据
        avatar_data = avatar.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="图片数据读取失败")

    # 获取当前登录用户
    user = g.user

    # 2.1 非空判断
    if not  avatar_data:
        return jsonify(errno=RET.NODATA, errmsg="图片数据为空")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 3.1 调用工具类将图片数据上传到七牛云
    try:
        pic_name = pic_storage(avatar_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片到七牛云异常")


    # 3.2 将返回的图片名称给予avatar_urlfuzhi ,并保存到数据库
    user.avatar_url = pic_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户图像异常")

    # 3.3 将图片的完整url返回
    # 格式：域名前缀 + 图片名称
    full_url = constants.QINIU_DOMIN_PREFIX + pic_name

    # 4. 返回上传图片成功
    return jsonify(errno=RET.OK, errmsg="返回上传图片成功",  data={"avatar_url":full_url})

#127.0.0.1:5000/user/baseinfo --用户基本资料页面
@profile_bp.route("/baseinfo", methods=["GET","POST"])
@get_user_data
def baseinfo():
    user = g.user
    # GET请求：返回用户基本资料
    if request.method == "GET":

        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("profile/user_base_info.html", data=data)

    # POST请求：修改用户基本资料
    """
     1.获取参数
         1.1 user:当前登陆的用户对象，signature:个性签名， nick_name取:昵称，gender:性别
     2.参数检验
         2.1 非空判断
         2.2 gender in ['MAN', 'WOMAN']
     3.逻辑处理
         3.1 将当前用户的各个属性重新赋值，保存到数据库即可
     4.返回值
    """
    # 1.1 user:当前登陆的用户对象，signature:个性签名， nick_name取:昵称，gender:性别
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    # 2.1 非空判断
    if not all([signature,nick_name,gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 2.2 gender in ['MAN', 'WOMAN']
    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.1 将当前用户的各个属性重新赋值，保存到数据库即可
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    # 注意：修改了昵称nick_name，会话对象中的数据也要调整
    session["nick_name"] = nick_name

    # 将上述操作保存到数据库
    try:
       db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存用户数据对象异常")

    # 4.返回值
    return jsonify(errno=RET.OK, errmsg="修改用户基本数据成功")


#127.0.0.1:5000/user/info --个人中心页面
@profile_bp.route("/info")
@get_user_data
def user_info():
    """展示个人中心页面"""
    user = g.user
    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template("profile/user.html", data=data)