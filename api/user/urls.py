"""
User API URLs - Endpoints accessible to regular users
"""
from django.urls import path, include
from .views import (
    UserDashboardView,
    UserVocabularyView,
    UserCollectionsView,
    UserProgressView,
    UserReviewView,
    UserProfileDetailView,
)

app_name = 'user'

urlpatterns = [
    # User dashboard and overview
    path('dashboard/', UserDashboardView.as_view(), name='dashboard'),
    
    # User profile management
    path('profile/', UserProfileDetailView.as_view(), name='profile-detail'),
    
    # Vocabulary management
    path('vocabulary/', UserVocabularyView.as_view(), name='vocabulary'),
    path('collections/', UserCollectionsView.as_view(), name='collections'),
    
    # Learning progress and statistics
    path('progress/', UserProgressView.as_view(), name='progress'),
    
    # Spaced repetition review system
    path('review/', UserReviewView.as_view(), name='review'),
    
    # Learning sessions and practice
    path('practice/', include([
        # These could be added later for specific practice modes
        path('flashcards/', UserReviewView.as_view(), name='practice-flashcards'),
        path('quiz/', UserReviewView.as_view(), name='practice-quiz'),
        path('writing/', UserReviewView.as_view(), name='practice-writing'),
    ])),
    
    # User settings and preferences
    path('settings/', include([
        path('notifications/', UserProfileDetailView.as_view(), name='notification-settings'),
        path('learning/', UserProfileDetailView.as_view(), name='learning-settings'),
        path('privacy/', UserProfileDetailView.as_view(), name='privacy-settings'),
    ])),
    
    # Legacy endpoints (for backward compatibility if needed)
    path('vocabulary/legacy/', include('api.user.vocabulary.urls')),
    path('profile/legacy/', include('api.user.profile.urls')),
    path('progress/legacy/', include('api.user.progress.urls')),
]