from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework_jwt.views import ObtainJSONWebToken

from users.utils import TokenManager
from meiduo_mall.utils.captcha.captcha import captcha
from verifications.views import SMSCodeView
from .serializers import UserSerializer, UserDetailSerializer, EmailSerializer, UserAddressSerializer, \
    AddressTitleSerializer
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection

from .models import User
from goods.models import SKU
from goods.serializers import SKUSerializer
from .serializers import UserBrowseHistorySerializer
from carts.utils import merge_cart_cookie_to_redis

import re
import pickle, base64


# Create your views here.


class ForgetPasswordAccountsVerify(APIView):
    """验证账户名和图片验证码"""

    def get(self, request, account):
        # 1.获取参数
        image_code_text = request.query_params.get("text")
        image_code_id = request.query_params.get("image_code_id")

        # 2.通过image_code_id从redis数据库中取出真实的图片验证码数据,校验图片验证码
        try:
            redis_conn = get_redis_connection("verify_codes")
            real_image_code = redis_conn.get('ImageCode_' + image_code_id)
        except Exception as e:
            return Response({"message": "图片验证码不存在"}, status=status.HTTP_400_BAD_REQUEST)

        if real_image_code and image_code_text.lower() == real_image_code.decode().lower():
            redis_conn.delete("ImageCode_" + image_code_id)
        else:
            return Response({"message": "图片验证码输入错误"}, status=status.HTTP_400_BAD_REQUEST)

        # 3.尝试获取用户,获取用户的手机号码
        try:
            if re.match('^1[3-9]\d{9}$', account):
                # 帐号为手机号
                user = User.objects.get(mobile=account)
            else:
                # 帐号为用户名
                user = User.objects.get(username=account)
        except User.DoesNotExist:
            return Response({"message": "请输入正确的手机号或用户名"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            phone_num = user.mobile

        # 生成token
        tokenMG = TokenManager()
        token = tokenMG.generate_token({"mobile": phone_num})

        return Response({'mobile': phone_num, "access_token": token})


class ForgetPasswordSendSMSCode(APIView):
    """"发送短信"""

    def get(self, requset):
        token = requset.query_params.get("access_token")
        tokenMG = TokenManager()
        try:
            data = tokenMG.parse_token(token=token)
        except:
            return Response({"message": "token无效"}, status=status.HTTP_400_BAD_REQUEST)
        # mobile = int(data)
        mobile = data.get("mobile")
        resp = SMSCodeView().get(requset, mobile=mobile)
        return resp


class ForgetPasswordCommit(APIView):
    """验证手机号及短信验证码"""

    def get(self, request, account):
        try:
            if re.match('^1[3-9]\d{9}$', account):
                # 帐号为手机号
                user = User.objects.get(mobile=account)
            else:
                # 帐号为用户名
                user = User.objects.get(username=account)
        except User.DoesNotExist:
            return Response({"message": "请输入正确的手机号或用户名"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_id = user.id
            mobile = user.mobile

        # 1.获取查询字符串中的sms_code
        sms_code = request.query_params.get("sms_code")

        # 2.连接redis数据库
        redis_conn = get_redis_connection('verify_codes')

        # 3.从数据库中取出sms_code验证前端输入的验证码
        real_sms_code = redis_conn.get("sms_%s" % mobile)

        if real_sms_code.decode() != sms_code:
            return Response({"message": "短信验证码输入错误"}, status=status.HTTP_400_BAD_REQUEST)

        # 生成token
        tokenMG = TokenManager()
        token = tokenMG.generate_token({"user_id": user_id})

        return Response({"user_id": user_id, "access_token": token})


class ResetPassWord(APIView):
    """重新设置密码"""

    def post(self, request):
        password = request.data.get("password")
        access_token = request.data.get("access_token")
        tokenMG = TokenManager()
        try:
            user_id = tokenMG.parse_token(token=access_token).get("user_id")
        except:
            return Response({"message": "token有误"})
        else:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()

        return Response({"message": "重置密码完成"}, status=status.HTTP_200_OK)


class ImageCodeIdView(APIView):
    """生成图片验证码"""

    def get(self, request, image_code_id):
        # 1.生成验证图片image_data
        image_name, real_image_code, image_data = captcha.generate_captcha()
        # 2.保存验证图片的内容存储到redis
        try:
            redis_conn = get_redis_connection("verify_codes")
            redis_conn.setex('ImageCode_' + image_code_id, 300, real_image_code)
        except:
            Response({"message": "验证码存储有误"})
        # 3.指定响应的数据格式为'image/jpg'
        return HttpResponse(image_data, content_type='image/jpg')


class UserAuthorizeView(ObtainJSONWebToken):
    """重写账号密码登录视图"""

    def post(self, request, *args, **kwargs):
        response = super(UserAuthorizeView, self).post(request, *args, **kwargs)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            merge_cart_cookie_to_redis(request, user, response)

        return response


# POST/GET  /browse_histories/
class UserBrowseHistoryView(CreateAPIView):
    """用户浏览记录"""

    # 指定序列化器(校验)
    serializer_class = UserBrowseHistorySerializer
    # 指定权限
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """读取用户浏览记录"""
        # 创建redis连接对象
        redis_conn = get_redis_connection('history')
        # 查询出redis中当前登录用户的浏览记录[b'1', b'2', b'3']
        sku_ids = redis_conn.lrange('history_%d' % request.user.id, 0, -1)

        # 把sku_id对应的sku模型取出来
        # skus = SKU.objects.filter(id__in=sku_ids)  # 此查询它会对数据进行排序处理
        # 查询sku列表数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)

        # 序列化器
        serializer = SKUSerializer(sku_list, many=True)

        return Response(serializer.data)


class AddressViewSet(UpdateModelMixin, CreateModelMixin, GenericViewSet):
    """用户收货地址"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer

    def create(self, request, *args, **kwargs):
        """新增收货地址"""
        # 判断用户的收货地址数据是否上限
        # address_count = Address.objects.filter(user=request.user).count()
        address_count = request.user.addresses.count()
        if address_count > 20:
            return Response({"message": '收货地址数量上限'}, status=status.HTTP_400_BAD_REQUEST)
            # 创建序列化器给data参数传值(反序列化)
            # serializer = UserAddressSerializer(data=request.data, context={'request': request})
            # 调用序列化器的is_valid方法
            # serializer.is_valid(raise_exception=True)
            # 调用序列化器的save
            # serializer.save()
            # 响应
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super(AddressViewSet, self).create(request, *args, **kwargs)

    def get_queryset(self):
        """获取查询集对象"""
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VerifyEmailView(APIView):
    """邮箱验证"""

    def get(self, request):
        # 获取token
        token = request.query_params.get("token")
        if not token:
            return Response({"message": "缺失token"}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if not user:
            return Response({"message": "无效token"}, status=status.HTTP_400_BAD_REQUEST)

        # 修改email_active：改变邮箱认证状态
        user.email_active = True
        user.save()

        return Response({"message": "ok"})


# PUT /email/
class EmailView(UpdateAPIView):
    """保存用户邮箱"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


# GET /user/
class UserDetailView(RetrieveAPIView):
    """用户详情"""
    serializer_class = UserDetailSerializer
    # 权限配置：认证用户才可以执行该视图的逻辑
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# POST /users/
class UserView(CreateAPIView):
    """用户注册"""
    # 指定序列化器
    serializer_class = UserSerializer


class UsernameCountView(APIView):
    """验证用户名是否已存在"""

    def get(self, request, username):
        # 查询用户名是否存在
        count = User.objects.filter(username=username).count()

        # 构建响应数据
        data = {
            'count': count,
            'username': username
        }
        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """验证手机号是否已存在"""

    def get(self, request, mobile):
        # 查询手机号数量
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'count': count,
            'mobile': mobile
        }
        return Response(data)
