from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('', RedirectView.as_view(url='usuarios/login/')),
    path('vendas/', include('vendas.urls', namespace='vendas')),  
    path('produtos/', include('produtos.urls', namespace='produtos')),
]