from rest_framework import serializers
from .models import ScrapingJob
from projects.serializers import SourcePlatformSerializer


class ScrapingJobSerializer(serializers.ModelSerializer):
    platform = SourcePlatformSerializer(read_only=True)
    platform_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ScrapingJob
        fields = '__all__'
        read_only_fields = ['created_at']
