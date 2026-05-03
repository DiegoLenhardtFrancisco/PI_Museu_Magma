from django.urls import path

from .api_views import DashboardView

urlpatterns = [
    path(
        "analytics/dashboard/",
        DashboardView.as_view(),
        name="analytics-dashboard",
    ),
]