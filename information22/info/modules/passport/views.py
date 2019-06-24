from flask import session
from info.modules.passport import passport_bp
from flask import request, current_app, abort, make_response, jsonify
from info.utils.captcha.captcha import captcha
from info import redis_store, db
from info import constants
from info.response_code import RET
import re
from info.models import User
from info.lib.yuntongxun.sms import CCP
from datetime import datetime


# post请求url地址：/passport/login_out
@passport_bp.route("/login_out", methods=["POST"])
def login_out():
    """退出登陆"""

    # 删除session中的用户数据即可
    session.pop("user_id")
    session.pop("mobile")
    session.pop("nick_name")
    # 注意：管理员用户退出的时候需要退出请求
    try:
        session.pop("is_admin")
    except Exception as e:
        # 提示退出登陆
        return jsonify(errno=RET.OK, errmsg="普通用户退出登录成功")
    else:
        return jsonify(errno=RET.OK, errmsg="管理员用户退出登录成功")


# post请求url地址：/passport/login
@passport_bp.route("/login", methods=["POST"])
def login():
    """用户登陆的后端接口"""
    """
    1.获取参数
        1.1 mobile:手机号码 ， password:密码
    2.校验参数
        2.1 非空校验
        2.2 手机号码格式校验
    3.逻辑处理
        3.1 根据手机号码去查询当前用户
        3.2 使用user对象判断用户填写的密码是否跟数据库里的一致
        3.3 使用session记录用户登陆消息
    4.返回值
    """
    # 1.1 mobile: 手机号码 ， password: 密码
    param_dict = request.json
    mobile = param_dict.get("mobile")
    password = param_dict.get("password")

    # 2.1 非空校验
    if not all([mobile, password]):
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 2.2 手机号码格式校验
    if not re.match("1[3456789][0-9]{9}", mobile):
        current_app.logger.error("手机格式错误")
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")

    # 3.1 根据手机号码去查询当前用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户查询异常")

    # 如果用户不存在时：
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 3.2 使用user对象判断用户填写的密码是否跟数据库里的一致
    if not user.check_password(password):
        # 密码填写错误
        return jsonify(errno=RET.DBERR, errmsg="密码填写错误")

    # 3.3 使用session记录用户登陆消息
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 3.4 修改用户最后一次登陆时间
    user.last_login = datetime.now()

    try:
        # 如果是修改只需要提交即可，不用add
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 4 返回登陆成功
    return jsonify(errno=RET.OK, errmsg="登陆成功")


# get请求url地址:/passport/image_code?code_id=UUID编码
@passport_bp.route("/image_code")
def get_image_code():
    """获取验证码图片的后端接口"""
    """
    1.获取参数
        1.1 code_id:UUID通用的唯一编码,作为key将验证码真实值存储到redis数据库
    2.校验参数
        2.1 非空判断code_id不能为空
    3.逻辑处理
        3.1 生成验证码图片,验证码图片的真实值
        3.2 code_id作为key将验证码图片的真实值保存懂啊redis数据库,并且设置有效时长(5分钟)
    4.返回值
        4.1 返回验证码图片
    """
    # 1.1 code_id: UUID通用的唯一编码, 作为key将验证码真实值存储到redis数据库
    code_id = request.args.get("code_id")
    # 2.1非空判断code_id不能为空
    if not code_id:
        current_app.logger.error("参数不足")
        abort(404)

    # 3.1生成验证码图片, 验证码图片的真实值
    image_name, real_image_code, image_data = captcha.generate_captcha()

    # 3.2code_id作为key将验证码图片的真实值保存懂啊redis数据库, 并且设置有效时长(5分钟)
    try:
        redis_store.setex("CODEID_%s" % code_id, constants.IMAGE_CODE_REDIS_EXPIRES, real_image_code)
    except Exception as e:
        current_app.logger.error(e)

    # 4.1返回验证码图片(返回的数据默认是二进制格式,不一定适用与所有的浏览器)
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/JPEG"
    return response


