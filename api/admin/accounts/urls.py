"""
Admin Accounts URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet, AdminPermissionViewSet

router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'permissions', AdminPermissionViewSet, basename='admin-permissions')

urlpatterns = [
    path('', include(router.urls)),
]