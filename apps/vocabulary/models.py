"""
Vocabulary Models Based on Database Diagram
"""
from djongo import models
from django.utils import timezone
from django.conf import settings


class Language(models.Model):
    """
    Language model for multi-language support
    """
    code = models.CharField(max_length=10, unique=True)  # e.g., 'en', 'es', 'fr'
    name = models.CharField(max_length=100)  # e.g., 'English', 'Spanish'
    native_name = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'English', 'Español'
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Book(models.Model):
    """
    Book model for organizing vocabulary by books
    """
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    publication_year = models.IntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='books')
    total_chapters = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.TextField(blank=True, null=True)  # URL or base64
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author or 'Unknown'}"


class Chapter(models.Model):
    """
    Chapter model for organizing content within books
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.IntegerField()
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        ordering = ['book', 'chapter_number']
        unique_together = ['book', 'chapter_number']
    
    def __str__(self):
        return f"{self.book.title} - Chapter {self.chapter_number}: {self.title or 'Untitled'}"


class DifficultyLevel(models.Model):
    """
    Difficulty level model with CEFR alignment
    """
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('elementary', 'Elementary'),
        ('intermediate', 'Intermediate'),
        ('upper_intermediate', 'Upper Intermediate'),
        ('advanced', 'Advanced'),
        ('proficient', 'Proficient'),
    ]
    
    CEFR_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True)
    numeric_level = models.IntegerField(unique=True)  # 1-6
    description = models.TextField(blank=True, null=True)
    cefr_level = models.CharField(max_length=10, choices=CEFR_CHOICES, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Difficulty Level'
        verbose_name_plural = 'Difficulty Levels'
        ordering = ['numeric_level']
    
    def __str__(self):
        return f"{self.level} ({self.cefr_level or 'No CEFR'})"


class Word(models.Model):
    """
    Enhanced word model with book context
    """
    PART_OF_SPEECH_CHOICES = [
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('pronoun', 'Pronoun'),
        ('preposition', 'Preposition'),
        ('conjunction', 'Conjunction'),
        ('interjection', 'Interjection'),
        ('article', 'Article'),
    ]
    
    word = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='words')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='words', null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='words', null=True, blank=True)
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, related_name='words')
    pronunciation = models.TextField(blank=True, null=True)
    part_of_speech = models.CharField(max_length=50, choices=PART_OF_SPEECH_CHOICES, blank=True, null=True)
    context_sentence = models.TextField(blank=True, null=True)
    page_number = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Word'
        verbose_name_plural = 'Words'
        ordering = ['word']
        unique_together = ['word', 'language']
        indexes = [
            models.Index(fields=['word', 'language']),
            models.Index(fields=['book', 'chapter']),
        ]
    
    def __str__(self):
        return f"{self.word} ({self.language.code})"


class WordTranslation(models.Model):
    """
    Word translations for multi-language support
    """
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='word_translations')
    translation = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Word Translation'
        verbose_name_plural = 'Word Translations'
        unique_together = ['word', 'language']
    
    def __str__(self):
        return f"{self.word.word} → {self.translation} ({self.language.code})"


class WordDefinition(models.Model):
    """
    Word definitions with examples
    """
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='definitions')
    definition = models.TextField()
    example_sentence = models.TextField(blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='word_definitions')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Word Definition'
        verbose_name_plural = 'Word Definitions'
    
    def __str__(self):
        return f"{self.word.word} definition ({self.language.code})"


class Collection(models.Model):
    """
    User-created word collections
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} by {self.user.email}"


class CollectionWord(models.Model):
    """
    Many-to-many relationship between collections and words
    """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_words')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='word_collections')
    added_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Collection Word'
        verbose_name_plural = 'Collection Words'
        unique_together = ['collection', 'word']
        indexes = [
            models.Index(fields=['collection', 'word']),
        ]
    
    def __str__(self):
        return f"{self.collection.name} - {self.word.word}"