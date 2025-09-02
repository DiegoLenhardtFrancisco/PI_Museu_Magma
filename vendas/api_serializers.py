from rest_framework import serializers
from vendas.models import Sale, SaleItem

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SaleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for SaleItem, used for read-only nested representation.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price']

class SaleSerializer(serializers.ModelSerializer):
    """
    Serializer for Sale, with nested items for detailed view.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True, allow_null=True)
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'customer', 'customer_name', 'user', 'user_name',
            'sale_date', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'discount', 'total_amount',
            'notes', 'total_cost', 'items'
        ]

