"""
API Documentation Views
OpenAPI schema, Swagger UI, and ReDoc endpoints
"""

from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse
import logging

from ..common import ResponseMixin, success_response

logger = logging.getLogger(__name__)


class APISchemaView(APIView, ResponseMixin):
    """
    API Schema endpoint - provides OpenAPI/Swagger schema
    """
    permission_classes = []
    
    def get(self, request):
        """Return API schema information"""
        
        schema_info = {
            "openapi": "3.0.0",
            "info": {
                "title": "Voca Backend API",
                "description": "Comprehensive vocabulary learning platform API with role-based access control",
                "version": "1.0.0",
                "contact": {
                    "name": "Voca API Support",
                    "email": "support@voca.app"
                },
                "license": {
                    "name": "MIT License"
                }
            },
            "servers": [
                {
                    "url": request.build_absolute_uri('/api/'),
                    "description": "Development server"
                }
            ],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    },
                    "tokenAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "description": "Mobile app or API client token"
                    }
                }
            },
            "security": [
                {"bearerAuth": []},
                {"tokenAuth": []}
            ],
            "paths": self.get_api_paths(request),
            "tags": self.get_api_tags()
        }
        
        return success_response(
            data=schema_info,
            message="API schema retrieved successfully"
        )
    
    def get_api_paths(self, request):
        """Get available API paths"""
        base_url = request.build_absolute_uri('/api/')
        
        paths = {
            "/base/": {
                "get": {
                    "summary": "Base API root",
                    "tags": ["Base"],
                    "responses": {
                        "200": {"description": "API information"}
                    }
                }
            },
            "/base/auth/login/": {
                "post": {
                    "summary": "User login",
                    "tags": ["Authentication"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string"},
                                        "device_id": {"type": "string"},
                                        "platform": {"type": "string", "enum": ["ios", "android", "web", "desktop"]}
                                    },
                                    "required": ["email", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Login successful"},
                        "401": {"description": "Invalid credentials"}
                    }
                }
            },
            "/base/auth/register/": {
                "post": {
                    "summary": "User registration",
                    "tags": ["Authentication"],
                    "responses": {
                        "201": {"description": "Registration successful"},
                        "400": {"description": "Validation error"}
                    }
                }
            },
            "/base/health/": {
                "get": {
                    "summary": "Health check",
                    "tags": ["Health"],
                    "responses": {
                        "200": {"description": "Service healthy"},
                        "503": {"description": "Service unhealthy"}
                    }
                }
            },
            "/user/dashboard/": {
                "get": {
                    "summary": "User dashboard",
                    "tags": ["User"],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Dashboard data"},
                        "401": {"description": "Authentication required"}
                    }
                }
            },
            "/staff/dashboard/": {
                "get": {
                    "summary": "Staff dashboard",
                    "tags": ["Staff"],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Staff dashboard data"},
                        "403": {"description": "Staff permission required"}
                    }
                }
            },
            "/admin/dashboard/": {
                "get": {
                    "summary": "Admin dashboard",
                    "tags": ["Admin"],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Admin dashboard data"},
                        "403": {"description": "Admin permission required"}
                    }
                }
            }
        }
        
        return paths
    
    def get_api_tags(self):
        """Get API tags for organization"""
        return [
            {"name": "Base", "description": "Base API endpoints"},
            {"name": "Authentication", "description": "Authentication and user management"},
            {"name": "Health", "description": "Health checks and system status"},
            {"name": "User", "description": "User role endpoints"},
            {"name": "Staff", "description": "Staff role endpoints"},
            {"name": "Admin", "description": "Administrator endpoints"},
            {"name": "CRUD", "description": "CRUD operations for all models"}
        ]


