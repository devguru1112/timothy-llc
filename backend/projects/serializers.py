from rest_framework import serializers
from .models import ProjectLead, SourcePlatform, ProjectMatch
from users.serializers import UserSerializer


class SourcePlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcePlatform
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectLeadSerializer(serializers.ModelSerializer):
    source_platform_name = serializers.CharField(source='source_platform.name', read_only=True)
    matched_user_username = serializers.CharField(source='matched_user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ProjectLead
        fields = '__all__'
        read_only_fields = ['scraped_at', 'created_at', 'updated_at']


class ProjectMatchSerializer(serializers.ModelSerializer):
    project = ProjectLeadSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectMatch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectLeadListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    source_platform_name = serializers.CharField(source='source_platform.name', read_only=True)
    matched_user_username = serializers.CharField(source='matched_user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ProjectLead
        fields = [
            'id', 'title', 'description', 'source_platform_name', 'source_url',
            'contact_email', 'contact_name', 'company_name', 'budget_min', 
            'budget_max', 'budget_currency', 'skills_required', 'relevance_score',
            'quality_score', 'status', 'matched_user_username', 'scraped_at',
            'created_at'
        ]
