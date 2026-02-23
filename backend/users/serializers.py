from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_fully_verified = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'bio', 'skills', 
                  'portfolio_url', 'is_community_member', 'priority_level',
                  'phone_verified', 'email_verified', 'is_fully_verified', 'is_superuser',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'phone_verified', 'email_verified', 'is_superuser']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone', 'bio', 'skills', 'portfolio_url']
        extra_kwargs = {
            'phone': {'required': True},  # Phone is now required for verification
            'bio': {'required': False, 'allow_blank': True},
            'skills': {'required': False},
            'portfolio_url': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class PhoneVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)
    phone = serializers.CharField(max_length=20, required=False)


class EmailVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)
