from rest_framework import serializers
from produtos.models import Produto

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer to represent the Product model.
    """

    category_display = serializers.CharField(source='get_categoria_display', read_only=True)

    unit_of_measure_display = serializers.CharField(source='get_unidade_medida_display', read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id',
            'codigo',
            'nome',
            'descricao',
            'preco_custo',
            'margem_lucro',
            'preco_venda',
            'quantidade',
            'unidade_medida',
            'unit_of_measure_display', 
            'categoria',
            'category_display',
            'fornecedor',
            'ativo',
            'imagem',
            'endereco_estoque',
            'data_cadastro',
            'horario_atualizacao',
            'data_validade',
            'quantidade_minima',

        ]

        read_only_fields = [
            'id',
            'codigo',
            'preco_venda',
            'data_cadastro',
            'horario_atualizacao',
        ]