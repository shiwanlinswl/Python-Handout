from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter

from .models import SKU
from .serializers import SKUSerializer

from drf_haystack.viewsets import HaystackViewSet
from .serializers import SKUIndexSerializer
# Create your views here.


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer


class SKUListView(ListAPIView):
    """商品列表界面"""

    # 指定序列化器
    serializer_class = SKUSerializer

    # 指定过滤后端为排序
    filter_backends = [OrderingFilter]
    # 指定排序字段
    ordering_fields = ['create_time', 'price', 'sales']

    # 指定查询集
    # queryset = SKU.objects.filter(is_launched=True, category_id=category_id)

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')  # 获取url路径中的正则组别名提取出来的参数
        return SKU.objects.filter(is_launched=True, category_id=category_id)



