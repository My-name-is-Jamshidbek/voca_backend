from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminMobileAppTokenViewSet, AdminAPIClientTokenViewSet, AdminTokenModelPermissionViewSet

router = DefaultRouter()
router.register(r'mobile-tokens', AdminMobileAppTokenViewSet, basename='admin-mobile-tokens')
router.register(r'api-tokens', AdminAPIClientTokenViewSet, basename='admin-api-tokens')
router.register(r'permissions', AdminTokenModelPermissionViewSet, basename='admin-token-permissions')

urlpatterns = [
    path('', include(router.urls)),
]