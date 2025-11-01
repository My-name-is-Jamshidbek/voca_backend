# Base Authentication APIs Documentation

This document describes the comprehensive base authentication system for the Voca backend application, including role-based access control for admin, staff, and user roles.

## Overview

The authentication system provides:
- JWT-based authentication with refresh tokens
- Role-based access control (Admin, Staff, User)
- Token-based authentication for mobile apps and API clients
- Comprehensive user management and profile features
- Password reset and change functionality
- Device management for multi-platform synchronization

## Authentication Methods

### 1. JWT Authentication
Standard JWT tokens for web and mobile applications with role-based permissions.

### 2. Token-Based Authentication
Custom token system supporting:
- **Mobile App Tokens**: Role-based tokens for mobile applications with version requirements
- **API Client Tokens**: Granular permission-based tokens for third-party integrations

## API Endpoints

### Base Authentication (`/api/base/auth/`)

#### Login
- **POST** `/api/base/auth/login/`
- **Description**: Authenticate user and return JWT tokens
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "device_id": "optional_device_id",
    "platform": "ios|android|web|desktop"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Login successful",
    "data": {
      "tokens": {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token"
      },
      "user": {
        "id": "user_id",
        "email": "user@example.com",
        "username": "username",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_staff": false,
        "is_superuser": false,
        "auth_provider": "email",
        "preferred_language": "en",
        "profile_picture": null,
        "last_login": "2023-01-01T12:00:00Z",
        "date_joined": "2023-01-01T12:00:00Z"
      }
    }
  }
  ```

#### Register
- **POST** `/api/base/auth/register/`
- **Description**: Register new user account
- **Request Body**:
  ```json
  {
    "email": "newuser@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "username": "optional_username",
    "first_name": "John",
    "last_name": "Doe",
    "preferred_language": "en",
    "device_id": "optional_device_id",
    "platform": "ios"
  }
  ```

#### Logout
- **POST** `/api/base/auth/logout/`
- **Description**: Logout user and blacklist refresh token
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "refresh_token": "jwt_refresh_token"
  }
  ```

#### Token Refresh
- **POST** `/api/base/auth/refresh/`
- **Description**: Refresh access token using refresh token

#### Password Change
- **POST** `/api/base/auth/password/change/`
- **Description**: Change user password
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "old_password": "current_password",
    "new_password": "new_password",
    "new_password_confirm": "new_password"
  }
  ```

#### Password Reset Request
- **POST** `/api/base/auth/password/reset/`
- **Description**: Request password reset email
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```

#### Password Reset Confirm
- **POST** `/api/base/auth/password/reset/confirm/`
- **Description**: Confirm password reset with token
- **Request Body**:
  ```json
  {
    "uid": "base64_encoded_user_id",
    "token": "reset_token",
    "new_password": "new_password",
    "new_password_confirm": "new_password"
  }
  ```

#### Profile Management
- **GET** `/api/base/auth/profile/`
- **PATCH** `/api/base/auth/profile/`
- **Description**: Get or update user profile
- **Headers**: `Authorization: Bearer <access_token>`

#### Device Management
- **GET** `/api/base/auth/devices/`
- **POST** `/api/base/auth/devices/`
- **DELETE** `/api/base/auth/devices/<device_id>/`
- **Description**: Manage user devices for synchronization

### User APIs (`/api/user/`)

#### Dashboard
- **GET** `/api/user/dashboard/`
- **Description**: Get user dashboard with learning statistics and recent activity
- **Permissions**: User role or higher
- **Response**: Learning statistics, recent sessions, collection progress, weekly goals

#### Vocabulary Management
- **GET** `/api/user/vocabulary/`
- **Description**: Get user's vocabulary with learning progress
- **Query Parameters**: 
  - `difficulty`: Filter by difficulty level
  - `language`: Filter by language ID
  - `mastery_level`: Filter by mastery level
  - `search`: Search in words and translations
  - `page`: Page number
  - `page_size`: Items per page

#### Collections
- **GET** `/api/user/collections/`
- **Description**: Get user's learning collections with progress

#### Progress Analytics
- **GET** `/api/user/progress/`
- **Description**: Get detailed learning progress and statistics
- **Query Parameters**: `days`: Time range in days (default: 30)

#### Spaced Repetition Review
- **GET** `/api/user/review/`
- **POST** `/api/user/review/`
- **Description**: Get words due for review and submit review results
- **GET Query Parameters**: `limit`: Number of words to review (default: 20)
- **POST Request Body**:
  ```json
  {
    "results": [
      {
        "progress_id": "progress_id",
        "is_correct": true
      }
    ]
  }
  ```

### Staff APIs (`/api/staff/`)

