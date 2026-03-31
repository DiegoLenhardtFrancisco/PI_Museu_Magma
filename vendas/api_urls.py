from rest_framework.routers import DefaultRouter

from .api_views import CustomerViewSet, SaleItemViewSet, SaleViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'sale-items', SaleItemViewSet, basename='saleitem')

urlpatterns = router.urls