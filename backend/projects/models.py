from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class SourcePlatform(models.Model):
    """Platforms where projects are sourced from."""
    name = models.CharField(max_length=200, unique=True)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    user_count = models.IntegerField(default=0, help_text="Approximate user count")
    scraping_method = models.CharField(
        max_length=50,
        choices=[
            ('public_api', 'Public API'),
            ('rss_feed', 'RSS Feed'),
            ('public_scrape', 'Public Scraping'),
            ('manual', 'Manual Entry'),
        ],
        default='manual'
    )
    rate_limit_per_minute = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'source_platforms'

    def __str__(self):
        return self.name


class ProjectLead(models.Model):
    """Individual project opportunities scraped from various sources."""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('qualified', 'Qualified'),
        ('contacted', 'Contacted'),
        ('responded', 'Responded'),
        ('matched', 'Matched'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=500)
    description = models.TextField()
    source_platform = models.ForeignKey(SourcePlatform, on_delete=models.CASCADE, related_name='projects')
    source_url = models.URLField(unique=True)
    source_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Contact information
    contact_email = models.EmailField(blank=True, null=True)
    contact_name = models.CharField(max_length=200, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Project details
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    budget_currency = models.CharField(max_length=3, default='USD')
    skills_required = models.JSONField(default=list, blank=True)
    project_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Qualification scores
    relevance_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI-generated relevance score (0-1)"
    )
    quality_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI-generated quality score (0-1)"
    )
    
    # Status and matching
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    matched_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='matched_projects'
    )
    
    # Metadata
    scraped_at = models.DateTimeField(auto_now_add=True)
    qualified_at = models.DateTimeField(blank=True, null=True)
    contacted_at = models.DateTimeField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_leads'
        indexes = [
            models.Index(fields=['status', 'relevance_score']),
            models.Index(fields=['source_platform', 'scraped_at']),
        ]

    def __str__(self):
        return self.title


class ProjectMatch(models.Model):
    """Tracks matches between projects and community members."""
    project = models.ForeignKey(ProjectLead, on_delete=models.CASCADE, related_name='matches')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_matches')
    match_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Compatibility score between project and user"
    )
    is_selected = models.BooleanField(default=False, help_text="User selected for this project")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_matches'
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['user', 'match_score']),
        ]

    def __str__(self):
        return f"{self.project.title} - {self.user.username}"
