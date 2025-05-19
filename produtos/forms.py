from decimal import Decimal
from django import forms
from .models import Produto


class ProdutoForm(forms.ModelForm):
    """
    Formulário principal para cadastro de produtos.
    """
    codigo = forms.CharField(disabled=True, required=False, label='Código')

    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'codigo', 'preco_custo',
            'quantidade', 'unidade_medida', 'categoria', 'fornecedor',
            'data_validade', 'quantidade_minima', 'imagem',
            'endereco_estoque', 'ativo',
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'data_validade': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_preco_custo(self):
        """
        Garante que o preço de custo seja positivo.
        """
        preco = self.cleaned_data['preco_custo']
        if preco <= 0:
            raise forms.ValidationError("O preço de custo deve ser maior que zero.")
        return preco


class EntradaProdutoForm(forms.ModelForm):
    """
    Formulário para registrar entrada ou atualização de estoque.
    """
    class Meta:
        model = Produto
        fields = ['quantidade', 'fornecedor', 'preco_custo', 'ativo', 'endereco_estoque', 'imagem']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'preco_custo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'endereco_estoque': forms.TextInput(attrs={'maxlength': 255}),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        if quantidade <= 0:
            raise forms.ValidationError("Informe uma quantidade positiva.")
        return Decimal(quantidade)

    def clean_preco_custo(self):
        preco = self.cleaned_data['preco_custo']
        if preco <= 0:
            raise forms.ValidationError("O preço de custo deve ser maior que zero.")
        return Decimal(preco)
