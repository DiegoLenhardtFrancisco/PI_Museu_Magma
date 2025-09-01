from rest_framework.routers import DefaultRouter

from .api_views import ProductViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')

urlpatterns = router.urls
