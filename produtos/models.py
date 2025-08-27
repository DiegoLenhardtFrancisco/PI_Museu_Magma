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
            self.sale_price = self.cost_price * (
                Decimal(1) + Decimal(self.profit_margin) / Decimal(100)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class MovimentacaoEstoque(models.Model):
    """
    Registra entradas, saídas e ajustes de estoque de um produto.
    """

    TIPO_CHOICES = [
        ('E', 'Entrada'),
        ('S', 'Saída'),
        ('A', 'Ajuste'),
    ]

    produto = models.ForeignKey(Product, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    fornecedor = models.CharField(max_length=100, null=True, blank=True)
    observacao = models.TextField(blank=True)
    endereco_estoque = models.CharField(max_length=255, null=True, blank=True)
    usuario = models.ForeignKey(
        'usuarios.CustomUser', on_delete=models.SET_NULL, null=True
    )
    data_movimentacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_movimentacao']
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.name} ({self.data_movimentacao:%d/%m/%Y %H:%M})"


# === SINAIS DE MODELO PARA RASTREAMENTO AUTOMÁTICO ===


@receiver(pre_save, sender=Product)
def capturar_valores_antes_alteracao(sender, instance, **kwargs):
    """
    Armazena os valores originais do produto antes de uma atualização, para comparação posterior.
    """
    if instance.pk:
        original = sender.objects.get(pk=instance.pk)
        instance._original_quantidade = original.quantidade
        instance._original_preco_custo = original.preco_custo
        instance._original_fornecedor = original.fornecedor
        instance._original_endereco = original.endereco_estoque


@receiver(post_save, sender=Product)
def create_stock_movement_after_update(sender, instance, created, **kwargs):
    """
    Automatically creates an inventory movement record after creating or changing a product.
    """
    if created:
        # Initial product registration
        MovimentacaoEstoque.objects.create(
            produto=instance,
            tipo='E',
            quantidade=instance.quantity,
            preco_custo=instance.cost_price,
            fornecedor=instance.supplier,
            observacao="Initial product creation",
            usuario=instance.user,
            endereco_estoque=instance.stock_location,
        )
    elif hasattr(instance, '_original_quantidade'):
        observacoes = []
        tipo = 'A'  # Padrão para Ajuste

        # Verifica se é um ajuste de inventário
        from_inventario = getattr(instance, '_from_inventario_adjustment', False)

        if from_inventario:
            old_qty = instance._original_quantidade
            new_qty = instance.quantidade
            observacoes.append(f"Ajuste de estoque: {old_qty} → {new_qty}")
            # Remove a flag após uso
            try:
                del instance._from_inventario_adjustment
            except AttributeError:
                pass
        else:
            # Lógica original para outros tipos de alteração
            if instance.quantidade != instance._original_quantidade:
                tipo = (
                    'E' if instance.quantidade > instance._original_quantidade else 'S'
                )
                quantidade_diff = abs(
                    instance.quantidade - instance._original_quantidade
                )
                observacoes.append(f"Quantidade alterada em {quantidade_diff}")

            if instance.preco_custo != instance._original_preco_custo:
                observacoes.append(f"Preço alterado para R$ {instance.preco_custo}")

            if instance.fornecedor != instance._original_fornecedor:
                observacoes.append(f"Fornecedor alterado para {instance.fornecedor}")

            if instance.endereco_estoque != instance._original_endereco:
                observacoes.append(
                    f"Endereço alterado para {instance.endereco_estoque}"
                )

        if observacoes:
            MovimentacaoEstoque.objects.create(
                produto=instance,
                tipo=tipo,
                quantidade=instance.quantidade,
                preco_custo=instance.preco_custo,
                fornecedor=instance.fornecedor,
                observacao=". ".join(observacoes),
                usuario=instance.usuario,
                endereco_estoque=instance.endereco_estoque,
            )
