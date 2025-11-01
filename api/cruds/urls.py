"""
Main CRUD API URLs - Modular Structure by App
Routes are organized by Django app for better maintainability
"""
from django.urls import path, include

app_name = 'cruds'

urlpatterns = [
    # Accounts App CRUD APIs
    path('accounts/', include('api.cruds.accounts.urls')),
    
    # Vocabulary App CRUD APIs  
    path('vocabulary/', include('api.cruds.vocabulary.urls')),
    
    # Progress App CRUD APIs
    path('progress/', include('api.cruds.progress.urls')),
    
    # Versioning App CRUD APIs
    path('versioning/', include('api.cruds.versioning.urls')),
    
    # Tokens App CRUD APIs (read-only reference)
    path('tokens/', include('api.cruds.tokens.urls')),
]

"""
New Modular API Structure:

ACCOUNTS ENDPOINTS:
- /api/cruds/accounts/users/                    - User management
- /api/cruds/accounts/user-devices/             - Device management

VOCABULARY ENDPOINTS:
- /api/cruds/vocabulary/languages/              - Language management
- /api/cruds/vocabulary/difficulty-levels/      - Difficulty levels
- /api/cruds/vocabulary/books/                  - Book management
- /api/cruds/vocabulary/chapters/               - Chapter management
- /api/cruds/vocabulary/words/                  - Word management
- /api/cruds/vocabulary/word-translations/      - Translation management
- /api/cruds/vocabulary/word-definitions/       - Definition management
- /api/cruds/vocabulary/collections/            - Collection management
- /api/cruds/vocabulary/collection-words/       - Collection word management

PROGRESS ENDPOINTS:
- /api/cruds/progress/user-progress/            - Learning progress
- /api/cruds/progress/user-sessions/            - Study sessions

VERSIONING ENDPOINTS:
- /api/cruds/versioning/app-versions/           - App version management

TOKENS ENDPOINTS (Read-only):
- /api/cruds/tokens/mobile-tokens/              - Mobile token reference
- /api/cruds/tokens/api-tokens/                 - API token reference

Benefits of Modular Structure:
✅ Better code organization and maintainability
✅ Clear separation of concerns by Django app
✅ Easier to locate and modify specific functionality
✅ Cleaner import structure and dependencies
✅ Scalable for adding new apps and models
✅ Follows Django best practices for large projects
"""