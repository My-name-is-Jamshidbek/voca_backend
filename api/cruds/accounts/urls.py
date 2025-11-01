"""
URL patterns for Accounts App CRUD APIs
"""
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserDeviceViewSet

# Create router for accounts app
accounts_router = DefaultRouter()
accounts_router.register(r'users', UserViewSet, basename='user')
accounts_router.register(r'user-devices', UserDeviceViewSet, basename='user-device')

# Export patterns
urlpatterns = accounts_router.urls