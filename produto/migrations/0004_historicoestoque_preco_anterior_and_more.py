# Generated by Django 5.0.4 on 2025-03-19 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0003_historicoestoque'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicoestoque',
            name='preco_anterior',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicoestoque',
            name='preco_novo',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='historicoestoque',
            name='valor_final_estoque',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicoestoque',
            name='valor_inicial_estoque',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='historicoestoque',
            name='quantidade',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='historicoestoque',
            name='tipo',
            field=models.CharField(choices=[('entrada', 'Entrada'), ('saida', 'Saída'), ('alteracao_preco', 'Alteração de Preço')], max_length=20),
        ),
    ]
