"""
Celery tasks for project-related background operations.
"""
from celery import shared_task
from django.utils import timezone
from .models import ProjectLead
from .services import ProjectMatchingService
import logging

logger = logging.getLogger(__name__)


@shared_task
def auto_match_qualified_projects():
    """Automatically find matches for qualified projects that haven't been matched yet."""
    try:
        qualified_projects = ProjectLead.objects.filter(
            status__in=['new', 'qualified'],
            matched_user__isnull=True
        )[:50]  # Process up to 50 at a time
        
        matching_service = ProjectMatchingService()
        matched_count = 0
        
        for project in qualified_projects:
            matches = matching_service.find_matches(project, limit=5)
            if matches:
                # Auto-select the highest scoring match if score > 0.7
                best_match = matches[0]
                if best_match.match_score > 0.7:
                    best_match.is_selected = True
                    project.matched_user = best_match.user
                    project.status = 'matched'
                    project.save()
                    best_match.save()
                    matched_count += 1
                    logger.info(f"Auto-matched project {project.id} to user {best_match.user.username}")
        
        logger.info(f"Auto-matched {matched_count} projects")
        return {'status': 'success', 'matched_count': matched_count}
        
    except Exception as e:
        logger.error(f"Error in auto_match_qualified_projects: {e}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def requalify_old_projects():
    """Re-qualify projects that are older than 7 days and still in 'new' status."""
    from datetime import timedelta
    from scrapers.qualifiers import ProjectQualifier
    
    try:
        cutoff_date = timezone.now() - timedelta(days=7)
        old_projects = ProjectLead.objects.filter(
            status='new',
            created_at__lt=cutoff_date
        )[:100]
        
        qualifier = ProjectQualifier()
        requalified_count = 0
        
        for project in old_projects:
            scores = qualifier.qualify(project)
            project.relevance_score = scores.get('relevance', 0.5)
            project.quality_score = scores.get('quality', 0.5)
            
            if scores.get('relevance', 0) > 0.5:
                project.status = 'qualified'
                project.qualified_at = timezone.now()
                requalified_count += 1
            
            project.save()
        
        logger.info(f"Re-qualified {requalified_count} old projects")
        return {'status': 'success', 'requalified_count': requalified_count}
        
    except Exception as e:
        logger.error(f"Error in requalify_old_projects: {e}")
        return {'status': 'error', 'message': str(e)}
