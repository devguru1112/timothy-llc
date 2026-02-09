from typing import List
from django.contrib.auth import get_user_model
from .models import ProjectLead, ProjectMatch

User = get_user_model()


class ProjectMatchingService:
    """Service for matching projects with community members."""
    
    def find_matches(self, project: ProjectLead, limit: int = 10) -> List[ProjectMatch]:
        """
        Find best matching users for a project based on skills and other factors.
        """
        # Get all active community members
        users = User.objects.filter(is_community_member=True, is_active=True)
        
        matches = []
        for user in users:
            # Calculate match score based on:
            # 1. Skills overlap
            # 2. User priority level
            # 3. Project relevance/quality scores
            
            skill_match = self._calculate_skill_match(project.skills_required, user.skills)
            priority_bonus = user.priority_level / 10.0  # Normalize priority
            project_quality = (project.relevance_score + project.quality_score) / 2
            
            match_score = (skill_match * 0.6) + (priority_bonus * 0.2) + (project_quality * 0.2)
            match_score = min(1.0, match_score)  # Cap at 1.0
            
            # Only create matches with score > 0.3
            if match_score > 0.3:
                match, created = ProjectMatch.objects.get_or_create(
                    project=project,
                    user=user,
                    defaults={'match_score': match_score}
                )
                if not created:
                    match.match_score = match_score
                    match.save()
                matches.append(match)
        
        # Sort by match score and return top matches
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:limit]
    
    def _calculate_skill_match(self, required_skills: List[str], user_skills: List[str]) -> float:
        """Calculate how well user skills match required skills."""
        if not required_skills:
            return 0.5  # Neutral score if no skills specified
        
        if not user_skills:
            return 0.0
        
        # Normalize skills to lowercase for comparison
        required_normalized = [s.lower().strip() for s in required_skills]
        user_normalized = [s.lower().strip() for s in user_skills]
        
        # Simple overlap calculation
        matches = sum(1 for skill in required_normalized if skill in user_normalized)
        return matches / len(required_normalized) if required_normalized else 0.0
