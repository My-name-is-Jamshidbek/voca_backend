"""
Base API URLs - Public and Authentication APIs
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .auth import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    ChangePasswordView
)
from . import HealthCheckView, APIRootView

app_name = 'base'

urlpatterns = [
    # Health and root
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='base:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='base:schema'), name='redoc'),
]