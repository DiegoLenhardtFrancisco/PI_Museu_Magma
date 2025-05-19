from django.db import models
from django.core.validators import MinValueValidator
from produtos.models import Produto
from usuarios.models import CustomUser
from decimal import Decimal
from django.db import transaction

class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]
    
    nome = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=2, choices=TIPO_CLIENTE_CHOICES)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nome} ({self.documento})"

class Venda(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberta'),
        ('F', 'Finalizada'),
        ('C', 'Cancelada'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('DI', 'Dinheiro'),
        ('CD', 'Cartão Débito'),
        ('CC', 'Cartão Crédito'),
        ('PX', 'Pix'),
        ('BO', 'Boleto'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    data_venda = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(max_length=2, choices=FORMA_PAGAMENTO_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-data_venda']
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'

    def calcular_total(self):
        total = sum(item.subtotal() for item in self.itens.all())
        return total - self.desconto

    def atualizar_estoque(self, operacao='remover'):
        with transaction.atomic():
            for item in self.itens.all():
                produto = item.produto
                if operacao == 'remover':
                    produto.quantidade -= item.quantidade
                else:
                    produto.quantidade += item.quantidade
                produto.save()

    def __str__(self):
        return f"Venda #{self.id} - {self.data_venda.strftime('%d/%m/%Y')}"

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} @ {self.preco_unitario}"