#### Staff Dashboard
- **GET** `/api/staff/dashboard/`
- **Description**: Get staff dashboard with system overview
- **Permissions**: Staff role or higher
- **Response**: User statistics, content statistics, activity metrics, most active users

#### User Management
- **GET** `/api/staff/users/`
- **PATCH** `/api/staff/users/<user_id>/`
- **Description**: View and manage users
- **Query Parameters**: Search, filters for auth provider, activity, dates
- **PATCH Actions**: Activate/deactivate users

#### Content Management
- **GET** `/api/staff/content/`
- **Description**: Get content statistics and recent additions
- **Response**: Language statistics, recent words, collections, quality metrics

#### Learning Analytics
- **GET** `/api/staff/analytics/`
- **Description**: Get learning analytics and trends
- **Query Parameters**: `days`: Time range for analytics
- **Response**: Daily trends, language popularity, challenging words, engagement metrics

#### System Health
- **GET** `/api/staff/health/`
- **Description**: Get system health metrics and monitoring data

### Admin APIs (`/api/admin/`)

#### Admin Dashboard
- **GET** `/api/admin/dashboard/`
- **Description**: Get comprehensive system overview
- **Permissions**: Admin role only
- **Response**: Complete system statistics, health indicators, token usage

#### System Administration
- **GET** `/api/admin/system/`
- **POST** `/api/admin/system/`
- **Description**: Manage system configuration and perform admin actions
- **POST Actions**: 
  - `maintenance_mode`: Toggle maintenance mode
  - `clear_cache`: Clear application cache
  - `backup_database`: Initiate database backup

#### User Administration
- **GET** `/api/admin/users/`
- **POST** `/api/admin/users/`
- **Description**: Advanced user management with bulk operations
- **POST Actions**:
  - `activate`: Bulk activate users
  - `deactivate`: Bulk deactivate users
  - `promote_to_staff`: Promote users to staff
  - `demote_from_staff`: Demote users from staff

#### Token Administration
- **GET** `/api/admin/tokens/`
- **POST** `/api/admin/tokens/`
- **Description**: Manage mobile app and API client tokens
- **POST Actions**: `activate`, `deactivate`, `revoke` tokens

#### System Analytics
- **GET** `/api/admin/analytics/`
- **Description**: Advanced system analytics and performance metrics
- **Query Parameters**: `days`: Time range for analytics

## Role-Based Permissions

### User Role
- Access to personal dashboard, vocabulary, and learning features
- Can manage own profile and devices
- Can participate in spaced repetition system
- Read-only access to learning materials

### Staff Role
- All user permissions
- User management (view, search, activate/deactivate)
- Content management overview
- Learning analytics and trends
- System health monitoring

### Admin Role
- All staff permissions
- System administration and maintenance
- Advanced user management with bulk operations
- Token administration and security
- Complete system analytics and performance metrics
- Database and backup management

## Authentication Headers

### JWT Authentication
```
Authorization: Bearer <jwt_access_token>
```

### Token-Based Authentication
```
Authorization: Bearer <mobile_or_api_token>
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": true,
  "message": "Error description",
  "details": "Additional error details",
  "error_code": "ERROR_CODE",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## Common HTTP Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request / Validation Error
- **401**: Unauthorized / Authentication Required
- **403**: Forbidden / Permission Denied
- **404**: Not Found
- **429**: Rate Limited
- **500**: Internal Server Error

## Security Features

### Token Security
- JWT tokens with configurable expiration
- Refresh token rotation
- Token blacklisting on logout
- IP address restrictions for API tokens
- Rate limiting per token

### Password Security
- Strong password validation
- Secure password reset flow
- Password change requires current password
- Account lockout protection (configurable)

### Role-Based Access Control
- Hierarchical role system (User < Staff < Admin)
- Granular permissions for API client tokens
- Model-level and field-level restrictions
- Audit logging for admin actions

## Rate Limiting

- User APIs: 1000 requests/hour
- Staff APIs: 2000 requests/hour  
- Admin APIs: 5000 requests/hour
- API Client Tokens: Configurable per token

## Getting Started

1. **Register a new user**:
   ```bash
   curl -X POST http://localhost:8000/api/base/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123","password_confirm":"testpass123"}'
   ```

2. **Login to get tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/base/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'
   ```

3. **Access protected endpoints**:
   ```bash
   curl -X GET http://localhost:8000/api/user/dashboard/ \
     -H "Authorization: Bearer <access_token>"
   ```

## Development Notes

- All import errors in the code are expected since the Django environment is not configured in the workspace
- The authentication system is designed to be production-ready with proper security measures
- Token-based authentication supports both mobile apps and API clients with different permission models
- The system includes comprehensive logging and monitoring capabilities
- Social authentication (Google, Apple) endpoints are placeholder for future implementation