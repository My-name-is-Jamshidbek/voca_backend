"""
Base ViewSet and Mixins for CRUD APIs
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from apps.tokens.models import APIClientToken, TokenModelPermission
from ...base import success_response, error_response
import logging

logger = logging.getLogger(__name__)


class TokenPermissionMixin:
    """
    Mixin to handle token-based permissions for model access
    """
    
    def check_token_permission(self, request, action):
        """Check if token has permission for the action on this model"""
        # If user is authenticated via session, allow access
        if hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
            return True
        
        # Check token permissions
        if hasattr(request, 'token_data') and request.token_data.get('token_type') == 'api':
            model_name = self.queryset.model.__name__
            
            try:
                token = APIClientToken.objects.get(id=request.token_data['token_id'])
                permission = token.model_permissions.filter(model_name=model_name).first()
                
                if not permission:
                    return False
                
                # Check specific permission based on action
                if action == 'list' and not permission.can_list:
                    return False
                elif action == 'retrieve' and not permission.can_read:
                    return False
                elif action == 'create' and not permission.can_create:
                    return False
                elif action in ['update', 'partial_update'] and not permission.can_update:
                    return False
                elif action == 'destroy' and not permission.can_delete:
                    return False
                
                return True
            except APIClientToken.DoesNotExist:
                return False
        
        return False
    
    def get_serializer(self, *args, **kwargs):
        """Override to filter fields based on token permissions"""
        serializer = super().get_serializer(*args, **kwargs)
        
        # Filter fields based on token permissions
        if hasattr(self.request, 'token_permissions'):
            permission = self.request.token_permissions
            
            # Remove restricted fields
            if permission.restricted_fields:
                for field in permission.restricted_fields:
                    if field in serializer.fields:
                        del serializer.fields[field]
            
            # Make fields read-only
            if permission.readonly_fields:
                for field in permission.readonly_fields:
                    if field in serializer.fields:
                        serializer.fields[field].read_only = True
        
        return serializer


class BaseModelViewSet(TokenPermissionMixin, viewsets.ModelViewSet):
    """
    Base ViewSet with common functionality and token permissions
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    def create(self, request, *args, **kwargs):
        """Override create to return standardized response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return success_response(
            data=serializer.data,
            message=f"{self.get_serializer().Meta.model.__name__} created successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Override update to return standardized response"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return success_response(
            data=serializer.data,
            message=f"{self.get_serializer().Meta.model.__name__} updated successfully"
        )
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to return standardized response"""
        instance = self.get_object()
        model_name = self.get_serializer().Meta.model.__name__
        self.perform_destroy(instance)
        
        return success_response(
            message=f"{model_name} deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    def list(self, request, *args, **kwargs):
        """Override list to return standardized response"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message=f"{self.get_serializer().Meta.model.__name__} list retrieved successfully"
        )