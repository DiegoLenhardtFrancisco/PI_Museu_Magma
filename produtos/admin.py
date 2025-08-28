from django.contrib import admin

from .models import StockMovement, Product


@admin.register(Product)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Manages the administration interface for the Product model.

    Displays the main fields in lists, allows filtering and
    searching, and sets fields as read-only for security.
    """

    list_display = [
        'name', 'code', 'cost_price', 'profit_margin', 'sale_price',
        'quantity', 'unit_of_measure', 'category', 'supplier',
        'created_at', 'is_active', 'user'
    ]
    list_filter = ['unit_of_measure', 'is_active', 'category']
    search_fields = ['name', 'code', 'supplier']

    readonly_fields = [
        'name', 'description', 'code', 'cost_price', 'sale_price',
        'quantity', 'unit_of_measure', 'category', 'supplier',
        'created_at', 'expires_at', 'minimum_quantity',
        'is_active', 'image', 'updated_at', 'user', 'stock_location'
    ]

    fields = [
        'name', 'description', 'code', 'cost_price', 'profit_margin', 'sale_price',
        'quantity', 'unit_of_measure', 'category', 'supplier',
        'created_at', 'expires_at', 'minimum_quantity',
        'is_active', 'image', 'updated_at', 'user', 'stock_location'
    ]

    def save_model(self, request, obj, form, change):
        # A lógica de cálculo foi movida para o modelo, então apenas salve
        super().save_model(request, obj, form, change)


@admin.register(StockMovement)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    """
    Administra a interface de administração para o modelo MovimentacaoEstoque.

    Permite visualização detalhada das entradas e saídas de estoque.
    """

    list_display = [
        'produto',
        'data_movimentacao',
        'tipo',
        'quantidade',
        'preco_custo',
        'usuario',
    ]
    list_filter = ['tipo', 'data_movimentacao']
    search_fields = ['produto__nome', 'produto__codigo']
    date_hierarchy = 'data_movimentacao'

    readonly_fields = [
        'produto',
        'tipo',
        'quantidade',
        'preco_custo',
        'fornecedor',
        'observacao',
        'usuario',
        'data_movimentacao',
        'endereco_estoque',
    ]
