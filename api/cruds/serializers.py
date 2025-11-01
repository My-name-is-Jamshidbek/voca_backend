"""
CRUD API Serializers for Vocabulary and Progress Models
"""
from rest_framework import serializers
from apps.vocabulary.models import (
    Language, Book, Chapter, DifficultyLevel, Word, 
    WordTranslation, WordDefinition, Collection, CollectionWord
)
from apps.progress.models import UserProgress, UserSession
from apps.versioning.models import AppVersion
from apps.accounts.models import UserDevice


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for Language model"""
    
    class Meta:
        model = Language
        fields = ['id', 'code', 'name', 'native_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class DifficultyLevelSerializer(serializers.ModelSerializer):
    """Serializer for DifficultyLevel model"""
    
    class Meta:
        model = DifficultyLevel
        fields = ['id', 'level', 'numeric_level', 'description', 'cefr_level']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model"""
    language_name = serializers.CharField(source='language.name', read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'publication_year', 'publisher',
            'language', 'language_name', 'total_chapters', 'description',
            'cover_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChapterSerializer(serializers.ModelSerializer):
    """Serializer for Chapter model"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = Chapter
        fields = [
            'id', 'book', 'book_title', 'chapter_number', 'title',
            'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WordSerializer(serializers.ModelSerializer):
    """Serializer for Word model"""
    language_name = serializers.CharField(source='language.name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    difficulty_level_name = serializers.CharField(source='difficulty_level.level', read_only=True)
    
    class Meta:
        model = Word
        fields = [
            'id', 'word', 'language', 'language_name', 'book', 'book_title',
            'chapter', 'chapter_title', 'difficulty_level', 'difficulty_level_name',
            'pronunciation', 'part_of_speech', 'context_sentence', 'page_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WordTranslationSerializer(serializers.ModelSerializer):
    """Serializer for WordTranslation model"""
    word_text = serializers.CharField(source='word.word', read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    
    class Meta:
        model = WordTranslation
        fields = [
            'id', 'word', 'word_text', 'language', 'language_name',
            'translation', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WordDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for WordDefinition model"""
    word_text = serializers.CharField(source='word.word', read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    
    class Meta:
        model = WordDefinition
        fields = [
            'id', 'word', 'word_text', 'definition', 'example_sentence',
            'language', 'language_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserProgress model"""
    word_text = serializers.CharField(source='word.word', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    accuracy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'user_email', 'word', 'word_text', 'status',
            'times_reviewed', 'times_correct', 'accuracy_rate',
            'last_reviewed', 'next_review', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'user_email', 'session_date', 'words_learned',
            'words_reviewed', 'total_time_minutes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class CollectionWordSerializer(serializers.ModelSerializer):
    """Serializer for CollectionWord model"""
    word_text = serializers.CharField(source='word.word', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    
    class Meta:
        model = CollectionWord
        fields = [
            'id', 'collection', 'collection_name', 'word', 'word_text', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer for Collection model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    words_count = serializers.IntegerField(source='collection_words.count', read_only=True)
    words = WordSerializer(source='collection_words.word', many=True, read_only=True)
    
    class Meta:
        model = Collection
        fields = [
            'id', 'user', 'user_email', 'name', 'description', 'is_public',
            'words_count', 'words', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AppVersionSerializer(serializers.ModelSerializer):
    """Serializer for AppVersion model"""
    
    class Meta:
        model = AppVersion
        fields = [
            'id', 'platform', 'version_number', 'build_number', 'release_notes',
            'is_mandatory', 'min_supported_version', 'released_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserDeviceSerializer(serializers.ModelSerializer):
    """Serializer for UserDevice model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserDevice
        fields = [
            'id', 'user', 'user_email', 'device_id', 'platform', 'app_version',
            'device_model', 'os_version', 'last_sync', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']