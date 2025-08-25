from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('', RedirectView.as_view(url='usuarios/login/')),
    path('vendas/', include('vendas.urls', namespace='vendas')),
    path('produtos/', include('produtos.urls', namespace='produtos')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]