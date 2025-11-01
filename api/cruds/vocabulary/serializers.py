"""
Serializers for Vocabulary App Models
"""
from rest_framework import serializers
from django.utils import timezone

from apps.vocabulary.models import (
    Language, Book, Chapter, DifficultyLevel, Word, 
    WordTranslation, WordDefinition, Collection, CollectionWord
)


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for Language model"""
    total_words = serializers.SerializerMethodField()
    active_books = serializers.SerializerMethodField()
    
    class Meta:
        model = Language
        fields = [
            'id', 'name', 'native_name', 'code', 'flag_emoji',
            'is_rtl', 'is_active', 'created_at', 'updated_at',
            'total_words', 'active_books'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_words', 'active_books']
    
    def get_total_words(self, obj):
        """Get total words count for this language"""
        return obj.words.count()
    
    def get_active_books(self, obj):
        """Get active books count for this language"""
        return obj.books.count()


class DifficultyLevelSerializer(serializers.ModelSerializer):
    """Serializer for DifficultyLevel model"""
    total_words = serializers.SerializerMethodField()
    
    class Meta:
        model = DifficultyLevel
        fields = [
            'id', 'level', 'cefr_level', 'numeric_level', 'description',
            'color_hex', 'created_at', 'updated_at', 'total_words'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_words']
    
    def get_total_words(self, obj):
        """Get total words count for this difficulty level"""
        return obj.words.count()


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model"""
    language_name = serializers.CharField(source='language.name', read_only=True)
    total_chapters = serializers.SerializerMethodField()
    total_words = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'isbn',
            'publisher', 'publication_year', 'cover_image',
            'language', 'language_name', 'created_at', 'updated_at',
            'total_chapters', 'total_words'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_chapters', 'total_words']
    
    def get_total_chapters(self, obj):
        """Get total chapters count for this book"""
        return obj.chapters.count()
    
    def get_total_words(self, obj):
        """Get total words count for this book"""
        return obj.words.count()


class ChapterSerializer(serializers.ModelSerializer):
    """Serializer for Chapter model"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    language_name = serializers.CharField(source='book.language.name', read_only=True)
    total_words = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'description', 'chapter_number',
            'book', 'book_title', 'language_name',
            'created_at', 'updated_at', 'total_words'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_words']
    
    def get_total_words(self, obj):
        """Get total words count for this chapter"""
        return obj.words.count()


class WordTranslationSerializer(serializers.ModelSerializer):
    """Serializer for WordTranslation model"""
    language_name = serializers.CharField(source='language.name', read_only=True)
    word_text = serializers.CharField(source='word.word', read_only=True)
    
    class Meta:
        model = WordTranslation
        fields = [
            'id', 'translation', 'word', 'word_text',
            'language', 'language_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WordDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for WordDefinition model"""
    language_name = serializers.CharField(source='language.name', read_only=True)
    word_text = serializers.CharField(source='word.word', read_only=True)
    
    class Meta:
        model = WordDefinition
        fields = [
            'id', 'definition', 'example_sentence', 'word', 'word_text',
            'language', 'language_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WordSerializer(serializers.ModelSerializer):
    """Serializer for Word model with nested relationships"""
    language_name = serializers.CharField(source='language.name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    difficulty_level_name = serializers.CharField(source='difficulty_level.level', read_only=True)
    difficulty_cefr = serializers.CharField(source='difficulty_level.cefr_level', read_only=True)
    
    # Nested relationships
    translations = WordTranslationSerializer(many=True, read_only=True)
    definitions = WordDefinitionSerializer(many=True, read_only=True)
    
    # User progress for this word (if applicable)
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Word
        fields = [
            'id', 'word', 'pronunciation', 'part_of_speech',
            'frequency_rank', 'context_sentence', 'etymology',
            'language', 'language_name', 'book', 'book_title',
            'chapter', 'chapter_title', 'difficulty_level',
            'difficulty_level_name', 'difficulty_cefr',
            'created_at', 'updated_at',
            'translations', 'definitions', 'user_progress'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_progress']
    
    def get_user_progress(self, obj):
        """Get user progress for this word if user is authenticated"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                from apps.progress.models import UserProgress
                progress = UserProgress.objects.get(user=request.user, word=obj)
                return {
                    'status': progress.status,
                    'times_correct': progress.times_correct,
                    'times_reviewed': progress.times_reviewed,
                    'last_reviewed': progress.last_reviewed,
                    'next_review': progress.next_review,
                    'ease_factor': progress.ease_factor,
                    'interval_days': progress.interval_days
                }
            except:
                return None
        return None
    
    def validate(self, data):
        """Validate word data"""
        # Ensure book and chapter are consistent
        if data.get('book') and data.get('chapter'):
            if data['chapter'].book != data['book']:
                raise serializers.ValidationError(
                    "Chapter must belong to the specified book"
                )
        
        # Ensure language consistency
        if data.get('book') and data.get('language'):
            if data['book'].language != data['language']:
                raise serializers.ValidationError(
                    "Word language must match book language"
                )
        
        return data


class CollectionWordSerializer(serializers.ModelSerializer):
    """Serializer for CollectionWord model"""
    word_text = serializers.CharField(source='word.word', read_only=True)
    word_language = serializers.CharField(source='word.language.name', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    
    class Meta:
        model = CollectionWord
        fields = [
            'id', 'collection', 'collection_name', 'word', 'word_text',
            'word_language', 'added_at', 'notes'
        ]
        read_only_fields = ['id', 'added_at']


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer for Collection model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    words_count = serializers.SerializerMethodField()
    collection_words = CollectionWordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'description', 'is_public', 'tags',
            'user', 'user_username', 'created_at', 'updated_at',
            'words_count', 'collection_words'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'words_count']
    
    def get_words_count(self, obj):
        """Get total words count in this collection"""
        return obj.collection_words.count()
    
    def validate_name(self, value):
        """Ensure collection name is unique for user"""
        user = self.context['request'].user
        if Collection.objects.filter(user=user, name=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                "You already have a collection with this name"
            )
        return value