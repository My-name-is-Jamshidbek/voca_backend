# API Token Management System

## Overview

The Token Management System provides secure API access control for the vocabulary learning application. It supports two types of tokens:

1. **Mobile App Tokens** - For mobile applications with role-based permissions
2. **API Client Tokens** - For external API clients with granular CRUD permissions

## Features

### 🔐 **Security Features**
- Secure token generation with cryptographically random strings
- IP address restrictions
- Rate limiting for API clients
- Token expiration and usage limits
- Comprehensive usage logging and analytics

### 📱 **Mobile App Tokens**
- Role-based access control (User, Staff, Admin)
- App version requirements
- Usage tracking and analytics
- Automatic token validation middleware

### 🔧 **API Client Tokens**
- Granular CRUD permissions per model
- Field-level access restrictions
- Rate limiting (hourly and daily)
- Endpoint restrictions
- Bulk operations support

### 📊 **Analytics & Monitoring**
- Real-time usage statistics
- Response time tracking
- Error rate monitoring
- Token performance analytics

## Token Types

### Mobile App Tokens

Mobile app tokens are designed for mobile applications and include:

**Required Fields:**
- `name` - Token identifier
- `app_version` - Required app version (ForeignKey to AppVersion)
- `role` - User role (user/staff/admin)

**Optional Fields:**
- `description` - Token description
- `expires_at` - Token expiration date
- `max_usage_count` - Maximum usage limit
- `allowed_ips` - List of allowed IP addresses

**Token Format:** `mob_` + 60 random characters

**Example:**
```json
{
    "name": "iOS App v2.1",
    "description": "Production iOS app token",
    "app_version": 1,
    "role": "user",
    "expires_at": "2025-12-31T23:59:59Z",
    "allowed_ips": ["192.168.1.100", "10.0.0.50"]
}
```

### API Client Tokens

API client tokens are designed for external systems and include:

**Required Fields:**
- `name` - Token identifier
- `client_name` - Client application name
- `client_email` - Client contact email

**Optional Fields:**
- `description` - Token description
- `client_organization` - Client organization
- `expires_at` - Token expiration date
- `max_usage_count` - Maximum usage limit
- `rate_limit_per_hour` - Hourly request limit (default: 1000)
- `rate_limit_per_day` - Daily request limit (default: 10000)
- `allowed_ips` - List of allowed IP addresses
- `allowed_endpoints` - List of allowed API endpoints

**Token Format:** `api_` + 60 random characters

**Example:**
```json
{
    "name": "Partner Analytics API",
    "description": "Token for analytics partner integration",
    "client_name": "Analytics Corp",
    "client_email": "api@analytics.corp",
    "client_organization": "Analytics Corporation",
    "rate_limit_per_hour": 500,
    "rate_limit_per_day": 5000,
    "allowed_endpoints": ["/api/cruds/words/", "/api/cruds/user-progress/"]
}
```

## Model Permissions

API client tokens can have granular permissions for each model in the system:

### Available Models:
- **accounts**: User, UserDevice
- **vocabulary**: Language, Book, Chapter, DifficultyLevel, Word, WordTranslation, WordDefinition, Collection, CollectionWord
- **progress**: UserProgress, UserSession
- **versioning**: AppVersion
- **tokens**: MobileAppToken, APIClientToken, TokenModelPermission

### Permission Types:
- `can_create` - Create new records
- `can_read` - Read/retrieve records
- `can_update` - Update existing records
- `can_delete` - Delete records
- `can_list` - List/search records
- `can_bulk_create` - Bulk create operations
- `can_bulk_update` - Bulk update operations
- `can_bulk_delete` - Bulk delete operations

### Field Restrictions:
- `restricted_fields` - List of fields that cannot be accessed
- `readonly_fields` - List of fields that are read-only

**Example Permission:**
```json
{
    "model_name": "Word",
    "can_create": true,
    "can_read": true,
    "can_update": false,
    "can_delete": false,
    "can_list": true,
    "restricted_fields": ["created_by", "internal_notes"],
    "readonly_fields": ["created_at", "updated_at"]
}
```

## API Endpoints

### Admin Endpoints (Staff/Admin only)

#### Mobile App Tokens
- `GET /api/admin/tokens/mobile-tokens/` - List mobile tokens
- `POST /api/admin/tokens/mobile-tokens/` - Create mobile token
- `GET /api/admin/tokens/mobile-tokens/{id}/` - Get mobile token details
- `PUT /api/admin/tokens/mobile-tokens/{id}/` - Update mobile token
- `DELETE /api/admin/tokens/mobile-tokens/{id}/` - Delete mobile token
- `POST /api/admin/tokens/mobile-tokens/{id}/regenerate/` - Regenerate token
- `POST /api/admin/tokens/mobile-tokens/{id}/revoke/` - Revoke token
- `POST /api/admin/tokens/mobile-tokens/{id}/activate/` - Activate token
- `GET /api/admin/tokens/mobile-tokens/{id}/usage_stats/` - Get usage statistics
- `POST /api/admin/tokens/mobile-tokens/bulk_action/` - Bulk actions
- `GET /api/admin/tokens/mobile-tokens/statistics/` - Overall statistics

