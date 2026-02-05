from django.db import models
from projects.models import SourcePlatform


class ScrapingJob(models.Model):
    """Tracks scraping jobs for different platforms."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    platform = models.ForeignKey(SourcePlatform, on_delete=models.CASCADE, related_name='scraping_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    projects_found = models.IntegerField(default=0)
    projects_added = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scraping_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.platform.name} - {self.status}"
