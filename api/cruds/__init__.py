"""
Initialize all CRUD API modules for easy imports
"""

# Import all ViewSets for backward compatibility if needed
from .accounts.views import UserViewSet, UserDeviceViewSet
from .vocabulary.views import (
    LanguageViewSet, DifficultyLevelViewSet, BookViewSet, ChapterViewSet,
    WordViewSet, WordTranslationViewSet, WordDefinitionViewSet,
    CollectionViewSet, CollectionWordViewSet
)
from .progress.views import UserProgressViewSet, UserSessionViewSet
from .versioning.views import AppVersionViewSet
from .tokens.views import MobileAppTokenViewSet, APIClientTokenViewSet

# Import all Serializers
from .accounts.serializers import UserSerializer, UserDeviceSerializer
from .vocabulary.serializers import (
    LanguageSerializer, DifficultyLevelSerializer, BookSerializer, ChapterSerializer,
    WordSerializer, WordTranslationSerializer, WordDefinitionSerializer,
    CollectionSerializer, CollectionWordSerializer
)
from .progress.serializers import UserProgressSerializer, UserSessionSerializer
from .versioning.serializers import AppVersionSerializer
from .tokens.serializers import (
    MobileAppTokenSerializer, APIClientTokenSerializer, TokenModelPermissionSerializer
)

__all__ = [
    # ViewSets
    'UserViewSet', 'UserDeviceViewSet',
    'LanguageViewSet', 'DifficultyLevelViewSet', 'BookViewSet', 'ChapterViewSet',
    'WordViewSet', 'WordTranslationViewSet', 'WordDefinitionViewSet',
    'CollectionViewSet', 'CollectionWordViewSet',
    'UserProgressViewSet', 'UserSessionViewSet',
    'AppVersionViewSet',
    'MobileAppTokenViewSet', 'APIClientTokenViewSet',
    
    # Serializers
    'UserSerializer', 'UserDeviceSerializer',
    'LanguageSerializer', 'DifficultyLevelSerializer', 'BookSerializer', 'ChapterSerializer',
    'WordSerializer', 'WordTranslationSerializer', 'WordDefinitionSerializer',
    'CollectionSerializer', 'CollectionWordSerializer',
    'UserProgressSerializer', 'UserSessionSerializer',
    'AppVersionSerializer',
    'MobileAppTokenSerializer', 'APIClientTokenSerializer', 'TokenModelPermissionSerializer'
]
