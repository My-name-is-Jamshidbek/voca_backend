"""
URL patterns for Tokens App CRUD APIs
"""
from rest_framework.routers import DefaultRouter
from .views import MobileAppTokenViewSet, APIClientTokenViewSet

# Create router for tokens app
tokens_router = DefaultRouter()
tokens_router.register(r'mobile-tokens', MobileAppTokenViewSet, basename='mobile-token')
tokens_router.register(r'api-tokens', APIClientTokenViewSet, basename='api-token')

# Export patterns
urlpatterns = tokens_router.urls