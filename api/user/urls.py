"""
User Role API URLs - Model-based organization
"""
from django.urls import path, include

app_name = 'user'

urlpatterns = [
    path('vocabulary/', include('api.user.vocabulary.urls')),
    path('profile/', include('api.user.profile.urls')),
    path('progress/', include('api.user.progress.urls')),
]