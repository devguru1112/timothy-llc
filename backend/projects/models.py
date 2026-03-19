from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class JobCategory(models.Model):
    """Categories for job classification (e.g., SEO, Marketing, Social Media)."""
    name = models.CharField(max_length=100, unique=True)
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="List of keywords to match jobs to this category (e.g., ['SEO', 'search engine optimization', 'keyword research'])"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_categories'
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


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


class ScrapingConfig(models.Model):
    """Configuration for scraping jobs - stores selected categories."""
    name = models.CharField(
        max_length=200,
        default="Default Scraping Config",
        help_text="Name for this scraping configuration"
    )
    categories = models.ManyToManyField(
        JobCategory,
        related_name='scraping_configs',
        help_text="Categories to scrape jobs for"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this configuration is active for scraping"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_scraping_configs'
    )

    class Meta:
        db_table = 'scraping_configs'
        verbose_name = 'Scraping Configuration'
        verbose_name_plural = 'Scraping Configurations'

    def __str__(self):
        return self.name


class SystemSettings(models.Model):
    """System-wide settings controlled by admin."""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='updated_settings'
    )

    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f"{self.key}: {self.value}"

    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value, returning default if not found."""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def get_int_setting(cls, key, default=0):
        """Get a setting as integer."""
        try:
            return int(cls.get_setting(key, default))
        except (ValueError, TypeError):
            return default


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
    
    # Public visibility
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this project is visible to non-authenticated users"
    )
    
    # Categories
    categories = models.ManyToManyField(
        JobCategory,
        related_name='projects',
        blank=True,
        help_text="Categories this job belongs to"
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
            models.Index(fields=['is_public', 'status']),
        ]

    def __str__(self):
        return self.title


class ProjectView(models.Model):
    """Tracks which authenticated users have viewed which project leads."""
    project = models.ForeignKey(ProjectLead, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_views'
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['user', 'viewed_at']),
        ]

    def __str__(self):
        return f"{self.user.username} viewed {self.project.title}"


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


class ProjectApplication(models.Model):
    """Applications from non-authenticated users."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('contacted', 'Contacted'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(ProjectLead, on_delete=models.CASCADE, related_name='applications')
    
    # Applicant information (no user account required)
    applicant_name = models.CharField(max_length=200)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=20, blank=True, null=True)
    applicant_portfolio = models.URLField(blank=True, null=True)
    applicant_skills = models.JSONField(default=list, blank=True)
    cover_letter = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about this application")
    
    # Optional: Link to user account if they sign up later
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_applications'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['applicant_email', 'created_at']),
        ]

    def __str__(self):
        return f"{self.applicant_name} - {self.project.title}"
