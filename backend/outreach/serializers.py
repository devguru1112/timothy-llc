from rest_framework import serializers
from .models import OutreachTemplate, OutreachMessage
from projects.serializers import ProjectLeadListSerializer
from users.serializers import UserSerializer


class OutreachTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutreachTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class OutreachMessageSerializer(serializers.ModelSerializer):
    project = ProjectLeadListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    template = OutreachTemplateSerializer(read_only=True)
    
    class Meta:
        model = OutreachMessage
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'sent_at', 'opened_at', 'responded_at']
