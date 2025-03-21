from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Painel de administração do Django
    path('pedido/', include('pedido.urls')),  # URLs da app pedido
    path('produto/', include('produto.urls')),  # URLs da app produto
    path('usuario/', include('usuario.urls')),  # URLs da app usuario
    path('', include('produto.urls')),  # Página inicial (index) da app produto
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)