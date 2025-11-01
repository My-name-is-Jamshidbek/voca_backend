"""
Authentication module URLs
JWT authentication, registration, password management, and profile management
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    LogoutView,
    ProfileView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    TokenValidateView,
    UserDeviceView,
)

app_name = 'authentication'

urlpatterns = [
    # JWT Token endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('validate/', TokenValidateView.as_view(), name='token-validate'),
    path('verify/', TokenVerifyView.as_view(), name='token-verify'),
    
    # User registration
    path('register/', RegisterView.as_view(), name='register'),
    
    # Password management
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Profile management
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Device management
    path('devices/', UserDeviceView.as_view(), name='user-devices'),
    path('devices/<str:device_id>/', UserDeviceView.as_view(), name='user-device-detail'),
]