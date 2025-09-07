from rest_framework import serializers

from produtos.models import Product, StockMovement


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer to represent the Product model.
    """

    category_display = serializers.CharField(
        source='get_categoria_display', read_only=True
    )

    unit_of_measure_display = serializers.CharField(
        source='get_unidade_medida_display', read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'code',
            'cost_price',
            'profit_margin',
            'sale_price',
            'quantity',
            'unit_of_measure',
            'unit_of_measure_display',
            'category',
            'category_display',
            'supplier',
            'is_active',
            'image',
            'stock_location',
            'created_at',
            'updated_at',
            'expires_at',
            'minimum_quantity',
            'created_by',
            'updated_by',
        ]
        read_only_fields = [
            'id',
            'code',
            'sale_price',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the StockMovement model.
    Provides detailed information for history logs.
    """

    product_name = serializers.CharField(source='product.name', read_only=True)
    user_name = serializers.CharField(
        source='user.username', read_only=True, default='Sistema'
    )
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id',
            'product',
            'product_name',
            'type',
            'type_display',
            'quantity',
            'cost_price',
            'supplier',
            'notes',
            'user',
            'user_name',
            'timestamp',
        ]
