from rest_framework import serializers
from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """添加和修改购物车序列化器"""
    sku_id = serializers.IntegerField(label="sku_id", min_value=1)
    count = serializers.IntegerField(label="数量", min_value=1)
    selected = serializers.BooleanField(label="勾选", default=True)

    def validate_sku_id(self, value):
        """校验购物车id"""
        try:
            SKU.objects.get(id=value)
        except SKU.DoseNotExist:
            raise serializers.ValidationError("sku_id不存在")

        return value


class CartSKUSerializer(serializers.ModelSerializer):
    """查询购物车序列化器"""
    count = serializers.IntegerField(label="数量")
    selected = serializers.BooleanField(label="是否勾选")

    class Meta:
        model = SKU
        fields = ["id", "price", "name", "default_image_url", "selected", "count"]


class CartDeleteSerializer(serializers.Serializer):
    """删除购物车序列化器"""
    sku_id = serializers.IntegerField(label="sku_id", min_value=1)

    def validate_sku_id(self, value):

        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("商品不存在")

        return value


class CartSelectedSerializer(serializers.Serializer):
    """全选购物车序列化器"""
    selected = serializers.BooleanField(label="全部勾选")