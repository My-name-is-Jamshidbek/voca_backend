# CRUD API Modular Structure

This directory contains the restructured CRUD API implementation organized by Django apps for better maintainability and scalability.

## 📁 Folder Structure

```
api/cruds/
├── __init__.py                 # Main module initialization
├── urls.py                     # Main URL routing to app modules
├── views.py                    # Legacy views file (deprecated)
├── serializers.py             # Legacy serializers file (deprecated)
├── common/                     # Shared components
│   ├── __init__.py
│   └── base.py                # BaseModelViewSet, TokenPermissionMixin
├── accounts/                   # User and Device management
│   ├── __init__.py
│   ├── serializers.py         # User, UserDevice serializers
│   ├── views.py               # User, UserDevice ViewSets
│   └── urls.py                # Accounts app routing
├── vocabulary/                 # Vocabulary management
│   ├── __init__.py
│   ├── serializers.py         # Language, Book, Word, etc. serializers
│   ├── views.py               # Vocabulary ViewSets
│   └── urls.py                # Vocabulary app routing
├── progress/                   # Learning progress tracking
│   ├── __init__.py
│   ├── serializers.py         # UserProgress, UserSession serializers
│   ├── views.py               # Progress ViewSets
│   └── urls.py                # Progress app routing
├── versioning/                 # App version management
│   ├── __init__.py
│   ├── serializers.py         # AppVersion serializers
│   ├── views.py               # Versioning ViewSets
│   └── urls.py                # Versioning app routing
└── tokens/                     # Token reference APIs
    ├── __init__.py
    ├── serializers.py         # Token serializers (read-only)
    ├── views.py               # Token ViewSets (read-only)
    └── urls.py                # Tokens app routing
```

## 🚀 Benefits of Modular Structure

### ✅ **Code Organization**
- **Separation by Django App**: Each folder corresponds to a Django app
- **Clear Responsibilities**: Each module handles specific domain logic
- **Easy Navigation**: Developers can quickly find relevant code

### ✅ **Maintainability**
- **Isolated Changes**: Modifications to one app don't affect others
- **Smaller Files**: More manageable file sizes
- **Clear Dependencies**: Import relationships are explicit

### ✅ **Scalability**
- **Easy to Add**: New apps can be added as separate modules
- **Team Development**: Multiple developers can work on different modules
- **Testing**: Each module can be tested independently

### ✅ **Django Best Practices**
- **App-based Organization**: Follows Django's app-centric design
- **Reusable Components**: Common functionality in shared modules
- **Clean Architecture**: Clear separation of concerns

## 🔗 API Endpoints Structure

### **Accounts Module** (`/api/cruds/accounts/`)
```
GET|POST    /users/                    - User management
GET|PUT|DEL /users/{id}/               - User details/update/delete
GET         /users/{id}/devices/       - User's devices
GET         /users/{id}/profile_stats/ - User statistics

GET|POST    /user-devices/             - Device management
GET|PUT|DEL /user-devices/{id}/        - Device details/update/delete
POST        /user-devices/{id}/sync_data/     - Update sync
POST        /user-devices/{id}/deactivate/   - Deactivate device
```

### **Vocabulary Module** (`/api/cruds/vocabulary/`)
```
# Languages
GET|POST    /languages/                - Language management
GET         /languages/active/         - Active languages only

# Books & Chapters
GET|POST    /books/                    - Book management
GET         /books/{id}/chapters/      - Book chapters
GET         /books/{id}/words/         - Book words

GET|POST    /chapters/                 - Chapter management
GET         /chapters/{id}/words/      - Chapter words

# Words & Related
GET|POST    /words/                    - Word management
GET         /words/by_difficulty/      - Filter by difficulty
POST        /words/{id}/mark_progress/ - Mark progress
GET         /words/{id}/translations/  - Word translations
GET         /words/{id}/definitions/   - Word definitions

GET|POST    /word-translations/        - Translation management
GET|POST    /word-definitions/         - Definition management

# Collections
GET|POST    /collections/              - Collection management
POST        /collections/{id}/add_word/    - Add word to collection
DELETE      /collections/{id}/remove_word/ - Remove word

GET|POST    /collection-words/         - Collection word management

# Difficulty Levels
GET|POST    /difficulty-levels/        - Difficulty level management
```

