from django.shortcuts import render
from rest_framework import status
from rest_framework_jwt.settings import api_settings

from rest_framework_jwt.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework.response import Response
from .models import OAuthQQUser
import logging
from .serializers import QQAuthUserSerializer
from .utils import generate_save_user_token
from carts.utils import merge_cart_cookie_to_redis

logging.getLogger('django')

# Create your views here.


class QQAuthUserView(APIView):
    """QQ登陆成功的回调处理"""
    def get(self, request):
        # 1.获取查询参数中的code参数
        code = request.query_params.get('code')
        if not code:
            return Response({"message": "缺少code"}, status=status.HTTP_400_BAD_REQUEST)

        # 1.1 创建QQ登陆SDK对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        try:
            # 2.通过code向QQ服务器中请求access_token
            access_token = oauth.get_access_token(code)

            # 3.通过access_token向QQ服务器中请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as error:
            # 使用日志记录错误信息
            logging.info(error)
            return Response({"message": "QQ服务器异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            # 4.查询openid是否有绑定过美多商城用户
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果openid未绑定用户，则创建新的用户并绑定openid
            # 把openid进行加密处理，先响应给浏览器，暂时帮忙保存着
            openid_sin = generate_save_user_token(openid)
            return Response({'access_token': openid_sin})

        else:
            # 如果openid已绑定用户，则生成jwt token，并返回

            # 手动生成token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数
            # 通过 对象.外键:获取oauth_user的user
            user = oauth_user.user
            payload = jwt_payload_handler(user)  # 生成荷载
            token = jwt_encode_handler(payload)  # 根据荷载生成token

            response = Response({
                "token": token,
                "username": user.username,
                "user_id": user.id
            })

            # 做cookie购物车合并到redis操作
            merge_cart_cookie_to_redis(request, user, response)

            # 返回
            return response

    def post(self, request):
        # 创建序列化器进行反序列化:校验绑定数据
        serializer = QQAuthUserSerializer(data=request.data)
        # 验证输入数据的有效性
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 手动生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数

        payload = jwt_payload_handler(user)  # 生成荷载
        token = jwt_encode_handler(payload)  # 根据荷载生成token

        response = Response({
            "token": token,
            "username": user.username,
            "user_id": user.id,
        })

        # 做cookie购物车合并到redis操作
        merge_cart_cookie_to_redis(request, user, response)

        # 返回
        return response


class QQAuthURLView(APIView):
    """
    提供QQ登陆页面网址
    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    创建QQ登陆sdk对象需要传入的参数
    QQ_CLIENT_ID = '101474184'
    QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
    QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
    """

    def get(self, request):
        # 1.获取next参数路径
        # next表示从哪个页面进入登录界面，登陆成功后就进入哪个页面
        next = request.query_params.get('next')
        if not next:
            next = '/'

        # 2.创建QQ登陆SDK对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        # 3.调用OAuthQQ中的get_qq_url方法获取QQ登录页面链接
        login_url = oauth.get_qq_url()

        # 4.把扫描url响应给前端
        return Response({"login_url": login_url})

