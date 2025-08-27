from rest_framework import serializers
from produtos.models import Product

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer to represent the Product model.
    """

    category_display = serializers.CharField(source='get_categoria_display', read_only=True)

    unit_of_measure_display = serializers.CharField(source='get_unidade_medida_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'code', 'cost_price',
            'profit_margin', 'sale_price', 'quantity',
            'unit_of_measure',
            'unit_of_measure_display', 
            'category',
            'category_display', 
            'supplier', 'is_active', 'image', 'stock_location',
            'created_at', 'updated_at', 'expires_at', 'minimum_quantity',
        ]
        read_only_fields = [
            'id', 'code', 'sale_price', 'created_at', 'updated_at',
        ]