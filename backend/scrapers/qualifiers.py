"""
AI-powered project qualification system.
"""
import logging
from typing import Dict
from projects.models import ProjectLead

logger = logging.getLogger(__name__)


class ProjectQualifier:
    """Qualifies projects using AI/ML to determine relevance and quality."""
    
    # Keywords that indicate high-quality projects
    QUALITY_KEYWORDS = [
        'budget', 'timeline', 'deadline', 'requirements', 'specifications',
        'experience', 'portfolio', 'references', 'milestones'
    ]
    
    # Keywords that indicate relevant projects
    RELEVANCE_KEYWORDS = [
        'web development', 'software', 'application', 'api', 'backend', 'frontend',
        'full stack', 'react', 'django', 'python', 'javascript', 'database',
        'mobile app', 'saas', 'platform', 'system'
    ]
    
    def qualify(self, project: ProjectLead) -> Dict[str, float]:
        """
        Qualify a project and return relevance and quality scores.
        Returns dict with 'relevance' and 'quality' scores (0-1).
        """
        text = f"{project.title} {project.description}".lower()
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(text, project)
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(text, project)
        
        return {
            'relevance': relevance_score,
            'quality': quality_score
        }
    
    def _calculate_quality_score(self, text: str, project: ProjectLead) -> float:
        """Calculate quality score based on project details."""
        score = 0.0
        
        # Check for quality keywords
        keyword_matches = sum(1 for keyword in self.QUALITY_KEYWORDS if keyword in text)
        score += min(0.4, keyword_matches * 0.05)
        
        # Budget presence increases quality
        if project.budget_min or project.budget_max:
            score += 0.2
        
        # Contact information increases quality
        if project.contact_email:
            score += 0.2
        if project.contact_name:
            score += 0.1
        if project.company_name:
            score += 0.1
        
        # Description length (longer = more detailed = higher quality)
        if len(project.description) > 200:
            score += 0.1
        elif len(project.description) > 100:
            score += 0.05
        
        return min(1.0, score)
    
    def _calculate_relevance_score(self, text: str, project: ProjectLead) -> float:
        """Calculate relevance score based on keywords and skills."""
        score = 0.0
        
        # Check for relevance keywords
        keyword_matches = sum(1 for keyword in self.RELEVANCE_KEYWORDS if keyword in text)
        score += min(0.6, keyword_matches * 0.1)
        
        # Skills match (if skills are specified)
        if project.skills_required:
            # More skills specified = more relevant (shows it's a real project)
            score += min(0.2, len(project.skills_required) * 0.05)
        
        # Normalize
        return min(1.0, score)
    
    def qualify_with_ai(self, project: ProjectLead) -> Dict[str, float]:
        """
        Advanced qualification using OpenAI API (if configured).
        Falls back to rule-based if API not available.
        """
        # TODO: Implement OpenAI-based qualification
        # For now, use rule-based
        return self.qualify(project)
