"""
analytics/api_urls.py

URL configuration for the analytics app.
"""

from django.urls import path

from .api_views import DashboardView

urlpatterns = [
    path(
        'analytics/dashboard/',
        DashboardView.as_view(),
        name='analytics-dashboard'
    ),
]