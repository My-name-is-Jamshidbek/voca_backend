"""
Staff API URLs - Endpoints accessible to staff members
"""
from django.urls import path, include
from .views import (
    StaffDashboardView,
    UserManagementView,
    ContentManagementView,
    LearningAnalyticsView,
    SystemHealthView,
)

app_name = 'staff'

urlpatterns = [
    # Staff dashboard
    path('dashboard/', StaffDashboardView.as_view(), name='dashboard'),
    
    # User management
    path('users/', UserManagementView.as_view(), name='user-list'),
    path('users/<str:user_id>/', UserManagementView.as_view(), name='user-detail'),
    
    # Content management
    path('content/', ContentManagementView.as_view(), name='content-overview'),
    
    # Learning analytics
    path('analytics/', LearningAnalyticsView.as_view(), name='learning-analytics'),
    
    # System health monitoring
    path('health/', SystemHealthView.as_view(), name='system-health'),
    
    # Content management sections
    path('content/', include([
        path('words/', ContentManagementView.as_view(), name='word-management'),
        path('collections/', ContentManagementView.as_view(), name='collection-management'),
        path('languages/', ContentManagementView.as_view(), name='language-management'),
    ])),
    
    # User moderation tools
    path('moderation/', include([
        path('reports/', UserManagementView.as_view(), name='user-reports'),
        path('flags/', UserManagementView.as_view(), name='content-flags'),
    ])),
    
    # Legacy endpoints (for backward compatibility)
    path('vocabulary/legacy/', include('api.staff.vocabulary.urls')),
    path('books/legacy/', include('api.staff.books.urls')),
    path('analytics/legacy/', include('api.staff.analytics.urls')),
]