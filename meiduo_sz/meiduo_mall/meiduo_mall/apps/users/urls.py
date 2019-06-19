from django.conf.urls import url
# from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    # 注册用户
    url(r'^users/$', views.UserView.as_view()),

    # 判断用户名是否已存在
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),

    # 判断手机号是否已存在
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

    # JWT登录
    # url(r'^authorizations/$', obtain_jwt_token),
    # 账号密码登录时需要 做cookie购物车合并到redis操作
    url(r'^authorizations/$', views.UserAuthorizeView.as_view()),

    # 用户中心个人信息
    url(r'^user/$', views.UserDetailView.as_view()),

    # 保存用户邮箱
    url(r'^email/$', views.EmailView.as_view()),

    # 激活邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),

    # 浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistoryView.as_view()),

    # 生成图片验证码
    url(r'^image_codes/(?P<image_code_id>.+)/$', views.ImageCodeIdView.as_view()),

    # 验证码和用户名校验
    url(r'^accounts/(?P<account>\w+)/sms/token/$', views.ForgetPasswordAccountsVerify.as_view()),

    # 忘记密码发送短信
    url(r'^sms_codes/$', views.ForgetPasswordSendSMSCode.as_view()),

    # 提交身份验证信息
    url(r'^accounts/(?P<account>\w+)/password/token/$', views.ForgetPasswordCommit.as_view()),

    # 重置密码
    url(r'^users/[0-9]+/password/$', views.ResetPassWord.as_view()),

]

# 路由器方式
router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')

urlpatterns += router.urls
