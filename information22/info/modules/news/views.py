from flask import current_app, jsonify, abort, g, session
from flask import request

from info import constants, db
from info.models import User, News, Comment, CommentLike
from info.modules.news import news_bp
from flask import render_template

from info.response_code import RET
from info.utils.common import get_user_data


# 127.0.0.1:5000/news/followed_user
@news_bp.route('/followed_user', methods=['POST'])
@get_user_data
def followed_user():
    """关注/取消关注"""
    """
    1.获取参数
        1.1 user:当前登录的用户, user_id:新闻作者id，action:关注、取消关注行为
    2.校验参数
        2.1 非空判断
    3.逻辑处理
        3.0 根据user_id查询当前新闻的'作者对象'
        3.1 关注：
            方式1.author作者添加到当前用户的关注列表中:
              user.followed.append(author)

            方式2.user当前用户添加作者粉丝列表:
              author.followers.append(user)

        3.2 取消关注：author作者从到当前用户的关注列表中移除 or user当前用户从添加作者粉丝列表移除
        3.3 将上述修改操作保存回数据库
    4.返回值
    """
    # 1.1 user:当前登录的用户, user_id:新闻作者id，action:关注、取消关注行为
    user = g.user
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    # 2.1 非空判断
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    if action not in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.0 根据user_id查询当前新闻的作者对象
    try:
        author = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")
    if not author:
        return jsonify(errno=RET.NODATA, errmsg="作者不存在")

    """
    # 3.1 关注：
    #             1.author作者添加到当前用户的关注列表中:
    #               user.followed.append(author)
    #
    #             2.user当前用户添加作者粉丝列表:
    #               author.followers.append(user)
    """
    if action == "follow":
        # 用户已经在作者粉丝列表中
        if user in author.followers:
            return jsonify(errno=RET.DATAEXIST, errmsg="已经关注不能重复关注")
        else:
            # 把当前用户添加到作者的粉丝列表：表示当前用户关注了作者
            author.followers.append(user)
    # 3.2 取消关注：author作者从到当前用户的关注列表中移除 or user当前用户从添加作者粉丝列表移除
    else:
        # 只有用户已经在关注列表中才有资格取消关注
        if user in author.followers:
            author.followers.remove(user)

    # 3.3 将上述修改操作保存回数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存关注信息对象异常")

    return jsonify(errno=RET.OK, errmsg="ok")


# POST请求方式：127.0.0.1:5000/news/comment_like  参数是请求携带
@news_bp.route('/comment_like', methods=["POST"])
@get_user_data
def comment_like():
    """评论点赞&取消点赞接口"""
    """
     1.获取参数
         1.1 comment_id:评论id,user:当前登陆的用户对象， action:点赞和取消点赞的行为
     2.参数检验
         2.1 非空判断
         2.2 action in ['add', 'remove']
     3.逻辑处理
         3.1 根据comment_id查询当前评论对象
         3.2 根据行为判断点赞还是取消点赞
         3.3点赞：创建CommentLike对象，并给各个属性赋值，保存到数据库
            3.3.1 对评论对象上的like_count累加
         3.4取消点赞：删除CommentLike对象，保存到数据库
            3.4.1 对评论对象上的like_count减一
     4.返回值
    """

    # 1.1 comment_id:评论id,user:当前登陆的用户对象， action:点赞和取消点赞的行为
    params_dict = request.json
    comment_id = params_dict.get("comment_id")
    action = params_dict.get("action")
    user = g.user

    # 2.1 非空判断
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 2.2 action in ['add', 'remove']
    if action not in ['add', 'remove']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.1 根据comment_id查询当前评论对象
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询评论对象异常")
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 3.2 根据行为判断点赞还是取消点赞
    # 3.3点赞：创建CommentLike对象，并给各个属性赋值，保存到数据库
    if action == "add":

        # 查询CommentLike对象是否存在，如果不存在才创建comment_like对象
        try:
            comment_like_obj = CommentLike.query.filter(CommentLike.comment_id == comment.id,
                                     CommentLike.user_id == user.id
                                     ).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询点赞对象异常")

        # 如果不存在才创建comment_like对象
        if not comment_like_obj:
            # 通过CommentLike类创建commit_like对象
            comment_like = CommentLike()
            # 点赞的评论id
            comment_like.comment_id = comment.id
            # 点赞的用户id
            comment_like.user_id = comment.user_id
            # 3.3.1 对评论对象上的like_count累加
            comment.like_count += 1

            # 保存回数据库
            db.session.add(comment_like)

    # 3.4取消点赞：删除CommentLike对象，保存到数据库
    else:
        # 查询CommentLike对象是否存在，如果不存在才创建comment_like对象
        try:
            comment_like_obj = CommentLike.query.filter(CommentLike.comment_id == comment.id,
                                                        CommentLike.user_id == user.id
                                                        ).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询点赞对象异常")

        # 如果存在评论点赞模型才有资格取消点赞
        if comment_like_obj:
            db.session.delete(comment_like_obj)
            # 3.4.1 对评论对象上的like_count减一

    # 将上述操作提交到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存评论对象异常")

    # 4.返回值
    return jsonify(errno=RET.OK, errmsg="OK")


