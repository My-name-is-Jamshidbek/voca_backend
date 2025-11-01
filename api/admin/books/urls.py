"""
Admin Books URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminBookViewSet, AdminChapterViewSet

router = DefaultRouter()
router.register(r'books', AdminBookViewSet, basename='admin-books')
router.register(r'chapters', AdminChapterViewSet, basename='admin-chapters')

urlpatterns = [
    path('', include(router.urls)),
]