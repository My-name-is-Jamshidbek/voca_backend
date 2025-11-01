"""
URL Configuration for voca_project

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from api.base import APIRootView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/v1/', APIRootView.as_view(), name='api-root'),
    
    # Base APIs (Public and Authentication)
    path('api/v1/base/', include('api.base.urls')),
    
    # Role-based APIs
    path('api/v1/user/', include('api.user.urls')),
    path('api/v1/staff/', include('api.staff.urls')),
    path('api/v1/admin/', include('api.admin.urls')),
    
    # CRUD APIs (Token-based access)
    path('api/v1/cruds/', include('api.cruds.urls')),
]