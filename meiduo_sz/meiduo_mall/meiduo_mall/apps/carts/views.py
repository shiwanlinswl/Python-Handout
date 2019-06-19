from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
import pickle, base64
from rest_framework.response import Response
from rest_framework import status

from .serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelectedSerializer
from goods.models import SKU
# Create your views here.


class CartView(APIView):
    """定义购物车视图"""

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法,
        禁用认证/延后认证
        """
        pass

    def post(self, request):
        """添加购物车"""

        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get("sku_id")
        count = serializer.validated_data.get("count")
        selected = serializer.validated_data.get("selected")
        # 创建响应对象
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        # 对请求用户进行认证
        try:
            # 登录用户数据保存——>redis中
            user = request.user  # 获取登录用户,首次需要认证
            # 建立redis连接对象
            redis_conn = get_redis_connection("cart")
            pl = redis_conn.pipeline()
            # 记录购物车商品数量
            pl.hincrby('cart_%d' % user.id, sku_id, count)
            if selected:  # 判断当前商品是否勾选，如果勾选就加入到set集合中
                pl.sadd("selected_%d" % user.id, sku_id)
            pl.execute()
        except Exception:
            # 未登录用户数据保存——>浏览器cookie中
            # 获取cookie中的购物车数据
            cart_cookie = request.COOKIES.get("carts")

            if cart_cookie:
                # 将cookie中字符串转换为json字典
                cart_cookie_bytes = cart_cookie.encode()
                cart_ascii_bytes = base64.b64decode(cart_cookie_bytes)
                cart_dict = pickle.loads(cart_ascii_bytes)
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            # 更新cart_dict字典的数据
            cart_dict[sku_id] = {
                "count": count,
                "selected": selected
            }

            # 将更新后的字典数据保存到cookie中
            cart_ascii_bytes = pickle.dumps(cart_dict)
            cart_cookie_bytes = base64.b64encode(cart_ascii_bytes)
            cart_str = cart_cookie_bytes.decode()

            response.set_cookie("carts", cart_str)

        return response

    def get(self, request):
        """查询购物车"""
        try:
            # 如果能获取user,则是登录用户,就进行redis数据库操作
            user = request.user
        except Exception:
            user = None
        else:
            # 创建redis连接对象
            redis_conn = get_redis_connection("cart")
            # 获取hash数据
            cart_redis_dict = redis_conn.hgetall("cart_%d" % user.id)
            # 获取set集合数据
            selected_ids = redis_conn.smembers("selected_%d" % user.id)
            # 把redis的购物车数据转换成和cookie的购物车数据一样格式

            # 定义一个用来转换redis数据格式的大字典
            cart_dict = {}
            for sku_id_bytes in cart_redis_dict:
                cart_dict[int(sku_id_bytes)] = {
                    "count": int(cart_redis_dict[sku_id_bytes]),
                    # 如果sku_id_bytes在selected_ids即为True,表示勾选上了
                    "selected": sku_id_bytes in selected_ids
                }
        # 如果未获取到user则是未登录用户,进行cookie操作
        if not user:
            cart_str = request.COOKIES.get("carts")
            if cart_str:
                # 将cookie获取字符串转化为字典格式
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 无论是登录还是未登录用户统一进行以下序列化操作,注意缩进问题

        # 获取购物车中所有商品的sku模型
        skus = SKU.objects.filter(id__in=cart_dict.keys())

        # 遍历skus集合里的每个sku元素,为每个sku模型添加两个属性
        for sku in skus:
            sku.count = cart_dict[sku.id]["count"]
            sku.selected = cart_dict[sku.id]["selected"]

        # 创建序列化器,进行序列化操作
        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改购物车"""
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get("sku_id")
        count = serializer.validated_data.get("count")
        selected = serializer.validated_data.get("selected")
        # 创建响应对象
        response = Response(serializer.data)

        try:
            # 如果能获取user,则是登录用户,就进行redis数据库操作
            user = request.user
        except Exception:
            user = None
        else:
            # 创建redis连接对象
            redis_conn = get_redis_connection("cart")
            # 创建管道
            pl = redis_conn.pipeline()
            # 修改指定的sku购买数据,将hash中的sku_id的value覆盖掉
            pl.hset("cart_%d" % user.id, sku_id, count)
            # 修改商品勾选状态
            if selected:
                # 勾选sadd将元素添加到集合
                pl.asdd("selected_%d" % user.id, sku_id)
            else:
                # 未勾选srem将元素移除集合
                pl.srem("selected_%d" % user.id, sku_id)
                pl.execute()

        # 如果未获取到user则是未登录用户,进行cookie操作
        if not user:
            cart_str = request.COOKIES.get("carts")
            if cart_str:
                # 将cookie获取字符串转化为字典格式
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 判断当前要修改的sku_id是否在cart_dict字典中
                if sku_id in cart_dict:
                    # 直接用前端获取的值覆盖旧的值
                    cart_dict[sku_id] = {
                        "count": count,
                        "selected": selected
                    }

                # 将修改后的字典重新放入cookie购物车中存储起来,方便后面使用
                cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie("carts", cart_str)

        return response


    def delete(self, request):
        """删除购物车"""
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get("sku_id")
        # 创建响应对象
        response = Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

        try:
            # 如果能获取user,则是登录用户,就进行redis数据库操作
            user = request.user
        except Exception:
            user = None
        else:
            # 创建redis连接对象
            redis_conn = get_redis_connection("cart")
            # 创建管道
            pl = redis_conn.pipeline()
            # 把本次要删除的sku_id从hash表中移除
            pl.hdel("cart_%d" % user.id, sku_id)
            # 把本次要删除的selected从set集合中移除
            pl.srem("selected_%d" % user.id, sku_id)
            pl.execute()

        # 如果未获取到user则是未登录用户,进行cookie操作
        if not user:
            cart_str = request.COOKIES.get("carts")
            if cart_str:
                # 将cookie获取字符串转化为字典格式
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 判断当前要修改的sku_id是否在cart_dict字典中
                if sku_id in cart_dict:
                    # 把要删除的sku_id从cart_dict字典中移除
                    del cart_dict[sku_id]

                if len(cart_dict.keys()):
                    # 如果cart_dict中还有值,更新cookie购物车数据
                    cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                    # 设置cookie
                    response.set_cookie("carts", cart_str)
                else:
                    # 如果cookie购物车数据已经全部删除,就把cookie移除
                    response.delete_cookie("carts")

        return response


