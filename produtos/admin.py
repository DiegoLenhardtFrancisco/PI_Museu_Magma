from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'created_by']


@admin.register(Product)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Manages the administration interface for the Product model.

    Displays the main fields in lists, allows filtering and
    searching, and sets fields as read-only for security.
    """

    list_display = [
        'name',
        'code',
        'cost_price',
        'profit_margin',
        'sale_price',
        'quantity',
        'unit_of_measure',
        'category',
        'supplier',
        'created_at',
        'is_active',
        'created_by',
    ]
    list_filter = ['unit_of_measure', 'is_active', 'category']
    search_fields = ['name', 'code', 'supplier']

    readonly_fields = [
        'updated_by',
        'name',
        'description',
        'code',
        'cost_price',
        'sale_price',
        'quantity',
        'unit_of_measure',
        'category',
        'supplier',
        'created_at',
        'expires_at',
        'minimum_quantity',
        'is_active',
        'image',
        'updated_at',
        'created_by',
        'stock_location',
    ]

    fields = [
        'name',
        'description',
        'code',
        'cost_price',
        'profit_margin',
        'sale_price',
        'quantity',
        'unit_of_measure',
        'category',
        'supplier',
        'created_at',
        'expires_at',
        'minimum_quantity',
        'is_active',
        'image',
        'updated_at',
        'stock_location',
    ]

    def save_model(self, request, obj, form, change):
        # A lógica de cálculo foi movida para o modelo, então apenas salve
        super().save_model(request, obj, form, change)


class StockMovementAdmin(admin.ModelAdmin):
    """
    Admin interface for the StockMovement model.
    """

    list_display = [
        'product',
        'timestamp',
        'type',
        'quantity',
        'cost_price',
        'user',
    ]
    list_filter = ['type', 'timestamp']
    search_fields = ['product__name', 'product__code']
    date_hierarchy = 'timestamp'

    readonly_fields = [
        'product',
        'type',
        'quantity',
        'cost_price',
        'supplier',
        'notes',
        'user',
        'timestamp',
        'stock_location',
    ]
