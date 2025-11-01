# Voca Backend API - Role-Based Architecture

A professional Django REST API with MongoDB backend using djongo, featuring a comprehensive role-based API architecture.

## 🚀 Features

- **Role-Based API Architecture** (Admin, Staff, User, Public, CRUD)
- **Django 4.2+** with djongo for MongoDB integration
- **Django REST Framework** for API development
- **JWT Authentication** with role-based permissions
- **MongoDB** database with djongo
- **API Documentation** with drf-spectacular (Swagger/OpenAPI)
- **Environment Configuration** with django-environ
- **CORS Support** for frontend integration
- **Professional Modular Structure**
- **Comprehensive Error Handling**
- **Health Check Endpoints**
- **Docker Support**

## 🏗️ Project Structure

```
voca_backend/
├── manage.py                    # Django management script
├── requirements.txt            # All dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── README.md                  # This documentation
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Multi-container setup
├── setup.cfg                  # Code quality configuration
├── pytest.ini               # Test configuration
├── .pre-commit-config.yaml   # Pre-commit hooks
│
├── config/                   # 📁 Django Configuration
│   ├── __init__.py          # Celery integration
│   ├── settings.py          # Django settings with djongo
│   ├── urls.py              # Main URL configuration
│   ├── celery.py            # Celery configuration
│   ├── wsgi.py & asgi.py    # WSGI/ASGI applications
│
├── apps/                     # 📁 Django Applications
│   ├── __init__.py
│   ├── accounts/            # 👤 User Management
│   │   ├── models.py        # User, Permission, RolePermission
│   │   └── apps.py
│   ├── vocabulary/          # 📚 Vocabulary Management
│   │   ├── models.py        # Category, Word, UserWordProgress
│   │   └── apps.py
│   └── quizzes/             # 🎯 Quiz System
│       ├── models.py        # Quiz, Question, QuizAttempt, Answer
│       └── apps.py
│
├── api/                      # 🔗 Role-Based API Structure
│   ├── __init__.py
│   ├── base/                # 🌐 Public & Authentication APIs
│   │   ├── __init__.py      # Permissions and utilities
│   │   ├── auth.py          # Authentication views
│   │   ├── serializers.py   # Auth serializers
│   │   └── urls.py          # Auth endpoints
│   ├── user/                # 👥 User Role APIs
│   │   ├── views.py         # User-specific endpoints
│   │   └── urls.py
│   ├── staff/               # 👨‍💼 Staff Role APIs
│   │   ├── views.py         # Staff-specific endpoints
│   │   └── urls.py
│   ├── admin/               # 👨‍💻 Admin Role APIs
│   │   ├── views.py         # Admin-specific endpoints
│   │   └── urls.py
│   └── cruds/               # 🔧 Token-Based CRUD APIs
│       ├── views.py         # Full CRUD operations
│       ├── serializers.py   # CRUD serializers
│       └── urls.py
│
├── logs/                     # 📝 Application logs
├── static/                   # 🎨 Static files
└── media/                    # 📁 User uploads
```

## 🎯 API Architecture

### Role-Based API Organization

#### 1. 🌐 **Base APIs** (`/api/v1/base/`)
**Public Access & Authentication**
- ✅ Health check endpoint
- ✅ API root and documentation
- ✅ User registration
- ✅ Login/Logout (JWT)
- ✅ Password change
- ✅ Token refresh/verify

#### 2. 👥 **User APIs** (`/api/v1/user/`)
**User Role Required**
- ✅ Personal word learning progress
- ✅ Quiz taking and attempts
- ✅ User dashboard and statistics
- ✅ Personal learning analytics

#### 3. 👨‍💼 **Staff APIs** (`/api/v1/staff/`)
**Staff Role Required**
- ✅ Content management (Categories, Words, Quizzes)
- ✅ Bulk content operations
- ✅ Content analytics and reporting
- ✅ User progress monitoring
- ✅ Educational content oversight

#### 4. 👨‍💻 **Admin APIs** (`/api/v1/admin/`)
**Admin Role Required**
- ✅ Complete user management
- ✅ Role assignment and permissions
- ✅ System analytics and health monitoring
- ✅ Platform-wide statistics
- ✅ Permission system management

#### 5. 🔧 **CRUD APIs** (`/api/v1/cruds/`)
**Token-Based Authentication**
- ✅ Full CRUD operations for all models
- ✅ Accessible by all authenticated users
- ✅ Standardized response format
- ✅ Comprehensive filtering and search
- ✅ Pagination support

