from decimal import Decimal
from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """
    Main form for product registration.
    """

    code = forms.CharField(disabled=True, required=False, label='Código')

    class Meta:
        fields = [
            'name', 'description', 'code', 'cost_price',
            'quantity', 'unit_of_measure', 'category', 'supplier',
            'expires_at', 'minimum_quantity', 'image',
            'stock_location', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expires_at': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_cost_price(self):
        """
        Ensures the cost price is positive.
        """
        cost_price = self.cleaned_data['cost_price']
        if cost_price <= 0:
            raise forms.ValidationError("The cost price must be greater than zero.")
        return cost_price

class EntradaProdutoForm(forms.ModelForm):
    """
    Form to register stock entry or update..
    """

    class Meta:
        model = Product
        fields = ['quantity', 'supplier', 'cost_price', 'is_active', 'stock_location', 'image']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'cost_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock_location': forms.TextInput(attrs={'maxlength': 255}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Please enter a positive quantity.")
        return Decimal(quantity)

    def clean_cost_price(self):
            price = self.cleaned_data['cost_price']
            if price <= 0:
                raise forms.ValidationError("The cost price must be greater than zero.")
            return Decimal(price)
