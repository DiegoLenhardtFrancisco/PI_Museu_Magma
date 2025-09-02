from django.db import transaction
from rest_framework import serializers
from .models import Customer, Sale, SaleItem
from produtos.models import Product

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SaleItemWriteSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = SaleItem
        fields = ['product_id', 'quantity']

class SaleItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price']

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
    items = SaleItemReadSerializer(many=True, read_only=True)
    items_to_create = SaleItemWriteSerializer(many=True, write_only=True)

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
            'notes', 'total_cost', 'items', 'items_to_create'
        ]
        read_only_fields = ['total_amount', 'total_cost', 'user', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items_to_create', [])
        
        with transaction.atomic():
            sale = Sale.objects.create(user=self.context['request'].user, **validated_data)

            total_cost = 0
            total_amount = 0

            for item_data in items_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = item_data['quantity']

                if product.quantity < quantity:
                    raise serializers.ValidationError(f"Estoque insuficiente para o produto: {product.name}")
                
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=product.sale_price
                )

                product.quantity -= quantity
                product.save()

                total_cost += product.cost_price * quantity
                total_amount += product.sale_price * quantity

            sale.total_cost = total_cost
            sale.total_amount = total_amount - sale.discount
            sale.status = 'COMPLETED'
            sale.save()

        return sale