# post请求地址:/passport/sms_code,参数适用请求体携带
@passport_bp.route("/sms_code", methods=["POST"])
def send_sms_code():
    """发送短信验证后端接口"""
    """
    1.获取参数
        1.1 mobile:手机号码 , image_code:用户填写的图片验证码 , image_code_id:UUID编码
    2.参数校验
        2.1 非空判断
        2.2 正则校验手机号码格式
    3.逻辑处理
        3.1 根据image_code_id编号去redis数据库获取真是的图片验证码值real_image_code
            3.1.1 real_image_code没有值:图片验证码过期
            3.1.2 real_image_code有值:将图片验证码从redis中删除(防止多次适用同一个验证码来进行多次验证码验证)
        3.2 对比用户添加的图片验证码值和真实的图片验证码值
            3.2.1 不相等:提示图片验证码填写错误
            3.2.2 相等:发送短信验证码

        TODO:判断用户填写的手机号码是否注册(提高用户体验)

        3.3 发送短信验证码具体流程
            3.3.1 生成6位的随机短信验证码值
            3.3.2 调用ccp类中方法发送短信验证码
            3.3.3 发送短信验证码失败:提示前端重新发送
            3.3.4 将6位的短信验证码使用redis数据库保存起来,设置有效时长(方便注册接口获取真实的短信验证值)
    4.返回值
        4.1 发送短信验证码成功
    """

    # 1.1 mobile: 手机号码, image_code: 用户填写的图片验证码, image_code_id: UUID编码（格式：json）
    # 将前端发送的json数据转换成python对象
    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id = param_dict.get("image_code_id")

    # 2.1非空判断
    if not all([mobile, image_code, image_code_id]):
        err_dict = {"errno": RET.PARAMERR, "errmsg": "参数不足"}
        """
        {
        "errno":4103,
        "errmsg":"参数不足"
        }
        """
        return jsonify(err_dict)

    # 2.2正则校验手机号码格式
    if not re.match("1[3456789][0-9]{9}", mobile):
        current_app.logger.error("手机格式错误")
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")

    # 3.1根据image_code_id编号去redis数据库获取真是的图片验证码值real_image_code
    try:
        real_image_code = redis_store.get("CODEID_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取真实的图片验证码错误")

    # 3.1.1 real_image_code没有值: 图片验证码过期
    if not real_image_code:
        current_app.logger.error("图片验证码过期了")
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期了")
    # 3.1.2 real_image_code有值: 将图片验证码从redis中删除(防止多次适用同一个验证码来进行多次验证码验证)
    else:
        try:
            redis_store.delete("CODEID_%s" % image_code_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="删除真实的图片验证码异常")
    """
    细节：1.忽略大小写 2.对比时数据格式要一致,将从redis中获取的真实图片验证码值转换成字符串
    """
    if image_code.lower() != real_image_code.lower():
        # 3.2.1不相等: 提示图片验证码填写错误
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码填写错误")

    # 3.2.2相等: 发送短信验证码

    # TODO: 判断用户填写的手机号码是否注册(提高用户体验)
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    # 表示用户已经注册过
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="用户已经注册过")
    # 3.3.1生成6位的随机短信验证码值
    import random
    sms_code = random.randint(0, 999999)
    # 不足6位在前面补0
    sms_code = "%06d" % sms_code

    # 3.3.2调用ccp类中方法发送短信验证码
    # 参数1:手机号码 参数2：{6位短信验证码，5分钟过期时长} 参数3：模板编号
    result = CCP().send_template_sms(mobile, {sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60}, 1)

    if result == -1:
        # 3.3.3发送短信验证码失败: 提示前端重新发送
        return jsonify(errno=RET.THIRDERR, errmsg="云通讯发送短信验证码失败")
    elif result == 0:
        # 3.3.4将6位的短信验证码使用redis数据库保存起来, 设置有效时长(方便注册接口获取真实的短信验证值)
        #                        手机号码      短信内容       过期时长
        redis_store.setex("SMS_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 4.1发送短信验证码成功
        return jsonify(errno=RET.OK, errmsg="发送短信验证码成功")


# post请求地址:/passport/register,参数适用请求体携带
@passport_bp.route('/register', methods=["POST"])
def register():
    """注册后端接口实现"""
    """
    1.参数获取
        1.1 mobile:手机号码 ， sms_code:用户填写的验证码 ， password:未加密的密码
    2.参数检验
        2.1 非空判断
        2.2 手机号码格式验证
    3.逻辑处理
        3.1 根据手机号码获取redis中的真实短信验证码real_sms_code
            3.1.1 real_sms_code没有值：短信验证码过期了
            3.1.2 real_sms_code有值：从redis数据库中删除
        3.2 对比用户填写的sms_code验证码和redis数据库中保存的real_sms_code真实验证码是否一致
            3.2.1 不相等:提示短信验证填写错误
            3.2.2 相等：注册
        3.3 创建用户对象，并给各个属性赋值
        3.4 将用户存储到数据库
        3.5 注册成功就代表登陆成功，记录用户登陆信息到session中
    4.返回值
    """
    # 1.1 mobile: 手机号码 ， sms_code: 用户填写的验证码 ， password: 未加密的密码
    # 将前端发送的json数据转换成python对象
    param_dict = request.json
    mobile = param_dict.get("mobile")
    sms_code = param_dict.get("sms_code")
    password = param_dict.get("password")

    # 2.1 非空判断
    if not all([mobile, sms_code, password]):
        current_app.logger.error("参数不足")
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 2.2 手机号码格式验证
    if not re.match("1[3456789][0-9]{9}", mobile):
        current_app.logger.error("手机格式错误")
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")
    # 3.1 根据手机号码获取redis中的真实短信验证码real_sms_code
    try:
        real_sms_code = redis_store.get("SMS_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")
    # 3.1.2 real_sms_code有值：从redis数据库中删除
    if real_sms_code:
        redis_store.delete("SMS_%s" % mobile)
    # 3.1.1 real_sms_code没有值：短信验证码过期了
    else:
        current_app.logger.error("短信验证码过期了")
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期了")
    # 3.2对比用户填写的sms_code验证码和redis数据库中保存的real_sms_code真实验证码是否一致
    print(sms_code, real_sms_code)
    if sms_code != real_sms_code:
        # 3.2.1不相等: 提示短信验证填写错误
        return jsonify(errno=RET.DATAERR, errmsg="短信验证填写错误")

    # 3.2.2相等：注册
    # 3.3创建用户对象，并给各个属性赋值
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 记录当前时间为用户最后一次登陆时间
    user.last_login = datetime.now()
    # TODO:密码加密处理赋值
    # 方法1
    # user.set_hashpassword(password)

    # 方法2：会动态的添加这个password属性
    # 知识点：把方法当做属性来使用
    user.password = password

    # 3.4将用户存储到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 数据库回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="添加用户到数据库异常")

    # 3.5注册成功就代表登陆成功，记录用户登陆信息到session中
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 4.注册成功，返回值
    return jsonify(errno=RET.OK, errmsg="注册成功")
