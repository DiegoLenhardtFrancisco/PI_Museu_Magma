from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models import AuditModel


class FixedCostEntry(AuditModel, models.Model):
    """
    Represents a single fixed cost entry for the museum.

    Each entry belongs to a category (e.g. Rent, Water, Electricity),
    has a due date, a monetary value and a payment status.
    Overdue pending entries can be identified by comparing due_date with today.
    """

    class Category(models.TextChoices):
        RENT = 'RENT', 'Aluguel'
        WATER = 'WATER', 'Água'
        ELECTRICITY = 'ELECTRICITY', 'Luz'
        INTERNET = 'INTERNET', 'Internet'
        SALARIES = 'SALARIES', 'Salários de Funcionários'
        TAXES = 'TAXES', 'Taxas'
        OPERATIONAL = 'OPERATIONAL', 'Despesas Operacionais'
        MAINTENANCE = 'MAINTENANCE', 'Manutenção'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        PAID = 'PAID', 'Pago'

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )
    description = models.CharField(max_length=255, blank=True)
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    due_date = models.DateField()
    paid_at = models.DateField(
        null=True,
        blank=True,
        help_text='Date the entry was actually paid. Set automatically on status change.',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        ordering = ['due_date']
        verbose_name = 'Custo Fixo'
        verbose_name_plural = 'Custos Fixos'

    def __str__(self):
        return f"{self.get_category_display()} — R$ {self.value} ({self.due_date})"