"""
Analytics module for User APIs
Contains serializers for analytics endpoints
"""

from rest_framework import serializers


class UserSessionSerializer(serializers.Serializer):
    """Serializer for user sessions in analytics"""
    id = serializers.CharField()
    session_date = serializers.DateField()
    duration_minutes = serializers.IntegerField()
    words_reviewed = serializers.IntegerField()
    accuracy_percentage = serializers.FloatField()