class APIDocumentationView(APIView, ResponseMixin):
    """
    API Documentation endpoint - provides comprehensive API documentation
    """
    permission_classes = []
    
    def get(self, request):
        """Return API documentation"""
        
        documentation = {
            "title": "Voca Backend API Documentation",
            "description": "Comprehensive guide to the Voca vocabulary learning platform API",
            "version": "1.0.0",
            "base_url": request.build_absolute_uri('/api/'),
            "authentication": {
                "jwt": {
                    "description": "JSON Web Token authentication for regular users",
                    "header": "Authorization: Bearer <jwt_token>",
                    "endpoints": ["/base/auth/login/", "/base/auth/refresh/"]
                },
                "token": {
                    "description": "Token-based authentication for mobile apps and API clients",
                    "header": "Authorization: Bearer <mobile_or_api_token>",
                    "types": ["Mobile App Token", "API Client Token"]
                }
            },
            "roles": {
                "user": {
                    "description": "Regular users with access to learning features",
                    "permissions": ["View own data", "Manage vocabulary", "Track progress"]
                },
                "staff": {
                    "description": "Staff members with user management and content oversight",
                    "permissions": ["All user permissions", "User management", "Content management", "Analytics"]
                },
                "admin": {
                    "description": "Administrators with full system access",
                    "permissions": ["All staff permissions", "System administration", "Token management", "Advanced analytics"]
                }
            },
            "endpoints": {
                "base": {
                    "description": "Core API endpoints including authentication and health checks",
                    "path": "/base/",
                    "modules": ["authentication", "health", "documentation"]
                },
                "user": {
                    "description": "User-specific endpoints for learning and progress tracking",
                    "path": "/user/",
                    "features": ["Dashboard", "Vocabulary", "Progress", "Reviews"]
                },
                "staff": {
                    "description": "Staff endpoints for user and content management",
                    "path": "/staff/",
                    "features": ["User management", "Content oversight", "Analytics"]
                },
                "admin": {
                    "description": "Administrator endpoints for system management",
                    "path": "/admin/",
                    "features": ["System administration", "Token management", "Advanced analytics"]
                },
                "cruds": {
                    "description": "CRUD operations for all data models",
                    "path": "/cruds/",
                    "features": ["Model-based operations", "Token permissions", "Filtering", "Search"]
                }
            },
            "response_format": {
                "success": {
                    "success": True,
                    "message": "Success message",
                    "data": "Response data",
                    "timestamp": "ISO timestamp"
                },
                "error": {
                    "success": False,
                    "error": True,
                    "message": "Error message",
                    "details": "Error details",
                    "timestamp": "ISO timestamp"
                }
            },
            "rate_limits": {
                "user": "1000 requests/hour",
                "staff": "2000 requests/hour",
                "admin": "5000 requests/hour",
                "api_client": "Configurable per token"
            },
            "examples": self.get_api_examples(request)
        }
        
        return success_response(
            data=documentation,
            message="API documentation retrieved successfully"
        )
    
    def get_api_examples(self, request):
        """Get API usage examples"""
        base_url = request.build_absolute_uri('/api/')
        
        return {
            "authentication": {
                "login": {
                    "request": {
                        "method": "POST",
                        "url": f"{base_url}base/auth/login/",
                        "headers": {"Content-Type": "application/json"},
                        "body": {
                            "email": "user@example.com",
                            "password": "password123"
                        }
                    },
                    "response": {
                        "success": True,
                        "data": {
                            "tokens": {
                                "access": "jwt_access_token",
                                "refresh": "jwt_refresh_token"
                            },
                            "user": {
                                "id": "user_id",
                                "email": "user@example.com",
                                "is_staff": False
                            }
                        }
                    }
                }
            },
            "user_dashboard": {
                "request": {
                    "method": "GET",
                    "url": f"{base_url}user/dashboard/",
                    "headers": {"Authorization": "Bearer <access_token>"}
                },
                "response": {
                    "success": True,
                    "data": {
                        "user_stats": {
                            "total_words_learned": 150,
                            "words_mastered": 45,
                            "learning_streak_days": 7
                        }
                    }
                }
            }
        }


class SwaggerUIView(APIView):
    """
    Swagger UI endpoint - serves interactive API documentation
    """
    permission_classes = []
    
    def get(self, request):
        """Return Swagger UI HTML"""
        schema_url = request.build_absolute_uri('/api/base/docs/schema/')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Voca API Documentation</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
            <style>
                html {{
                    box-sizing: border-box;
                    overflow: -moz-scrollbars-vertical;
                    overflow-y: scroll;
                }}
                *, *:before, *:after {{
                    box-sizing: inherit;
                }}
                body {{
                    margin:0;
                    background: #fafafa;
                }}
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {{
                    const ui = SwaggerUIBundle({{
                        url: '{schema_url}',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout"
                    }});
                }};
            </script>
        </body>
        </html>
        """
        
        from django.http import HttpResponse
        return HttpResponse(html_content, content_type='text/html')


class ReDocView(APIView):
    """
    ReDoc endpoint - serves alternative API documentation
    """
    permission_classes = []
    
    def get(self, request):
        """Return ReDoc HTML"""
        schema_url = request.build_absolute_uri('/api/base/docs/schema/')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Voca API Documentation</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                }}
            </style>
        </head>
        <body>
            <redoc spec-url='{schema_url}'></redoc>
            <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        """
        
        from django.http import HttpResponse
        return HttpResponse(html_content, content_type='text/html')