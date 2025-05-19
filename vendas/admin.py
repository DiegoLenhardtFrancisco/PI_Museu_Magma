from django.contrib import admin
from .models import Cliente, Venda, ItemVenda

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'documento', 'tipo', 'telefone', 'email']
    search_fields = ['nome', 'documento']
    list_filter = ['tipo']
    ordering = ['nome']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'data_venda', 'cliente', 'total', 'forma_pagamento', 'status']
    list_filter = ['status', 'forma_pagamento']
    search_fields = ['cliente__nome', 'id']
    readonly_fields = ['total', 'data_venda']
    date_hierarchy = 'data_venda'

@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ['venda', 'produto', 'quantidade', 'preco_unitario']
    search_fields = ['produto__nome', 'venda__id']
    raw_id_fields = ['produto']