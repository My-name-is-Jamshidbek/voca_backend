"""
Admin Vocabulary URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminCategoryViewSet, AdminWordViewSet

router = DefaultRouter()
router.register(r'categories', AdminCategoryViewSet, basename='admin-categories')
router.register(r'words', AdminWordViewSet, basename='admin-words')

urlpatterns = [
    path('', include(router.urls)),
]