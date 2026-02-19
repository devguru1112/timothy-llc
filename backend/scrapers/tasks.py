"""
Celery tasks for background scraping and qualification.
"""
from celery import shared_task
from django.utils import timezone
from projects.models import ProjectLead, SourcePlatform, JobCategory, ScrapingConfig
from scrapers.models import ScrapingJob
from scrapers.scrapers import get_scraper
from scrapers.qualifiers import ProjectQualifier
import logging

logger = logging.getLogger(__name__)


def match_categories(project_data: dict) -> list:
    """
    Match a project to categories based on keywords.
    Returns list of category IDs that match.
    """
    text = f"{project_data.get('title', '')} {project_data.get('description', '')}".lower()
    matched_categories = []
    
    # Get active categories
    categories = JobCategory.objects.filter(is_active=True)
    
    for category in categories:
        if not category.keywords:
            continue
        
        # Check if any keyword matches
        for keyword in category.keywords:
            if keyword.lower() in text:
                matched_categories.append(category.id)
                break  # Only add category once
    
    return matched_categories


def get_active_scraping_categories() -> list:
    """
    Get category IDs from active scraping configuration.
    Returns empty list if no active config exists.
    """
    try:
        config = ScrapingConfig.objects.filter(is_active=True).first()
        if config:
            return list(config.categories.filter(is_active=True).values_list('id', flat=True))
    except Exception as e:
        logger.warning(f"Error getting scraping config: {e}")
    
    return []


@shared_task
def scrape_platform(platform_id: int, limit: int = 50, category_ids: list = None):
    """
    Scrape projects from a specific platform.
    
    Args:
        platform_id: ID of the platform to scrape
        limit: Maximum number of projects to scrape
        category_ids: Optional list of category IDs to filter by. If None, uses active ScrapingConfig.
    """
    try:
        platform = SourcePlatform.objects.get(id=platform_id, is_active=True)
        job = ScrapingJob.objects.create(
            platform=platform,
            status='running',
            started_at=timezone.now()
        )
        
        # Get categories to filter by
        if category_ids is None:
            category_ids = get_active_scraping_categories()
        
        scraper = get_scraper(platform)
        projects = scraper.scrape(limit=limit)
        
        projects_added = 0
        for project_data in projects:
            # Check if project already exists
            if ProjectLead.objects.filter(source_url=project_data.get('source_url')).exists():
                continue
            
            # Match categories
            matched_category_ids = match_categories(project_data)
            
            # Filter by selected categories if specified
            if category_ids:
                # Only include if project matches at least one selected category
                if not any(cat_id in matched_category_ids for cat_id in category_ids):
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
            
            # Assign matched categories
            if matched_category_ids:
                project.categories.set(matched_category_ids)
            
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
def scrape_all_active_platforms(limit: int = 50, category_ids: list = None):
    """
    Scrape all active platforms.
    
    Args:
        limit: Maximum number of projects per platform
        category_ids: Optional list of category IDs to filter by. If None, uses active ScrapingConfig.
    """
    platforms = SourcePlatform.objects.filter(is_active=True)
    results = []
    for platform in platforms:
        result = scrape_platform.delay(platform.id, limit, category_ids)
        results.append({'platform': platform.name, 'task_id': result.id})
    return results
