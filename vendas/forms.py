from django import forms
from .models import Cliente, Venda, ItemVenda
from produtos.models import Produto
from django.forms import inlineformset_factory
from decimal import Decimal

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'documento', 'tipo', 'email', 'telefone', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['cliente', 'forma_pagamento', 'desconto', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'desconto': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ItemVendaForm(forms.ModelForm):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        widget=forms.Select(attrs={'class': 'produto-select'}),
        label=''
    )
    
    quantidade = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        label=''
    )

    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade']
        exclude = ('preco_unitario',)

ItemVendaFormSet = inlineformset_factory(
    Venda,
    ItemVenda,
    form=ItemVendaForm,
    extra=5,
    can_delete=False
)