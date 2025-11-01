# API Base Module - Modular Architecture

This document describes the restructured API base module that follows a modular architecture pattern consistent with the CRUDS API structure.

## 📁 Directory Structure

```
api/base/
├── __init__.py                 # Base module initialization
├── urls.py                     # Main URL routing to submodules
├── README.md                   # This documentation file
├── common/                     # Shared utilities and base classes
│   ├── __init__.py            # Common module exports
│   ├── views.py               # APIRootView and shared base classes
│   ├── permissions.py         # Role-based permissions
│   └── responses.py           # Standardized response utilities
├── authentication/            # Authentication and user management
│   ├── __init__.py            # Authentication module exports
│   ├── urls.py               # Authentication URL routing
│   ├── views.py              # Authentication views (JWT, register, etc.)
│   ├── permissions.py        # Authentication-specific permissions
│   └── responses.py          # Authentication response utilities
├── health/                    # Health monitoring and system status
│   ├── __init__.py           # Health module exports
│   ├── urls.py               # Health check URL routing
│   └── views.py              # Health check and system status views
└── documentation/             # API documentation and schema
    ├── __init__.py           # Documentation module exports
    ├── urls.py               # Documentation URL routing
    └── views.py              # API schema, Swagger UI, ReDoc views
```

## 🏗️ Architecture Overview

### Modular Design Principles

1. **Separation of Concerns**: Each module handles a specific aspect of the base API
2. **Reusability**: Common utilities are shared across modules
3. **Maintainability**: Clear module boundaries make code easier to maintain
4. **Consistency**: Follows the same pattern as the CRUDS API structure
5. **Scalability**: Easy to add new modules or extend existing ones

### Module Responsibilities

#### `common/` - Shared Foundation
- **Purpose**: Provides shared utilities, base classes, and common functionality
- **Key Components**:
  - `APIRootView`: Main API entry point with service information
  - `RoleBasedPermission` classes: User, Staff, Admin permission hierarchies
  - `ResponseMixin`: Standardized response formatting
  - Response utility functions: `success_response()`, `error_response()`

#### `authentication/` - User Management
- **Purpose**: Handles all authentication and user account management
- **Key Features**:
  - JWT token authentication with refresh tokens
  - User registration and profile management
  - Password change and reset workflows
  - Device management for mobile/API clients
  - Token validation and logout functionality
- **Security**: Role-based permissions with hierarchical access control

#### `health/` - System Monitoring
- **Purpose**: Provides health checks and system status monitoring
- **Key Features**:
  - Basic health check endpoint (`/health/`)
  - Comprehensive system status (`/health/status/`)
  - Readiness and liveness probes for Kubernetes
  - Database, cache, and memory monitoring
  - Service dependency checking

#### `documentation/` - API Documentation
- **Purpose**: Provides comprehensive API documentation and interactive tools
- **Key Features**:
  - OpenAPI/Swagger schema generation
  - Interactive Swagger UI (`/docs/swagger/`)
  - Alternative ReDoc interface (`/docs/redoc/`)
  - Comprehensive API documentation (`/docs/`)
  - Usage examples and authentication guides

## 🔧 URL Structure

### Main Routes (`/api/base/`)
```
/api/base/                     # API root information
/api/base/auth/                # Authentication module
/api/base/health/              # Health monitoring module  
/api/base/docs/                # Documentation module
```

### Authentication Routes (`/api/base/auth/`)
```
POST   /login/                 # User login (JWT tokens)
POST   /register/              # User registration
POST   /logout/                # User logout
GET    /profile/               # User profile
PUT    /profile/               # Update profile
POST   /password/change/       # Change password
POST   /password/reset/        # Request password reset
POST   /password/reset/confirm/ # Confirm password reset
GET    /devices/               # List user devices
POST   /devices/               # Register new device
DELETE /devices/{device_id}/   # Remove device
POST   /validate/              # Validate token
POST   /refresh/               # Refresh JWT token
POST   /verify/                # Verify JWT token
```

### Health Routes (`/api/base/health/`)
```
GET    /                       # Basic health check
GET    /status/                # Detailed system status
GET    /ready/                 # Readiness probe
GET    /live/                  # Liveness probe
```

### Documentation Routes (`/api/base/docs/`)
```
GET    /                       # API documentation
GET    /schema/                # OpenAPI schema
GET    /swagger/               # Swagger UI
GET    /redoc/                 # ReDoc interface
```

## 🔐 Authentication & Permissions

### Authentication Methods

1. **JWT Tokens**: Primary authentication for web/mobile users
   - Access tokens (15 minutes expiry)
   - Refresh tokens (7 days expiry)
   - Device-specific token management

