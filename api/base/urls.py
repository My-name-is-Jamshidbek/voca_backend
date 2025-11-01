"""
Base API URLs - Public and Authentication APIs
Modular structure with separated concerns
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .common.views import APIRootView

app_name = 'base'

urlpatterns = [
    # Root endpoint
    path('', APIRootView.as_view(), name='api-root'),
    
    # Authentication module
    path('auth/', include('api.base.authentication.urls')),
    
    # Health monitoring module
    path('health/', include('api.base.health.urls')),
    
    # Documentation module
    path('docs/', include('api.base.documentation.urls')),
    
    # JWT token endpoints (kept for backward compatibility)
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token-verify'),
]