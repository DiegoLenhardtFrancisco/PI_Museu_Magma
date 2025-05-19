from django.contrib import admin
from .models import Produto, MovimentacaoEstoque


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Administra a interface de administração para o modelo Produto.

    Exibe os principais campos em listagens, permite filtragem e 
    busca, e define campos como somente leitura para segurança.
    """
    list_display = [
        'nome', 'codigo', 'preco_custo', 'margem_lucro', 'preco_venda',
        'quantidade', 'unidade_medida', 'categoria', 'fornecedor',
        'data_cadastro', 'ativo', 'usuario'
    ]
    list_filter = ['unidade_medida', 'ativo', 'categoria']
    search_fields = ['nome', 'codigo', 'fornecedor']
    
    readonly_fields = [
        'nome', 'descricao', 'codigo', 'preco_custo', 'preco_venda',
        'quantidade', 'unidade_medida', 'categoria', 'fornecedor',
        'data_cadastro', 'data_validade', 'quantidade_minima',
        'ativo', 'imagem', 'horario_atualizacao', 'usuario'
    ]

    fields = [
        'nome', 'descricao', 'codigo', 'preco_custo', 'margem_lucro', 'preco_venda',
        'quantidade', 'unidade_medida', 'categoria', 'fornecedor',
        'data_cadastro', 'data_validade', 'quantidade_minima',
        'ativo', 'imagem', 'horario_atualizacao', 'usuario'
    ]

    def save_model(self, request, obj, form, change):
        # A lógica de cálculo foi movida para o modelo, então apenas salve
        super().save_model(request, obj, form, change)


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    """
    Administra a interface de administração para o modelo MovimentacaoEstoque.

    Permite visualização detalhada das entradas e saídas de estoque.
    """
    list_display = [
        'produto', 'data_movimentacao', 'tipo', 
        'quantidade', 'preco_custo', 'usuario'
    ]
    list_filter = ['tipo', 'data_movimentacao']
    search_fields = ['produto__nome', 'produto__codigo']
    date_hierarchy = 'data_movimentacao'

    readonly_fields = [
        'produto', 'tipo', 'quantidade', 'preco_custo',
        'fornecedor', 'observacao', 'usuario', 'data_movimentacao',
        'endereco_estoque'
    ]
