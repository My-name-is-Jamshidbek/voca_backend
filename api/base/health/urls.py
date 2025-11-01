"""
Health module URLs
Health checks, system status, readiness and liveness probes
"""

from django.urls import path
from .views import (
    HealthCheckView,
    SystemStatusView,
    ReadinessView,
    LivenessView,
)

app_name = 'health'

urlpatterns = [
    # Main health check endpoint
    path('', HealthCheckView.as_view(), name='health-check'),
    
    # Detailed system status
    path('status/', SystemStatusView.as_view(), name='system-status'),
    
    # Kubernetes/Docker health probes
    path('readiness/', ReadinessView.as_view(), name='readiness-probe'),
    path('liveness/', LivenessView.as_view(), name='liveness-probe'),
    
    # Alternative endpoint names for compatibility
    path('check/', HealthCheckView.as_view(), name='health-check-alt'),
    path('alive/', LivenessView.as_view(), name='alive-check'),
    path('ready/', ReadinessView.as_view(), name='ready-check'),
]