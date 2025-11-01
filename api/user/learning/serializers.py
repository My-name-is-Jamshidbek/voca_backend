"""
Learning Module Serializers
Handles vocabulary learning and progress tracking for Flutter app
"""

from rest_framework import serializers
from apps.vocabulary.models import Word, WordTranslation, WordDefinition, Collection, CollectionWord, DifficultyLevel
from apps.progress.models import UserProgress, UserSession
from apps.accounts.models import Language
import logging

logger = logging.getLogger(__name__)


class DifficultyLevelSerializer(serializers.ModelSerializer):
    """
    Serializer for Difficulty Level
    
    Example:
        {
            "id": "level-1",
            "level_name": "A1",
            "description": "Beginner",
            "cefr_level": "A1",
            "order": 1
        }
    """
    
    class Meta:
        model = DifficultyLevel
        fields = ['id', 'level_name', 'description', 'cefr_level', 'order']
        read_only_fields = ['id']


class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for Language
    
    Example:
        {
            "id": "lang-1",
            "name": "English",
            "code": "en",
            "native_name": "English",
            "is_active": true,
            "flag_emoji": "🇬🇧"
        }
    """
    
    class Meta:
        model = Language
        fields = ['id', 'name', 'code', 'native_name', 'is_active', 'flag_emoji']
        read_only_fields = ['id']


class WordTranslationSerializer(serializers.ModelSerializer):
    """
    Serializer for Word Translation
    
    Example:
        {
            "id": "trans-1",
            "language": "German",
            "translation": "Hallo",
            "language_code": "de"
        }
    """
    
    language_name = serializers.CharField(source='language.name', read_only=True)
    
    class Meta:
        model = WordTranslation
        fields = ['id', 'language', 'language_name', 'translation']
        read_only_fields = ['id']


class WordDefinitionSerializer(serializers.ModelSerializer):
    """
    Serializer for Word Definition
    
    Example:
        {
            "id": "def-1",
            "definition": "A greeting expression",
            "example_sentence": "Hello, how are you?",
            "part_of_speech": "interjection"
        }
    """
    
    class Meta:
        model = WordDefinition
        fields = ['id', 'definition', 'example_sentence', 'part_of_speech']
        read_only_fields = ['id']


class WordDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Word with full details including translations and definitions
    
    Example:
        {
            "id": "word-1",
            "word": "Hello",
            "phonetic": "həˈloʊ",
            "pronunciation_url": "https://example.com/audio/hello.mp3",
            "difficulty_level": {"level_name": "A1", "cefr_level": "A1"},
            "translations": [
                {
                    "language": "de",
                    "translation": "Hallo"
                }
            ],
            "definitions": [
                {
                    "definition": "A greeting expression",
                    "example_sentence": "Hello, how are you?",
                    "part_of_speech": "interjection"
                }
            ],
            "image_url": "https://example.com/images/hello.jpg",
            "tags": "greeting,common",
            "frequency_rank": 100
        }
    """
    
    difficulty_level = DifficultyLevelSerializer(read_only=True)
    translations = WordTranslationSerializer(many=True, read_only=True, source='word_translations')
    definitions = WordDefinitionSerializer(many=True, read_only=True, source='word_definitions')
    
    class Meta:
        model = Word
        fields = [
            'id', 'word', 'phonetic', 'pronunciation_url', 
            'difficulty_level', 'translations', 'definitions',
            'image_url', 'tags', 'frequency_rank'
        ]
        read_only_fields = ['id']


class WordListSerializer(serializers.ModelSerializer):
    """
    Serializer for Word list (simplified)
    
    Example:
        {
            "id": "word-1",
            "word": "Hello",
            "difficulty_level": "A1",
            "frequency_rank": 100,
            "image_url": "https://example.com/images/hello.jpg"
        }
    """
    
    difficulty_level_name = serializers.CharField(
        source='difficulty_level.level_name',
        read_only=True
    )
    
    class Meta:
        model = Word
        fields = [
            'id', 'word', 'phonetic', 'difficulty_level_name',
            'frequency_rank', 'image_url'
        ]
        read_only_fields = ['id']


class UserProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for User Progress (learning progress of a word)
    
    Fields:
        - id: Progress record ID
        - word: Word details (nested WordDetailSerializer)
        - mastery_level: Learning level (0-5, 0=not started, 5=mastered)
        - times_reviewed: Number of times reviewed
        - correct_answers: Number of correct reviews
        - incorrect_answers: Number of incorrect reviews
        - last_reviewed: Last review timestamp
        - next_review_date: Next scheduled review date
        - first_learned_date: Date when first learned
        - accuracy_percentage: Overall accuracy (0-100)
    
    Example:
        {
            "id": "prog-1",
            "word": {
                "id": "word-1",
                "word": "Hello",
                "difficulty_level": "A1"
            },
            "mastery_level": 2,
            "times_reviewed": 5,
            "correct_answers": 4,
            "incorrect_answers": 1,
            "last_reviewed": "2024-11-01T10:30:00Z",
            "next_review_date": "2024-11-02T10:30:00Z",
            "first_learned_date": "2024-10-20T14:15:00Z",
            "accuracy_percentage": 80.0
        }
    """
    
    word = WordDetailSerializer(read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'word', 'mastery_level', 'times_reviewed',
            'correct_answers', 'incorrect_answers', 'last_reviewed',
            'next_review_date', 'first_learned_date', 'accuracy_percentage'
        ]
        read_only_fields = ['id', 'times_reviewed', 'last_reviewed', 'accuracy_percentage']


class UserProgressUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Updating User Progress
    
    Fields:
        - is_correct: Whether the review answer was correct
        - review_notes: Additional notes about the review
    
    Example:
        {
            "is_correct": true,
            "review_notes": "Easy to remember"
        }
    """
    
    is_correct = serializers.BooleanField(required=True)
    review_notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = UserProgress
        fields = ['is_correct', 'review_notes']


class CollectionWordSerializer(serializers.ModelSerializer):
    """
    Serializer for Word in Collection
    
    Example:
        {
            "id": "cw-1",
            "word": {
                "id": "word-1",
                "word": "Hello",
                "difficulty_level": "A1"
            },
            "added_date": "2024-10-20T14:15:00Z"
        }
    """
    
    word = WordListSerializer(read_only=True)
    
    class Meta:
        model = CollectionWord
        fields = ['id', 'word', 'added_date']
        read_only_fields = ['id', 'added_date']


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Collection (user's custom word collection)
    
    Fields:
        - id: Collection ID
        - name: Collection name
        - description: Collection description
        - words_count: Number of words in collection
        - created_at: Creation timestamp
        - updated_at: Last update timestamp
        - words: List of words in collection
    
    Example:
        {
            "id": "col-1",
            "name": "Daily Vocabulary",
            "description": "Words I learn daily",
            "words_count": 25,
            "created_at": "2024-10-20T14:15:00Z",
            "updated_at": "2024-11-01T15:30:00Z",
            "words": [...]
        }
    """
    
    words_count = serializers.SerializerMethodField()
    words = CollectionWordSerializer(many=True, read_only=True, source='collection_words')
    
    def get_words_count(self, obj):
        return obj.collection_words.count()
    
    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'description', 'words_count',
            'created_at', 'updated_at', 'words'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CollectionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for Creating/Updating Collection
    
    Fields:
        - name: Collection name (required, max 100 chars)
        - description: Collection description (optional, max 500 chars)
    
    Example:
        {
            "name": "Daily Vocabulary",
            "description": "Words I learn daily"
        }
    """
    
    class Meta:
        model = Collection
        fields = ['name', 'description']


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for User Session (learning session)
    
    Fields:
        - id: Session ID
        - session_date: Date of the session
        - duration_minutes: Session duration in minutes
        - words_reviewed: Number of words reviewed
        - correct_answers: Correct answers count
        - incorrect_answers: Incorrect answers count
        - words_added: New words added in this session
        - accuracy_percentage: Session accuracy percentage
    
    Example:
        {
            "id": "sess-1",
            "session_date": "2024-11-01",
            "duration_minutes": 30,
            "words_reviewed": 15,
            "correct_answers": 12,
            "incorrect_answers": 3,
            "words_added": 5,
            "accuracy_percentage": 80.0
        }
    """
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_date', 'duration_minutes', 'words_reviewed',
            'correct_answers', 'incorrect_answers', 'words_added',
            'accuracy_percentage'
        ]
        read_only_fields = ['id', 'accuracy_percentage']
