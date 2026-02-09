"""
Celery tasks for background scraping and qualification.
"""
from celery import shared_task
from django.utils import timezone
from projects.models import ProjectLead, SourcePlatform
from scrapers.models import ScrapingJob
from scrapers.scrapers import get_scraper
from scrapers.qualifiers import ProjectQualifier
import logging

logger = logging.getLogger(__name__)


@shared_task
def scrape_platform(platform_id: int, limit: int = 50):
    """Scrape projects from a specific platform."""
    try:
        platform = SourcePlatform.objects.get(id=platform_id, is_active=True)
        job = ScrapingJob.objects.create(
            platform=platform,
            status='running',
            started_at=timezone.now()
        )
        
        scraper = get_scraper(platform)
        projects = scraper.scrape(limit=limit)
        
        projects_added = 0
        for project_data in projects:
            # Check if project already exists
            if ProjectLead.objects.filter(source_url=project_data.get('source_url')).exists():
                continue
            
            # Create new project lead
            project = ProjectLead.objects.create(
                title=project_data.get('title', 'Untitled'),
                description=project_data.get('description', ''),
                source_platform=platform,
                source_url=project_data.get('source_url', ''),
                source_id=project_data.get('source_id', ''),
                contact_email=project_data.get('contact_email'),
                contact_name=project_data.get('contact_name'),
                company_name=project_data.get('company_name'),
                budget_min=project_data.get('budget_min'),
                budget_max=project_data.get('budget_max'),
                skills_required=project_data.get('skills_required', []),
            )
            
            # Qualify the project
            qualifier = ProjectQualifier()
            scores = qualifier.qualify(project)
            project.relevance_score = scores.get('relevance', 0.5)
            project.quality_score = scores.get('quality', 0.5)
            project.qualified_at = timezone.now()
            project.status = 'qualified' if scores.get('relevance', 0) > 0.5 else 'new'
            project.save()
            
            projects_added += 1
        
        job.status = 'completed'
        job.projects_found = len(projects)
        job.projects_added = projects_added
        job.completed_at = timezone.now()
        job.save()
        
        logger.info(f"Scraped {projects_added} new projects from {platform.name}")
        return {'status': 'success', 'projects_added': projects_added}
        
    except SourcePlatform.DoesNotExist:
        logger.error(f"Platform {platform_id} not found")
        return {'status': 'error', 'message': 'Platform not found'}
    except Exception as e:
        logger.error(f"Error scraping platform {platform_id}: {e}")
        if 'job' in locals():
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
        return {'status': 'error', 'message': str(e)}


@shared_task
def scrape_all_active_platforms(limit: int = 50):
    """Scrape all active platforms."""
    platforms = SourcePlatform.objects.filter(is_active=True)
    results = []
    for platform in platforms:
        result = scrape_platform.delay(platform.id, limit)
        results.append({'platform': platform.name, 'task_id': result.id})
    return results
