from django.db import models
from django.contrib.auth import get_user_model
from projects.models import ProjectLead

User = get_user_model()


class OutreachTemplate(models.Model):
    """Email templates for outreach."""
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'outreach_templates'

    def __str__(self):
        return self.name


class OutreachMessage(models.Model):
    """Tracks outreach messages sent to prospects."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('responded', 'Responded'),
        ('bounced', 'Bounced'),
    ]

    project = models.ForeignKey(ProjectLead, on_delete=models.CASCADE, related_name='outreach_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outreach_messages')
    template = models.ForeignKey(OutreachTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    subject = models.CharField(max_length=500)
    body = models.TextField()
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=200, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(blank=True, null=True)
    opened_at = models.DateTimeField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    response_text = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'outreach_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.title} - {self.recipient_email}"
