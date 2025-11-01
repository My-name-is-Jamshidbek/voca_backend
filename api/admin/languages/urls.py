"""
Admin Languages URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminLanguageViewSet

router = DefaultRouter()
router.register(r'', AdminLanguageViewSet, basename='admin-languages')

urlpatterns = [
    path('', include(router.urls)),
]