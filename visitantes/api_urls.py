from rest_framework.routers import DefaultRouter

from .api_views import VisitorViewSet, VisitViewSet

router = DefaultRouter()
router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'visits', VisitViewSet, basename='visit')

urlpatterns = router.urls