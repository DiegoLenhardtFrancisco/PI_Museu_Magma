from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.base_produto, name='base_produto'),
    path('novo/', views.criar_produto, name='criar_produto'),
    path('entrada/', views.entrada_produto, name='entrada_produto'),  # Nova URL para entrada de material
    path('historico/', views.historico_individual, name='historico_individual'),  # Relatório de movimentações
    path('inventario/', views.relatorio_inventario, name='relatorio_inventario'),  # Relatório de inventário
]
