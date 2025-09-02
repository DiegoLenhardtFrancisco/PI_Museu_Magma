from django.contrib import admin

from .models import Customer, Sale, SaleItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'document', 'customer_type', 'phone', 'email']
    search_fields = ['name', 'document']
    list_filter = ['customer_type']
    ordering = ['name']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale_date', 'customer', 'total_amount', 'payment_method', 'status']
    list_filter = ['status', 'payment_method']
    search_fields = ['customer__name', 'id']
    readonly_fields = ['total_amount', 'sale_date']
    date_hierarchy = 'sale_date'

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'unit_price']
    search_fields = ['product__name', 'sale__id']
    raw_id_fields = ['product']
