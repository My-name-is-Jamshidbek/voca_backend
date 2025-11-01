"""
Health Check Views
System health monitoring and status endpoints
"""

from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from django.db import connection
from django.conf import settings
import logging

from ..common import ResponseMixin, success_response, error_response

logger = logging.getLogger(__name__)


class HealthCheckView(APIView, ResponseMixin):
    """
    Health Check endpoint - checks the status of the application
    """
    permission_classes = []
    
    def get(self, request):
        """Perform comprehensive health check"""
        health_status = {
            "status": "healthy",
            "database": "connected",
            "debug": settings.DEBUG,
            "timestamp": timezone.now().isoformat(),
            "components": {}
        }
        
        # Database health check
        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    health_status["database"] = "connected"
                    health_status["components"]["database"] = {
                        "status": "healthy",
                        "response_time": "fast"
                    }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["database"] = "disconnected"
            health_status["status"] = "unhealthy"
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            return error_response(
                message="Service unhealthy",
                details=health_status,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Cache health check (if configured)
        try:
            from django.core.cache import cache
            cache_key = "health_check_test"
            cache.set(cache_key, "test_value", 30)
            cache_value = cache.get(cache_key)
            if cache_value == "test_value":
                health_status["components"]["cache"] = {
                    "status": "healthy"
                }
            else:
                health_status["components"]["cache"] = {
                    "status": "unhealthy",
                    "error": "Cache test failed"
                }
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unavailable",
                "error": str(e)
            }
        
        # Memory usage check (basic)
        try:
            import psutil
            memory = psutil.virtual_memory()
            health_status["components"]["memory"] = {
                "status": "healthy" if memory.percent < 90 else "warning",
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2)
            }
        except ImportError:
            health_status["components"]["memory"] = {
                "status": "unavailable",
                "error": "psutil not installed"
            }
        except Exception as e:
            health_status["components"]["memory"] = {
                "status": "error",
                "error": str(e)
            }
        
        return success_response(data=health_status, message="Service is healthy")


class SystemStatusView(APIView, ResponseMixin):
    """
    System Status endpoint - detailed system information
    """
    permission_classes = []
    
    def get(self, request):
        """Get detailed system status"""
        
        system_info = {
            "application": {
                "name": "Voca Backend API",
                "version": "1.0.0",
                "environment": "development" if settings.DEBUG else "production",
                "debug_mode": settings.DEBUG,
            },
            "database": self.get_database_info(),
            "api_endpoints": self.get_api_endpoints(request),
            "timestamp": timezone.now().isoformat()
        }
        
        return success_response(
            data=system_info, 
            message="System status retrieved successfully"
        )
    
    def get_database_info(self):
        """Get database connection information"""
        try:
            from django.db import connections
            default_db = connections['default']
            return {
                "engine": default_db.settings_dict.get('ENGINE', 'Unknown'),
                "name": default_db.settings_dict.get('NAME', 'Unknown'),
                "host": default_db.settings_dict.get('HOST', 'localhost'),
                "port": default_db.settings_dict.get('PORT', 'default'),
                "connected": True
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    def get_api_endpoints(self, request):
        """Get available API endpoints"""
        base_url = request.build_absolute_uri().replace('/health/status/', '')
        
        return {
            "base_apis": f"{base_url}/",
            "authentication": f"{base_url}/auth/",
            "health_check": f"{base_url}/health/",
            "system_status": f"{base_url}/health/status/",
            "documentation": f"{base_url}/docs/",
            "api_schema": f"{base_url}/schema/",
        }


class ReadinessView(APIView, ResponseMixin):
    """
    Readiness Check endpoint - checks if the service is ready to handle requests
    """
    permission_classes = []
    
    def get(self, request):
        """Check if service is ready"""
        readiness_checks = {
            "database": self.check_database_readiness(),
            "migrations": self.check_migrations(),
            "dependencies": self.check_dependencies(),
        }
        
        all_ready = all(check["ready"] for check in readiness_checks.values())
        
        readiness_status = {
            "ready": all_ready,
            "checks": readiness_checks,
            "timestamp": timezone.now().isoformat()
        }
        
        if all_ready:
            return success_response(
                data=readiness_status,
                message="Service is ready"
            )
        else:
            return error_response(
                message="Service is not ready",
                details=readiness_status,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def check_database_readiness(self):
        """Check if database is ready"""
        try:
            connection.ensure_connection()
            return {"ready": True, "message": "Database connection successful"}
        except Exception as e:
            return {"ready": False, "message": f"Database connection failed: {e}"}
    
    def check_migrations(self):
        """Check if migrations are up to date"""
        try:
            from django.core.management import execute_from_command_line
            from django.db.migrations.executor import MigrationExecutor
            
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                return {"ready": False, "message": "Pending migrations found"}
            else:
                return {"ready": True, "message": "All migrations applied"}
        except Exception as e:
            return {"ready": False, "message": f"Migration check failed: {e}"}
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        dependencies = []
        
        try:
            import rest_framework
            dependencies.append({"name": "djangorestframework", "status": "available"})
        except ImportError:
            dependencies.append({"name": "djangorestframework", "status": "missing"})
        
        try:
            import rest_framework_simplejwt
            dependencies.append({"name": "djangorestframework-simplejwt", "status": "available"})
        except ImportError:
            dependencies.append({"name": "djangorestframework-simplejwt", "status": "missing"})
        
        try:
            import djongo
            dependencies.append({"name": "djongo", "status": "available"})
        except ImportError:
            dependencies.append({"name": "djongo", "status": "missing"})
        
        missing_deps = [dep for dep in dependencies if dep["status"] == "missing"]
        
        if missing_deps:
            return {
                "ready": False, 
                "message": f"Missing dependencies: {[dep['name'] for dep in missing_deps]}",
                "dependencies": dependencies
            }
        else:
            return {
                "ready": True, 
                "message": "All dependencies available",
                "dependencies": dependencies
            }


class LivenessView(APIView, ResponseMixin):
    """
    Liveness Check endpoint - simple check to verify the service is alive
    """
    permission_classes = []
    
    def get(self, request):
        """Simple liveness check"""
        return success_response(
            data={
                "alive": True,
                "timestamp": timezone.now().isoformat()
            },
            message="Service is alive"
        )