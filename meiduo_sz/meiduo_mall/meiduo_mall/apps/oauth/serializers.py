from rest_framework import serializers
from .utils import check_save_user_token
from django_redis import get_redis_connection
from users.models import User
from .models import OAuthQQUser


class QQAuthUserSerializer(serializers.Serializer):
    """绑定用户的序列化器"""

    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        """对反序列化数据进行校验：attrs字典"""
        # 获取加密的openid
        access_token = attrs.get("access_token")
        # 获取解密的openid
        openid = check_save_user_token(access_token)

        if not openid:
            raise serializers.ValidationError('openid无效')

        # 把解密后的openid保存到反序列化的字典中以备后续使用
        attrs["access_token"] = openid

        # 连接redis数据库
        redis_conn = get_redis_connection('verify_codes')
        # 获取当前用户手机号
        mobile = attrs.get('mobile')
        # 获取数据库中真实的验证码
        real_sms_code = redis_conn.get("sms_%s" % mobile)

        # 获取前端发过来的验证码
        sms_code = attrs.get('sms_code')

        # 注意：从redis数据库中取来的数据都是bytes类型，需要进行解码
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('验证码错误')
        try:
            # 判断用户是否已经注册过
            user = User.objects.get(mobile=mobile)
        except User.DoseNotExist:
            pass
        else:
            password = attrs.get('password')
            # 检验注册用户的密码是否正确
            if not user.check_password(password):
                raise serializers.ValidationError("用户已存在，但密码不正确")
            else:
                # 将认证后的user放进校验字典中，后续会使用
                attrs["user"] = user
        return attrs

    def create(self, validated_data):
        """新增操作：将openid和user进行绑定"""
        # 反序列化后得到的数据
        user = validated_data.get('user')
        if not user:
            user = User(
                user=validated_data.get('mobile'),
                password=validated_data.get('password'),
                mobile=validated_data.get('mobile'),
            )
            # 对密码进行加密
            user.set_password(validated_data.get('password'))
            # 保存新增操作
            user.save()

        # 将用户绑定openid
        OAuthQQUser.objects.create(
            user=user,
            openid=validated_data.get("access_token")
        )

        return user

