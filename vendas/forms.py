from decimal import Decimal

from django import forms
from django.forms import inlineformset_factory

from produtos.models import Product

from .models import Customer, Sale, SaleItem


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'document', 'customer_type', 'email', 'phone', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'payment_method', 'discount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'discount': forms.NumberInput(attrs={'step': '0.01'}),
        }

class SaleItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'produto-select'}),
        label=''
    )
    quantity = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'step': '0.01'}), label=''
    )
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']
        exclude = ('unit_price',)

ItemSaleFormSet = inlineformset_factory(
    Sale, SaleItem, form=SaleItemForm, extra=5, can_delete=False
)