from itsdangerous import TimedJSONWebSignatureSerializer as Serializer ,BadData
from django.conf import settings


def generate_save_user_token(openid):
    """对openid进行加密"""
    # 1.创建序列化器对象
    serializer = Serializer(settings.SECRET_KEY, 600)
    # 2.调用对象的dumps()方法，将字典数据转化为json字符串
    data = {'openid': openid}
    data_bytes = serializer.dumps(data)
    # 3.将openid数据返回
    return data_bytes.decode()


def check_save_user_token(openid):
    """对加密的openid进行解密"""
    serializer = Serializer(settings.SECRET_KEY, 600)
    try:
        # 调用loads()方法对openid进行解码
        data = serializer.loads(openid)
    except BadData:
        return None
    else:
        return data.get('openid')
