"""
Documentation URL Configuration
"""

from django.urls import path, include
from . import views

app_name = 'documentation'

urlpatterns = [
    # API Schema
    path('schema/', views.APISchemaView.as_view(), name='api_schema'),
    
    # Documentation
    path('', views.APIDocumentationView.as_view(), name='api_docs'),
    
    # Interactive documentation
    path('swagger/', views.SwaggerUIView.as_view(), name='swagger_ui'),
    path('redoc/', views.ReDocView.as_view(), name='redoc'),
]