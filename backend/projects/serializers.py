from rest_framework import serializers
from .models import ProjectLead, SourcePlatform, ProjectMatch, ProjectApplication, SystemSettings
from users.serializers import UserSerializer


class SourcePlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourcePlatform
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ['updated_at']


class ProjectLeadSerializer(serializers.ModelSerializer):
    source_platform_name = serializers.CharField(source='source_platform.name', read_only=True)
    matched_user_username = serializers.CharField(source='matched_user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ProjectLead
        fields = '__all__'
        read_only_fields = ['scraped_at', 'created_at', 'updated_at']


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
            'created_at', 'is_public'
        ]


class ProjectLeadPublicSerializer(serializers.ModelSerializer):
    """Serializer for public (non-authenticated) access - limited fields."""
    source_platform_name = serializers.CharField(source='source_platform.name', read_only=True)
    
    class Meta:
        model = ProjectLead
        fields = [
            'id', 'title', 'description', 'source_platform_name', 'company_name',
            'budget_min', 'budget_max', 'budget_currency', 'skills_required',
            'project_type', 'created_at', 'is_public'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectMatchSerializer(serializers.ModelSerializer):
    project = ProjectLeadSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectMatch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectApplicationSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = ProjectApplication
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'status']


class ProjectApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating applications (no authentication required)."""
    
    class Meta:
        model = ProjectApplication
        fields = [
            'project', 'applicant_name', 'applicant_email', 'applicant_phone',
            'applicant_portfolio', 'applicant_skills', 'cover_letter'
        ]
    
    def validate_project(self, value):
        """Ensure project is public and accepting applications."""
        if not value.is_public:
            raise serializers.ValidationError("This project is not available for public applications.")
        if value.status in ['closed', 'matched', 'rejected']:
            raise serializers.ValidationError("This project is no longer accepting applications.")
        return value