# POST请求方式：127.0.0.1:5000/news/news_comment  参数是请求携带
@news_bp.route('/news_comment', methods=["POST"])
@get_user_data
def news_comment():
    """发布新闻(主、子)评论的后端接口"""
    """
     1.获取参数
         1.1 news_id:当前新闻的id,user:当前登陆的用户对象，comment:新闻评论的内容， parent_id:区分主评论，子评论的参数
     2.参数检验
         2.1 非空判断
     3.逻辑处理
         3.1 根据新闻id查询当前新闻对象
         3.2 创建评论对象，并给各个属性赋值，保存回数据库
     4.返回值
    """

    # 1.1 news_id:当前新闻的id,user:当前登陆的用户对象，comment:新闻评论的内容， parent_id:区分主评论，子评论的参数
    params = request.json
    news_id = params.get("news_id")
    content = params.get("comment")
    parent_id = params.get("parent_id")
    user = g.user

    # 2.1 非空判断
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 3.1 根据新闻id查询当前新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻对象异常")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻对象不存在")

    # 3.2 创建评论对象，并给各个属性赋值，保存回数据库
    comment_obj = Comment()
    comment_obj.user_id = user.id
    comment_obj.news_id = news.id
    comment_obj.content = content
    # 区分主评论和子评论
    if parent_id:
        # 代表是一条子评论
        comment_obj.parent_id = parent_id

    try:
        db.session.add(comment_obj)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 4.返回值评论对象的字典数据
    return jsonify(errno=RET.OK, errmsg="发布评论成功", data=comment_obj.to_dict())