#### API Client Tokens
- `GET /api/admin/tokens/api-tokens/` - List API tokens
- `POST /api/admin/tokens/api-tokens/` - Create API token
- `GET /api/admin/tokens/api-tokens/{id}/` - Get API token details
- `PUT /api/admin/tokens/api-tokens/{id}/` - Update API token
- `DELETE /api/admin/tokens/api-tokens/{id}/` - Delete API token
- `POST /api/admin/tokens/api-tokens/{id}/regenerate/` - Regenerate token
- `POST /api/admin/tokens/api-tokens/{id}/revoke/` - Revoke token
- `POST /api/admin/tokens/api-tokens/{id}/activate/` - Activate token
- `GET /api/admin/tokens/api-tokens/{id}/permissions/` - Get permissions
- `POST /api/admin/tokens/api-tokens/{id}/permissions/` - Set permissions
- `GET /api/admin/tokens/api-tokens/{id}/usage_stats/` - Get usage statistics
- `POST /api/admin/tokens/api-tokens/bulk_action/` - Bulk actions
- `POST /api/admin/tokens/api-tokens/bulk_permissions_update/` - Bulk permissions update
- `GET /api/admin/tokens/api-tokens/statistics/` - Overall statistics

#### Token Permissions
- `GET /api/admin/tokens/permissions/` - List all permissions
- `POST /api/admin/tokens/permissions/` - Create permission
- `GET /api/admin/tokens/permissions/{id}/` - Get permission details
- `PUT /api/admin/tokens/permissions/{id}/` - Update permission
- `DELETE /api/admin/tokens/permissions/{id}/` - Delete permission
- `GET /api/admin/tokens/permissions/by_model/` - Permissions by model
- `GET /api/admin/tokens/permissions/by_token/` - Permissions by token

### Public Endpoints

#### Token Validation
- `POST /api/tokens/validate/` - Validate token (no auth required)

#### Token Statistics (Authenticated)
- `GET /api/tokens/stats/` - Get token statistics

#### Usage Logs (Authenticated)
- `GET /api/tokens/usage-logs/` - Get usage logs

## Authentication

### Using Tokens

Include the token in the Authorization header:

```http
Authorization: Bearer mob_ABC123DEF456GHI789JKL012MNO345PQR678STU901VWX234YZ567890
```

### Token Validation Flow

1. Client sends request with token in Authorization header
2. Middleware extracts and validates token
3. System checks token status, expiration, IP restrictions
4. For API tokens, system checks rate limits and endpoint permissions
5. Request is processed or rejected based on validation result
6. Usage is logged for analytics

## Usage Examples

### Creating a Mobile App Token

```bash
curl -X POST "https://api.vocaapp.com/api/admin/tokens/mobile-tokens/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iOS Production App",
    "description": "Production token for iOS app v2.1",
    "app_version": 1,
    "role": "user",
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

### Creating an API Client Token with Permissions

```bash
curl -X POST "https://api.vocaapp.com/api/admin/tokens/api-tokens/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Analytics Partner",
    "client_name": "Analytics Corp API",
    "client_email": "api@analytics.corp",
    "rate_limit_per_hour": 500,
    "permissions_data": [
      {
        "model_name": "Word",
        "can_read": true,
        "can_list": true
      },
      {
        "model_name": "UserProgress",
        "can_read": true,
        "can_list": true
      }
    ]
  }'
```

### Using a Token to Access API

```bash
curl -X GET "https://api.vocaapp.com/api/cruds/words/" \
  -H "Authorization: Bearer api_XYZ789ABC012DEF345GHI678JKL901MNO234PQR567STU890VWX123"
```

### Validating a Token

```bash
curl -X POST "https://api.vocaapp.com/api/tokens/validate/" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "mob_ABC123DEF456GHI789JKL012MNO345PQR678STU901VWX234YZ567890",
    "endpoint": "/api/cruds/words/",
    "method": "GET",
    "ip_address": "192.168.1.100"
  }'
```

## Security Considerations

### Best Practices

1. **Token Storage**: Store tokens securely and never expose them in logs
2. **Token Rotation**: Regularly regenerate tokens for better security
3. **IP Restrictions**: Use IP allowlists for additional security
4. **Rate Limiting**: Set appropriate rate limits based on usage patterns
5. **Monitoring**: Monitor token usage for suspicious activity
6. **Expiration**: Set reasonable expiration dates for tokens

### Rate Limiting

API client tokens include built-in rate limiting:
- **Hourly Limit**: Requests per hour (default: 1000)
- **Daily Limit**: Requests per day (default: 10000)
- **Automatic Blocking**: Requests are blocked when limits are exceeded

### Usage Logging

All token usage is logged with:
- Timestamp and response time
- IP address and user agent
- Request/response sizes
- Status codes and errors
- Endpoint and HTTP method

## Monitoring & Analytics

### Token Statistics

The system provides comprehensive analytics:
- Token usage trends
- Most active tokens
- Error rates by token
- Response time analytics
- Geographic usage patterns

### Usage Alerts

Monitor for:
- Unusual usage spikes
- High error rates
- Slow response times
- Unauthorized access attempts
- Rate limit violations

## Migration & Deployment

### Database Migrations

```bash
python manage.py makemigrations tokens
python manage.py migrate
```

### Initial Setup

1. Add to `INSTALLED_APPS` in settings
2. Include URLs in main URL configuration
3. Add middleware to `MIDDLEWARE` setting (optional)
4. Create initial admin user for token management

### Environment Variables

```env
# Token settings (optional)
TOKEN_DEFAULT_EXPIRY_DAYS=365
TOKEN_MAX_USAGE_COUNT=1000000
TOKEN_RATE_LIMIT_HOUR=1000
TOKEN_RATE_LIMIT_DAY=10000
```

## Troubleshooting

### Common Issues

1. **Token Not Found**: Check token format and database
2. **Permission Denied**: Verify model permissions are set correctly
3. **Rate Limit Exceeded**: Check hourly/daily usage limits
4. **IP Blocked**: Verify IP allowlist configuration
5. **Token Expired**: Check expiration date and status

### Debugging

Enable debug logging for token middleware:

```python
LOGGING = {
    'loggers': {
        'apps.tokens': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Support

For technical support or questions about the token management system:
- Check the API documentation
- Review usage logs for debugging
- Contact the development team
- Submit issues via the project repository