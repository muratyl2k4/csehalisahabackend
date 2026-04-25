from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    photo = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'photo', 'author_name', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
