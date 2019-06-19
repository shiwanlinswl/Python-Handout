"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
import xadmin

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'xadmin/', include(xadmin.site.urls)),

    # 包含发送短信验证码模块路由
    url(r'^', include('verifications.urls')),

    # 用户模块路由
    url(r'^', include('users.urls')),

    # qq登陆
    url(r'^oauth/', include('oauth.urls')),

    # 省市区
    url(r'^', include('areas.urls')),

    # 富文本编辑界面路由
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    # 商品模块
    url(r'^', include('goods.urls')),

    # 购物车模块
    url(r'^', include('carts.urls')),
    # 订单模块
    url(r'^', include('orders.urls')),


]