### **Progress Module** (`/api/cruds/progress/`)
```
GET|POST    /user-progress/            - Learning progress
GET         /user-progress/due_for_review/    - Words due for review
GET         /user-progress/statistics/        - Progress statistics
POST        /user-progress/{id}/update_review/ - Update review

GET|POST    /user-sessions/            - Study sessions
POST        /user-sessions/log_activity/      - Log activity
GET         /user-sessions/weekly_stats/      - Weekly statistics
```

### **Versioning Module** (`/api/cruds/versioning/`)
```
GET|POST    /app-versions/             - App version management
GET         /app-versions/latest/      - Latest versions
GET         /app-versions/check_update/ - Check for updates
```

### **Tokens Module** (`/api/cruds/tokens/`) - Read-only
```
GET         /mobile-tokens/            - Mobile token reference
GET         /mobile-tokens/usage_stats/ - Mobile token statistics

GET         /api-tokens/               - API token reference
GET         /api-tokens/usage_stats/   - API token statistics
GET         /api-tokens/{id}/permissions_detail/ - Token permissions
```

## 🔧 Common Components

### **BaseModelViewSet** (`common/base.py`)
- Standardized CRUD operations
- Token permission integration
- Unified response format
- Error handling

### **TokenPermissionMixin** (`common/base.py`)
- Token-based authentication
- Model-level permissions
- Field-level restrictions
- Role-based access control

## 📋 Features by Module

### **Accounts Features**
- User profile management
- Device registration and sync
- Multi-device support
- User statistics and analytics

### **Vocabulary Features**
- Multi-language support
- CEFR difficulty levels
- Book and chapter organization
- Word translations and definitions
- Personal collections
- Progress tracking integration

### **Progress Features**
- Spaced repetition algorithm
- Learning statistics
- Session tracking
- Review scheduling
- Performance analytics

### **Versioning Features**
- Platform-specific versions
- Update checking
- Mandatory updates
- Beta version support

### **Tokens Features**
- Token usage monitoring
- Permission management
- Security analytics
- Admin reference

## 🔐 Security Features

### **Token Authentication**
- Mobile app tokens (role-based)
- API client tokens (permission-based)
- Automatic token validation
- Usage logging

### **Permission Control**
- Model-level CRUD permissions
- Field-level restrictions
- User-scoped data access
- Admin privilege escalation

## 🧪 Testing Strategy

Each module can be tested independently:

```python
# Test accounts module
python manage.py test api.cruds.accounts

# Test vocabulary module  
python manage.py test api.cruds.vocabulary

# Test progress module
python manage.py test api.cruds.progress

# Test versioning module
python manage.py test api.cruds.versioning

# Test tokens module
python manage.py test api.cruds.tokens
```

## 📈 Migration Guide

### From Legacy Structure
The old monolithic files (`views.py`, `serializers.py`) have been split into modular components:

**Old Structure:**
```
cruds/
├── views.py (1000+ lines)
├── serializers.py (800+ lines)
└── urls.py
```

**New Structure:**
```
cruds/
├── accounts/ (User management)
├── vocabulary/ (Word management)  
├── progress/ (Learning tracking)
├── versioning/ (App updates)
├── tokens/ (Security reference)
└── common/ (Shared components)
```

### Import Changes
```python
# Old imports
from api.cruds.views import UserViewSet
from api.cruds.serializers import UserSerializer

# New imports  
from api.cruds.accounts.views import UserViewSet
from api.cruds.accounts.serializers import UserSerializer

# Or use the main module for backward compatibility
from api.cruds import UserViewSet, UserSerializer
```

## 🎯 Best Practices

### **Adding New Models**
1. Determine the appropriate app module
2. Create serializer in `{app}/serializers.py`
3. Create ViewSet in `{app}/views.py`
4. Add route to `{app}/urls.py`
5. Update main `__init__.py` for exports

### **Custom Actions**
Add custom actions to the appropriate ViewSet:
```python
@action(detail=True, methods=['post'])
def custom_action(self, request, pk=None):
    # Implementation
    pass
```

### **Cross-Module Dependencies**
- Import other modules as needed
- Use lazy imports for circular dependency prevention
- Keep dependencies minimal and explicit

This modular structure provides a robust, scalable foundation for the vocabulary learning API while maintaining clean code organization and Django best practices.