from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import HealthCheckView

urlpatterns = [
    # Healthcheck endpoint
    path('healthcheck/', HealthCheckView.as_view(), name='healthcheck'),

    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App-specific API URLs will be added here
    path('', include('produtos.api_urls')),
    path('', include('vendas.api_urls')), 
    path('', include('usuarios.api_urls')),
]