class CartSelectedView(APIView):
    """购物车全选"""

    def perform_authentication(self, request):
        """
        禁用认证/延后认证
        """
        pass

    def put(self, request):
        """全选购物车"""
        serializer = CartSelectedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data.get("selected")
        # 创建响应对象
        response = Response(serializer.data)

        try:
            # 如果能获取user,则是登录用户,就进行redis数据库操作
            user = request.user
        except Exception:
            user = None
        else:
            # 创建redis连接对象
            redis_conn = get_redis_connection("cart")
            # 获取redis中的hash字典
            cart_redis_dict = redis_conn.hgetall("cart_%d" % user.id)
            if selected:
                # *cart_redis_dict.keys():将字典中所有的键解包,统一进行勾选或取消勾选操作
                redis_conn.sadd("selected_%d" % user.id, *cart_redis_dict.keys())
            else:
                redis_conn.srem("selected_%d" % user.id, *cart_redis_dict.keys())

        # 如果未获取到user则是未登录用户,进行cookie操作
        if not user:
            cart_str = request.COOKIES.get("carts")
            if cart_str:
                # 将cookie获取字符串转化为字典格式
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 遍历cookie字典
                for sku_id in cart_dict:
                    # 取出sku_id对应的小字典
                    sku_id_dict = cart_dict[sku_id]
                    # 根据接收到前端selected状态,覆盖字典中selcted
                    sku_id_dict[selected] = selected

                # 更新cookie购物车数据
                cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 设置cookie
                response.set_cookie("carts", cart_str)

        return response




