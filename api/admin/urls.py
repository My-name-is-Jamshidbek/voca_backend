"""
Admin API URLs - Endpoints accessible to administrators only
"""
from django.urls import path, include
from .views import (
    AdminDashboardView,
    SystemAdministrationView,
    UserAdministrationView,
    TokenAdministrationView,
    SystemAnalyticsView,
)

app_name = 'admin'

urlpatterns = [
    # Admin dashboard
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    
    # System administration
    path('system/', SystemAdministrationView.as_view(), name='system-admin'),
    
    # User administration
    path('users/', UserAdministrationView.as_view(), name='user-admin'),
    
    # Token administration
    path('tokens/', TokenAdministrationView.as_view(), name='token-admin'),
    
    # System analytics
    path('analytics/', SystemAnalyticsView.as_view(), name='system-analytics'),
    
    # System management sections
    path('system/', include([
        path('maintenance/', SystemAdministrationView.as_view(), name='maintenance'),
        path('backup/', SystemAdministrationView.as_view(), name='backup'),
        path('cache/', SystemAdministrationView.as_view(), name='cache-management'),
        path('logs/', SystemAdministrationView.as_view(), name='log-management'),
    ])),
    
    # User management sections
    path('users/', include([
        path('roles/', UserAdministrationView.as_view(), name='role-management'),
        path('permissions/', UserAdministrationView.as_view(), name='permission-management'),
        path('bulk/', UserAdministrationView.as_view(), name='bulk-operations'),
    ])),
    
    # Token management sections
    path('tokens/', include([
        path('mobile/', TokenAdministrationView.as_view(), name='mobile-tokens'),
        path('api/', TokenAdministrationView.as_view(), name='api-tokens'),
        path('usage/', TokenAdministrationView.as_view(), name='token-usage'),
    ])),
    
    # Analytics sections
    path('analytics/', include([
        path('users/', SystemAnalyticsView.as_view(), name='user-analytics'),
        path('content/', SystemAnalyticsView.as_view(), name='content-analytics'),
        path('performance/', SystemAnalyticsView.as_view(), name='performance-analytics'),
        path('security/', SystemAnalyticsView.as_view(), name='security-analytics'),
    ])),
    
    # Legacy endpoints (for backward compatibility)
    path('accounts/legacy/', include('api.admin.accounts.urls')),
    path('vocabulary/legacy/', include('api.admin.vocabulary.urls')),
    path('languages/legacy/', include('api.admin.languages.urls')),
    path('books/legacy/', include('api.admin.books.urls')),
    path('analytics/legacy/', include('api.admin.analytics.urls')),
    path('tokens/legacy/', include('api.admin.tokens.urls')),
]