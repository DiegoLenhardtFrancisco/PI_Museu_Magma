from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Category(models.Model):
    """
    Represents fixed categories for product classification.
    """

    CATEGORY_CHOICES = [
        ('FOSSIL', 'Fóssil'),
        ('ARTISANSHIP', 'Artesanato'),
        ('MINERAL', 'Mineral'),
        ('OTHER', 'Outro'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Product(models.Model):
    """
    Main template for registering products in the inventory system.
    """

    UNIT_CHOICES = [
        ('UNIT', 'Unidade'),
        ('KG', 'Quilograma'),
        ('LT', 'Litro'),
        ('MT', 'Metro'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=50, unique=True)
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    unit_of_measure = models.CharField(max_length=10, choices=UNIT_CHOICES)
    category = models.CharField(
        max_length=50, choices=Category.CATEGORY_CHOICES, null=True
    )
    supplier = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField(null=True, blank=True)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock_location = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey('usuarios.CustomUser', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        """
        Recalculates the selling price before saving, based on cost and margin.
        """
        if self.cost_price is not None and self.profit_margin is not None:
            cost = Decimal(self.cost_price)
            profit_margin_percent = Decimal(self.profit_margin) / Decimal(100)
            self.sale_price = cost * (Decimal(1) + profit_margin_percent)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class StockMovement(models.Model):
    """
    Logs entries, exits, and adjustments for a product's stock.
    """

    MOVEMENT_TYPE_CHOICES = [
        ('ENTRY', 'Entrada'),
        ('SALE', 'Saída (Venda)'),
        ('ADJUST', 'Ajuste'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    type = models.CharField(max_length=6, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(blank=True)
    stock_location = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(
        'usuarios.CustomUser', on_delete=models.SET_NULL, null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'

    def __str__(self):
        return f"{self.get_type_display()} - {self.product.name} ({self.timestamp:%d/%m/%Y %H:%M})"


# === MODEL SIGNALS FOR AUTOMATIC TRACKING (FULLY TRANSLATED) ===

@receiver(pre_save, sender=Product)
def capture_values_before_update(sender, instance, **kwargs):
    """
    Stores the original values of the product before an update, for later comparison.
    """
    if instance.pk:
        original = sender.objects.get(pk=instance.pk)
        instance._original_quantity = original.quantity
        instance._original_cost_price = original.cost_price
        instance._original_supplier = original.supplier
        instance._original_stock_location = original.stock_location


@receiver(post_save, sender=Product)
def create_stock_movement_after_update(sender, instance, created, **kwargs):
    """
    Automatically creates an inventory movement record after creating or changing a product.
    """
    if created:
        StockMovement.objects.create(
            product=instance,
            type='E',
            quantity=instance.quantity,
            cost_price=instance.cost_price,
            supplier=instance.supplier,
            notes="Initial product creation",
            user=instance.user,
            stock_location=instance.stock_location,
        )
    elif hasattr(instance, '_original_quantity'):
        notes = []
        movement_type = 'ADJUST'

        if instance.quantity != instance._original_quantity:
            movement_type = 'ENTRY' if instance.quantity > instance._original_quantity else 'SALE'
            quantity_diff = abs(instance.quantity - instance._original_quantity)
            notes.append(f"Quantidade alterada em {quantity_diff}")

        if instance.cost_price != instance._original_cost_price:
            notes.append(f"Preço de custo alterado para R$ {instance.cost_price}")

        if instance.supplier != instance._original_supplier:
            notes.append(f"Fornecedor alterado para {instance.supplier}")

        if instance.stock_location != instance._original_stock_location:
            notes.append(f"Localização alterada para {instance.stock_location}")

        if notes:
            StockMovement.objects.create(
                product=instance,
                type=movement_type,
                quantity=instance.quantity, # Salva a quantidade final do produto
                cost_price=instance.cost_price,
                supplier=instance.supplier,
                notes=". ".join(notes), # Nota para o usuário
                user=instance.user,
                stock_location=instance.stock_location,
            )
