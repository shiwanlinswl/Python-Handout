from django.conf import settings
from django.contrib.auth.backends import ModelBackend

import re
from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt登录验证的响应体"""
    return {
        "username": user.username,
        'token': token,
        'user_id': user.id,
    }


def get_user_by_account(account):
    """通过传入手机号或用户名动态查找user"""

    # # 判断account是不是手机号
    # if re.match(r'1[3-9]\d{9}', account):
    #     # 表示是手机号登录
    #     try:
    #         user = User.objects.get(mobile=account)
    #     except User.DoesNotExist:
    #         return None
    #
    # else:
    #     # 用户名登录
    #     try:
    #         user = User.objects.get(username=account)
    #     except User.DoesNotExist:
    #         return None

    # zx15312345678  # 如果想要实现多账号登录用户名必须不能以数字
    # 13981234567
    try:
        if re.match(r'1[3-9]\d{9}', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义django认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方式,使用多账号登录
        :param request:   本次登录请求对象
        :param username: 用户名/手机号
        :param password: 密码
        :return: 要么返回查到的user/None
        """

        # 1.通过传入的username 获取到user对象(通过手机号或用户名动态查询user)
        user = get_user_by_account(username)
        # 2.判断user的密码
        if user and user.check_password(password):
            return user
        else:
            # 3. 返回user/None
            return None


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired


class TokenManager:
    def __init__(self, secret_key=settings.SECRET_KEY, expiration=60*5):
        self.SECRET_KEY = secret_key
        self.expiration = expiration

    def generate_token(self, data):
        """
        生成token,并在token中保存数据
        :param data: dict
        :return: token: str
        """
        s = Serializer(self.SECRET_KEY, expires_in=self.expiration)
        token = s.dumps(data)
        return token

    def parse_token(self, token):
        """
        解析token,返回中间加密的内容
        :param token:  str
        :return: data:  dict
        """
        s = Serializer(self.SECRET_KEY)
        try:

            data = s.loads(token)
            # data = data.get("mobile")
        except SignatureExpired:
            raise Exception("token 过期")
        except BadSignature:
            raise Exception('token 错误')
        return data
