"""
Admin Role API URLs - Model-based organization
"""
from django.urls import path, include

app_name = 'admin'

urlpatterns = [
    path('accounts/', include('api.admin.accounts.urls')),
    path('vocabulary/', include('api.admin.vocabulary.urls')),
    path('languages/', include('api.admin.languages.urls')),
    path('books/', include('api.admin.books.urls')),
    path('analytics/', include('api.admin.analytics.urls')),
    path('tokens/', include('api.admin.tokens.urls')),
]