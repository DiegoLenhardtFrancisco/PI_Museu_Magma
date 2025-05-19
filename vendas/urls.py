from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    path('', views.venda_rapida, name='venda_rapida'),
    ]