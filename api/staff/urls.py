"""
Staff Role API URLs - Model-based organization
"""
from django.urls import path, include

app_name = 'staff'

urlpatterns = [
    path('vocabulary/', include('api.staff.vocabulary.urls')),
    path('books/', include('api.staff.books.urls')),
    path('analytics/', include('api.staff.analytics.urls')),
]