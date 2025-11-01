from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MobileAppTokenViewSet, APIClientTokenViewSet, 
    TokenUsageLogViewSet, TokenValidationView, TokenStatsView
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'mobile-tokens', MobileAppTokenViewSet, basename='mobile-tokens')
router.register(r'api-tokens', APIClientTokenViewSet, basename='api-tokens')
router.register(r'usage-logs', TokenUsageLogViewSet, basename='usage-logs')

app_name = 'tokens'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('validate/', TokenValidationView.as_view(), name='token-validate'),
    path('stats/', TokenStatsView.as_view(), name='token-stats'),
]