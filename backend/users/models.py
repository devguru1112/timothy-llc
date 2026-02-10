from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string


class User(AbstractUser):
    """Custom User model with additional fields for community members."""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    portfolio_url = models.URLField(blank=True, null=True)
    is_community_member = models.BooleanField(default=True)
    priority_level = models.IntegerField(default=1, help_text="Higher number = higher priority for project matching")
    
    # Verification fields
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verification_code = models.CharField(max_length=6, blank=True, null=True)
    phone_verification_code_expires = models.DateTimeField(blank=True, null=True)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    email_verification_code_expires = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username
    
    def generate_verification_code(self, length=6):
        """Generate a random verification code."""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_phone_verification_code(self):
        """Generate and send phone verification code."""
        code = self.generate_verification_code()
        self.phone_verification_code = code
        self.phone_verification_code_expires = timezone.now() + timedelta(minutes=10)
        self.save()
        
        # Send SMS (implemented in services)
        from users.services import send_sms_verification
        send_sms_verification(self.phone, code)
        
        return code
    
    def send_email_verification_code(self):
        """Generate and send email verification code."""
        code = self.generate_verification_code()
        self.email_verification_code = code
        self.email_verification_code_expires = timezone.now() + timedelta(hours=24)
        self.save()
        
        # Send email (implemented in services)
        from users.services import send_email_verification
        send_email_verification(self.email, code)
        
        return code
    
    def verify_phone_code(self, code):
        """Verify phone verification code."""
        if not self.phone_verification_code:
            return False
        
        if timezone.now() > self.phone_verification_code_expires:
            return False
        
        if self.phone_verification_code == code:
            self.phone_verified = True
            self.phone_verification_code = None
            self.phone_verification_code_expires = None
            self.save()
            return True
        
        return False
    
    def verify_email_code(self, code):
        """Verify email verification code."""
        if not self.email_verification_code:
            return False
        
        if timezone.now() > self.email_verification_code_expires:
            return False
        
        if self.email_verification_code == code:
            self.email_verified = True
            self.email_verification_code = None
            self.email_verification_code_expires = None
            self.save()
            return True
        
        return False
    
    @property
    def is_fully_verified(self):
        """Check if both phone and email are verified."""
        return self.phone_verified and self.email_verified