2. **Mobile/API Tokens**: Long-lived tokens for mobile apps and API clients
   - Configurable expiry per token
   - Device and platform tracking
   - Enhanced security features

### Permission Hierarchy

```
User (Base Level)
├── View own profile and data
├── Manage own vocabulary and progress
└── Access learning features

Staff (Inherits User + Additional)
├── View and manage users
├── Access content management tools
├── View learning analytics
└── Moderate user content

Admin (Inherits Staff + Additional)
├── Full system administration
├── Token and device management
├── Advanced analytics and reporting
├── System configuration access
└── All API endpoints access
```

## 📊 Response Format

### Standardized Response Structure

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data here
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response Structure

```json
{
    "success": false,
    "error": true,
    "message": "Error description",
    "details": {
        // Error details here
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🚀 Getting Started

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 2. Testing Authentication
```bash
# Register a new user
curl -X POST http://localhost:8000/api/base/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Login to get tokens
curl -X POST http://localhost:8000/api/base/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

### 3. Health Check
```bash
# Basic health check
curl http://localhost:8000/api/base/health/

# Detailed system status
curl http://localhost:8000/api/base/health/status/
```

## 🔧 Configuration

### Environment Variables
```bash
# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Health Check Settings
HEALTH_CHECK_TIMEOUT=30  # seconds
HEALTH_CHECK_CACHE_TTL=60  # seconds

# Rate Limiting
RATE_LIMIT_USER=1000     # requests per hour
RATE_LIMIT_STAFF=2000    # requests per hour
RATE_LIMIT_ADMIN=5000    # requests per hour
```

### Database Migrations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## 📈 Monitoring & Logging

### Health Monitoring
- **Readiness Probe**: `/api/base/health/ready/` - Ready to accept traffic
- **Liveness Probe**: `/api/base/health/live/` - Service is running
- **Status Check**: `/api/base/health/status/` - Detailed system health

### Logging
- Authentication events are logged with user context
- Health check failures are logged with system details
- API access is logged with performance metrics

## 🛠️ Development

### Adding New Features

1. **Create module-specific views** in the appropriate module
2. **Add URL routes** to the module's `urls.py`
3. **Update permissions** if needed in `permissions.py`
4. **Add tests** for new functionality
5. **Update documentation** in this README

### Testing
```bash
# Run all tests
python manage.py test api.base

# Run specific module tests
python manage.py test api.base.authentication
python manage.py test api.base.health
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/base/docs/swagger/
- **ReDoc**: http://localhost:8000/api/base/docs/redoc/
- **API Docs**: http://localhost:8000/api/base/docs/

### Schema Export
```bash
# Export OpenAPI schema
curl http://localhost:8000/api/base/docs/schema/ > api_schema.json
```

## 🔄 Migration from Old Structure

### Changed File Locations
```
OLD                           NEW
api/base/authentication.py   → api/base/authentication/views.py
api/base/permissions.py      → api/base/authentication/permissions.py
                               api/base/common/permissions.py
api/base/responses.py        → api/base/authentication/responses.py
                               api/base/common/responses.py
```

### URL Changes
- All existing URLs remain functional
- New modular URLs are available
- Backward compatibility maintained

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Django environment is properly configured
2. **Permission Denied**: Check user roles and token validity
3. **Health Check Failures**: Verify database and cache connections
4. **Token Expired**: Use refresh token to get new access token

### Debug Mode
```python
# Enable debug logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api.base': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📝 Changelog

### v1.0.1 - Cleanup and Optimization
- ✅ Removed unused legacy files (authentication.py, permissions.py, responses.py, serializers.py, auth.py)
- ✅ Organized common utilities into separate files (views.py, permissions.py, responses.py)
- ✅ Updated imports and module structure for better organization
- ✅ Verified all references and eliminated duplicate code
- ✅ Maintained full backward compatibility with existing URLs

### v1.0.0 - Initial Modular Structure
- ✅ Restructured monolithic files into modular architecture
- ✅ Created separate modules for authentication, health, documentation
- ✅ Implemented shared common utilities
- ✅ Added comprehensive health monitoring
- ✅ Enhanced API documentation with interactive tools
- ✅ Maintained backward compatibility with existing URLs
- ✅ Added role-based permission system
- ✅ Implemented standardized response format

## 🤝 Contributing

1. Follow the modular architecture pattern
2. Add tests for new functionality
3. Update documentation for changes
4. Maintain backward compatibility
5. Use standardized response format
6. Follow Django and DRF best practices

---

**Note**: This modular structure improves maintainability, follows established patterns, and provides a solid foundation for future API development.