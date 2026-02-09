# Generated manually - Initial migration for projects app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SourcePlatform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('url', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
                ('user_count', models.IntegerField(default=0, help_text='Approximate user count')),
                ('scraping_method', models.CharField(choices=[('public_api', 'Public API'), ('rss_feed', 'RSS Feed'), ('public_scrape', 'Public Scraping'), ('manual', 'Manual Entry')], default='manual', max_length=50)),
                ('rate_limit_per_minute', models.IntegerField(default=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'source_platforms',
            },
        ),
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True)),
                ('value', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'system_settings',
                'verbose_name': 'System Setting',
                'verbose_name_plural': 'System Settings',
            },
        ),
        migrations.CreateModel(
            name='ProjectLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('description', models.TextField()),
                ('source_url', models.URLField(unique=True)),
                ('source_id', models.CharField(blank=True, max_length=200, null=True)),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('contact_name', models.CharField(blank=True, max_length=200, null=True)),
                ('contact_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('company_name', models.CharField(blank=True, max_length=200, null=True)),
                ('budget_min', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('budget_max', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('budget_currency', models.CharField(default='USD', max_length=3)),
                ('skills_required', models.JSONField(blank=True, default=list)),
                ('project_type', models.CharField(blank=True, max_length=100, null=True)),
                ('relevance_score', models.FloatField(default=0.0, help_text='AI-generated relevance score (0-1)', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('quality_score', models.FloatField(default=0.0, help_text='AI-generated quality score (0-1)', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('status', models.CharField(choices=[('new', 'New'), ('qualified', 'Qualified'), ('contacted', 'Contacted'), ('responded', 'Responded'), ('matched', 'Matched'), ('closed', 'Closed'), ('rejected', 'Rejected')], default='new', max_length=20)),
                ('is_public', models.BooleanField(default=True, help_text='Whether this project is visible to non-authenticated users')),
                ('scraped_at', models.DateTimeField(auto_now_add=True)),
                ('qualified_at', models.DateTimeField(blank=True, null=True)),
                ('contacted_at', models.DateTimeField(blank=True, null=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('matched_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matched_projects', to=settings.AUTH_USER_MODEL)),
                ('source_platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='projects.sourceplatform')),
            ],
            options={
                'db_table': 'project_leads',
            },
        ),
        migrations.CreateModel(
            name='ProjectMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_score', models.FloatField(default=0.0, help_text='Compatibility score between project and user', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('is_selected', models.BooleanField(default=False, help_text='User selected for this project')),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='projects.projectlead')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_matches', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'project_matches',
                'unique_together': {('project', 'user')},
            },
        ),
        migrations.CreateModel(
            name='ProjectApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicant_name', models.CharField(max_length=200)),
                ('applicant_email', models.EmailField(max_length=254)),
                ('applicant_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('applicant_portfolio', models.URLField(blank=True, null=True)),
                ('applicant_skills', models.JSONField(blank=True, default=list)),
                ('cover_letter', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('contacted', 'Contacted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('notes', models.TextField(blank=True, help_text='Internal notes about this application', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='projects.projectlead')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'project_applications',
            },
        ),
        migrations.AddIndex(
            model_name='projectlead',
            index=models.Index(fields=['status', 'relevance_score'], name='project_lea_status_123abc_idx'),
        ),
        migrations.AddIndex(
            model_name='projectlead',
            index=models.Index(fields=['source_platform', 'scraped_at'], name='project_lea_source__123abc_idx'),
        ),
        migrations.AddIndex(
            model_name='projectlead',
            index=models.Index(fields=['is_public', 'status'], name='project_lea_is_publ_123abc_idx'),
        ),
        migrations.AddIndex(
            model_name='projectmatch',
            index=models.Index(fields=['user', 'match_score'], name='project_mat_user_id_123abc_idx'),
        ),
        migrations.AddIndex(
            model_name='projectapplication',
            index=models.Index(fields=['project', 'status'], name='project_app_project_123abc_idx'),
        ),
        migrations.AddIndex(
            model_name='projectapplication',
            index=models.Index(fields=['applicant_email', 'created_at'], name='project_app_applica_123abc_idx'),
        ),
    ]
