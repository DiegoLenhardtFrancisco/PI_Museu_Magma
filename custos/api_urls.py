from rest_framework.routers import DefaultRouter

from .api_views import FixedCostEntryViewSet

router = DefaultRouter()
router.register(r'fixed-cost-entries', FixedCostEntryViewSet, basename='fixed-cost-entry')

urlpatterns = router.urls