# POST请求方式：127.0.0.1:5000/news/news_collect  参数是请求携带
@news_bp.route('/news_collect', methods=["POST"])
@get_user_data
def news_collect():
    """新闻收藏，取消收藏的后端接口"""
    """
    1.获取参数
        1.1 news_id:当前新闻的id,user:当前登陆的用户对象，action:收藏，取消收藏的行为
    2.参数检验
        2.1 非空判断
        2.2 action in ['collect', 'cancle_collect']
    3.逻辑处理
        3.1 根据新闻id查询当前新闻对象，判断新闻是否存在
        3.2 收藏：将新闻对象添加到user.collection_news列表中
        3.3 取消收藏：将新闻对象从user.collection_news列表中移除
    4.返回值
    """
    #  1.1 news_id:当前新闻的id,user:当前登陆的用户对象，action:收藏，取消收藏的行为
    param_dict = request.json
    news_id = param_dict.get('news_id')
    action = param_dict.get('action')
    user = g.user
    # 2.1 非空判断
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    # 2.2 action in ['collect', 'cancel_collect']
    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.1 根据新闻id查询当前新闻对象，判断新闻您是否存在
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻对象异常")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 3.2 收藏：将新闻对象添加到user.collection_news列表中
    if action == "collect":
        user.collection_news.append(news)
    # 3.3 取消收藏：将新闻对象从user.collection_news列表中移除
    else:
        # 新闻已经被用户收藏的情况才允许取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)

    # 3.4
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存失败")

    # 4.返回成功
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_bp.route('/<int:news_id>')
@get_user_data
def news_detail(news_id):
    """点击显示新闻详情"""

    """
    ---------1.用户登陆成功,查询用户基本信息展示---------

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
    """
    # 使用g对象传递user对象数据
    user = g.user

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

    # ---------3.根据新闻news_id查询新闻详情展示---------
    news_obj = None
    if news_id:
        try:
            news_obj = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
            return jsonify(errno=RET.DBERR, errmsg="查询新闻对象异常")

    # 将新闻对象的点击量累加
    news_obj.clicks += 1

    # 查询到的新闻对象转换为字典对象
    new_dict = news_obj.to_dict() if news_obj else None

    # ---------4.查询当前用户是否收藏过当前新闻---------
    # 标识当前用户是否收藏当前新闻，默认值False：没有收藏

    # 标识当前用户是否已经被收藏，默认是没被收藏
    is_collected = False
    # 标识当前登录用户是否已经关注新闻作者，默认值false是没关注
    is_followed = False

    # 防止退出登录user.collection_news没有值导致报错
    if user:
        # User.collection_news:当前用户对象收藏的新闻列表数据
        # news_obj:当前新闻对象
        # 判断当前新闻你对象是否在当前用户对象收藏的新闻列表中
        if news_obj in user.collection_news:
            # 标识当前用户已经收藏该新闻
            is_collected = True

    # ---------5.查询评论列表数据---------
    try:
       comment_list = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    commentlike_obj_list = []
    if user:
        # ---------6.查询当前用户具体对那几条评论点赞了---------
        # 1.查询当前新闻的所有评论，取得所有评论的id -> list[1,2,3,4,5,6]
        comment_id_list = [comment.id for comment in comment_list]

        # 2.再通过评论点赞模型(CommentLike)查询当前用户点赞了那几条评论  —>[模型1,模型2...]
        try:
            commentlike_obj_list = CommentLike.query.filter(CommentLike.comment_id.in_(comment_id_list),
                                    CommentLike.user_id == user.id
                                     ).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="删除真实的图片验证码异常")

    # 3.遍历上一步的评论点赞模型列表，获取所以点赞过的评论id（comment_like.comment_id）
    # 点过赞的评论列表[1,3,5]
    commentlike_id_list = [commentlike.comment_id for commentlike in commentlike_obj_list]

    comment_dict_list = []
    # 评论对象列表转为字典列表
    for comment in comment_list if comment_list else []:
        # 对象转为字典
        comment_dict = comment.to_dict()
        # 所有评论对象默认是没点赞的
        comment_dict["is_like"] = False

        # comment.id == 1 in [1,3,5] ---> comment_dict["is_like"] = True
        # comment.id == 2 in [1,3,5] ---> comment_dict["is_like"] = False
        # comment.id == 3 in [1,3,5] ---> comment_dict["is_like"] = True
        # 当前评论的id在用户点赞的id列表中，将is_like标识为True表示点赞
        if comment.id in commentlike_id_list:
            comment_dict["is_like"] = True
        comment_dict_list.append(comment_dict)

    # ---------7.查询当前用户是否已经关注新闻作者 - --------
    # 标识当前登录用户是否已经关注新闻作者，默认值false是没关注
    is_collected = False
    """
    author:作者
    user:当前登录用户
    user.followers:作者的粉丝列表
    useer.followed:用户的关注列表

    当前登录用户关注新闻作者两种表现形式：
        当前用户在作者的粉丝列表：user in author.followers
        作者在用户的关注列表中：author in user.followed
    """
    # 1.查询当前作者
    try:
        author = User.query.filter(User.id == news_obj.user_id).first()
    except Exception as e:
        current_app.logger.error(e)

    if user and author:
        # 当前用户在作者的粉丝列表
        if user in author.followers:
            is_followed = True

    # 4.组织响应数据
    data = {
        "user_info": user_dict,
        "click_news_list": news_dict_list,
        "news": new_dict,
        "is_collected": is_collected,
        "comments": comment_dict_list
    }

    return render_template("news/detail.html", data=data)