## 📊 Data Models

### User Management (`apps.accounts`)
- **User**: Custom user with role-based permissions
- **UserProfile**: Extended user information
- **Permission**: Custom permissions system
- **RolePermission**: Role-to-permission mapping

### Vocabulary System (`apps.vocabulary`)
- **Category**: Vocabulary organization
- **Word**: Vocabulary items with metadata
- **UserWordProgress**: Individual learning progress tracking

### Quiz System (`apps.quizzes`)
- **Quiz**: Quiz definitions and settings
- **Question**: Quiz questions with options
- **QuizAttempt**: User quiz sessions
- **Answer**: Individual question responses

## 🔐 Authentication & Permissions

### User Roles
- **User**: Standard learners (default role)
- **Staff**: Content managers and educators
- **Admin**: System administrators

### Permission System
- Role-based access control (RBAC)
- JWT token authentication
- Custom permission classes
- Fine-grained access control

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and navigate
git clone <repository-url>
cd voca_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings:
# - SECRET_KEY (generate new)
# - MONGO_URI (your MongoDB connection)
# - JWT_SECRET_KEY (generate new)
# - Other configurations as needed
```

### 3. Database Setup

```bash
# Ensure MongoDB is running
# Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

🎉 **API available at:** `http://localhost:8000/api/v1/`

## 📚 API Endpoints

### Base APIs (Public)
```
GET  /api/v1/base/health/                 # Health check
GET  /api/v1/base/docs/                   # API documentation
POST /api/v1/base/auth/register/          # User registration
POST /api/v1/base/auth/login/             # Login
POST /api/v1/base/auth/logout/            # Logout
POST /api/v1/base/auth/change-password/   # Change password
```

### User Role APIs
```
GET  /api/v1/user/words/                  # Browse words
POST /api/v1/user/words/{id}/mark-learned/ # Mark word as learned
GET  /api/v1/user/words/my-progress/      # Learning progress
GET  /api/v1/user/quizzes/                # Available quizzes
POST /api/v1/user/quizzes/{id}/take-quiz/ # Start quiz
GET  /api/v1/user/profile/dashboard/      # User dashboard
```

### Staff Role APIs
```
GET|POST|PUT|DELETE /api/v1/staff/categories/ # Manage categories
GET|POST|PUT|DELETE /api/v1/staff/words/      # Manage words
POST /api/v1/staff/words/bulk-create/         # Bulk create words
GET|POST|PUT|DELETE /api/v1/staff/quizzes/    # Manage quizzes
GET  /api/v1/staff/reports/dashboard/         # Staff dashboard
```

### Admin Role APIs
```
GET|POST|PUT|DELETE /api/v1/admin/users/       # User management
POST /api/v1/admin/users/{id}/change-role/     # Change user role
GET  /api/v1/admin/content/overview/           # Content overview
GET  /api/v1/admin/analytics/system-health/    # System health
GET  /api/v1/admin/analytics/usage-analytics/  # Usage analytics
```

### CRUD APIs (All Models)
```
GET|POST|PUT|DELETE /api/v1/cruds/categories/     # Category CRUD
GET|POST|PUT|DELETE /api/v1/cruds/words/          # Word CRUD
GET|POST|PUT|DELETE /api/v1/cruds/quizzes/        # Quiz CRUD
GET|POST|PUT|DELETE /api/v1/cruds/quiz-attempts/  # Quiz attempt CRUD
```

## 📖 API Documentation

Access interactive API documentation:
- **Swagger UI**: `http://localhost:8000/api/v1/base/docs/`
- **ReDoc**: `http://localhost:8000/api/v1/base/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/base/schema/`

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access services:
# - API: http://localhost:8000
# - MongoDB: localhost:27017
# - Redis: localhost:6379
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test module
pytest apps/accounts/tests.py
```

## 🔧 Development Tools

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Pre-commit hooks
pre-commit run --all-files
```

## 🔒 Security Features

- JWT-based authentication
- Role-based access control
- Password validation
- CORS configuration
- SQL injection protection (MongoDB)
- XSS protection headers
- Rate limiting ready

## 📈 Monitoring & Analytics

- Health check endpoints
- User activity tracking
- Content usage analytics
- Performance monitoring ready
- Error tracking with Sentry (configurable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure code quality checks pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using Django, DRF, and MongoDB**