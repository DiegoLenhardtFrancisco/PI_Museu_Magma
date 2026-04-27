from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from usuarios.api_views import CustomTokenObtainPairView

from .views import HealthCheckView

urlpatterns = [
    # Healthcheck endpoint
    path('healthcheck/', HealthCheckView.as_view(), name='healthcheck'),
    # Authentication endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # App-specific API URLs
    path('', include('produtos.api_urls')),
    path('', include('vendas.api_urls')),
    path('', include('usuarios.api_urls')),
    path('', include('visitantes.api_urls')),
    path('', include('custos.api_urls')),
]
