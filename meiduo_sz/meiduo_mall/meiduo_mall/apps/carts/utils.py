"""
购物车cookie合并到redis
购物车合并 需求: 以cookie为准备  用cookie去合并到redis
如果cookie中的某个sku_id在redis中没有  新增到redis
如果cookie中的某个sku_id在redis中存在  就用cookie的这个sku_id数据覆盖redis的重复sku_id数据

如果cookie和redis中有相同的sku_id, 并且在cookie或redis有一方是勾选的那么这个商品最终在redis中就是勾选的
如果cookie中独立存在的sku_id,是未勾选合并到redis之后还是未勾选
"""
import pickle, base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    # 以cookie合并到redis
    # 获取cookie购物车数据
    cart_str = request.COOKIES.get("carts")

    # 判断如果cookie没有数据,代码不在往下执行
    if not cart_str:
        return

    # 将cart_str转为cart_dict
    cookie_cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    # 定义中间合并字典
    # new_redis_cart_dict = {}

    # 创建redis连接对象
    redis_conn = get_redis_connection("cart")

    # 遍历cookie字典 将sku_id和count直接加入到redis和hash字典,如果cookie中的sku_id在hash中已存在,会以cookie去覆盖hash
    for sku_id in cookie_cart_dict:
        redis_conn.hset("cart_%d" % user.id, sku_id, cookie_cart_dict[sku_id]["count"])
        # 判断cookie购物车数据中是否勾选
        if cookie_cart_dict[sku_id]["selected"]:
            redis_conn.sadd("selected_%d" % user.id, sku_id)

    # 清空cookie购物车数据
    response.delete_cookie("carts")

