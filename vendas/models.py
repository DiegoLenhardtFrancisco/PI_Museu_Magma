from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models, transaction

from core.models import AuditModel
from produtos.models import Product
from usuarios.models import CustomUser


class Customer(AuditModel, models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    name = models.CharField(max_length=100)
    document = models.CharField(max_length=20, unique=True)
    customer_type = models.CharField(max_length=2, choices=CUSTOMER_TYPE_CHOICES)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.name} ({self.document})"


class Sale(AuditModel, models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Aberta'),
        ('COMPLETED', 'Finalizada'),
        ('CANCELLED', 'Cancelada'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Dinheiro'),
        ('DEBIT', 'Cartão Débito'),
        ('CREDIT', 'Cartão Crédito'),
        ('PIX', 'Pix'),
        ('TICKET', 'Boleto'),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    sale_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    # sale_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'

    def calcular_total(self):
        total = sum(item.subtotal() for item in self.itens.all())
        return total - self.desconto

    def update_stock(self, operacao='remover'):
        with transaction.atomic():
            for item in self.itens.all():
                product = item.product
                if operacao == 'remover':
                    product.quantidade -= item.quantidade
                else:
                    product.quantidade += item.quantidade
                product.save()

    def __str__(self):
        return f"Sale #{self.id} - {self.sale_date.strftime('%d/%m/%Y')}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'

    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ {self.unit_price}"
