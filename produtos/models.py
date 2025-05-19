from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class Categoria(models.Model):
    """
    Representa categorias fixas para classificação dos produtos.
    """
    CATEGORIA_CHOICES = [
        ('FOSSIL', 'Fóssil'),
        ('ARTESANATO', 'Artesanato'),
        ('MINERAL', 'Mineral'),
        ('OUTRO', 'Outro'),
    ]

    nome = models.CharField(max_length=100, choices=CATEGORIA_CHOICES, unique=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """
    Modelo principal para cadastro de produtos no sistema de estoque.
    """
    UNIDADE_CHOICES = [
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('LT', 'Litro'),
        ('MT', 'Metro'),
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    codigo = models.CharField(max_length=50, unique=True)

    preco_custo = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    preco_venda = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False
    )

    quantidade = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    unidade_medida = models.CharField(max_length=2, choices=UNIDADE_CHOICES)

    categoria = models.CharField(
        max_length=50, choices=Categoria.CATEGORIA_CHOICES, null=True
    )
    fornecedor = models.CharField(max_length=100, null=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_validade = models.DateField(null=True, blank=True)
    quantidade_minima = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    horario_atualizacao = models.DateTimeField(auto_now=True)
    endereco_estoque = models.CharField(max_length=255, null=True, blank=True)

    usuario = models.ForeignKey(
        'usuarios.CustomUser', on_delete=models.SET_NULL, null=True
    )

    def save(self, *args, **kwargs):
        """
        Recalcula o preço de venda antes de salvar, baseado no custo e margem.
        """
        if self.preco_custo is not None and self.margem_lucro is not None:
            self.preco_venda = self.preco_custo * (Decimal(1) + Decimal(self.margem_lucro) / Decimal(100))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"


class MovimentacaoEstoque(models.Model):
    """
    Registra entradas, saídas e ajustes de estoque de um produto.
    """
    TIPO_CHOICES = [
        ('E', 'Entrada'),
        ('S', 'Saída'),
        ('A', 'Ajuste'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)

    fornecedor = models.CharField(max_length=100, null=True, blank=True)
    observacao = models.TextField(blank=True)
    endereco_estoque = models.CharField(max_length=255, null=True, blank=True)

    usuario = models.ForeignKey('usuarios.CustomUser', on_delete=models.SET_NULL, null=True)
    data_movimentacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_movimentacao']
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome} ({self.data_movimentacao:%d/%m/%Y %H:%M})"


# === SINAIS DE MODELO PARA RASTREAMENTO AUTOMÁTICO ===

@receiver(pre_save, sender=Produto)
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


@receiver(post_save, sender=Produto)
def criar_movimentacao_apos_alteracao(sender, instance, created, **kwargs):
    """
    Cria automaticamente um registro de movimentação de estoque após criação ou alteração de um produto.
    """
    if created:
        # Cadastro inicial do produto
        MovimentacaoEstoque.objects.create(
            produto=instance,
            tipo='E',
            quantidade=instance.quantidade,
            preco_custo=instance.preco_custo,
            fornecedor=instance.fornecedor,
            observacao="Cadastro inicial do produto",
            usuario=instance.usuario,
            endereco_estoque=instance.endereco_estoque
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
                tipo = 'E' if instance.quantidade > instance._original_quantidade else 'S'
                quantidade_diff = abs(instance.quantidade - instance._original_quantidade)
                observacoes.append(f"Quantidade alterada em {quantidade_diff}")

            if instance.preco_custo != instance._original_preco_custo:
                observacoes.append(f"Preço alterado para R$ {instance.preco_custo}")

            if instance.fornecedor != instance._original_fornecedor:
                observacoes.append(f"Fornecedor alterado para {instance.fornecedor}")

            if instance.endereco_estoque != instance._original_endereco:
                observacoes.append(f"Endereço alterado para {instance.endereco_estoque}")

        if observacoes:
            MovimentacaoEstoque.objects.create(
                produto=instance,
                tipo=tipo,
                quantidade=instance.quantidade,
                preco_custo=instance.preco_custo,
                fornecedor=instance.fornecedor,
                observacao=". ".join(observacoes),
                usuario=instance.usuario,
                endereco_estoque=instance.endereco_estoque
            )