import re
from typing import List, Set

from django.contrib.auth import get_user_model
from .models import ProjectLead, ProjectMatch

User = get_user_model()

_SKILL_SPLIT = re.compile(r"[,;/|]+")


def _flatten_skills(raw) -> List[str]:
    """Normalize list entries and split combined strings like \"React, Node\" into tokens."""
    out: List[str] = []
    for item in raw or []:
        if item is None:
            continue
        s = str(item).strip()
        if not s:
            continue
        for part in _SKILL_SPLIT.split(s):
            t = part.strip()
            if t:
                out.append(t)
    return out


def _normalize_phrase(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def _word_tokens(s: str) -> Set[str]:
    return {t for t in re.findall(r"\w+", s.lower()) if len(t) >= 2}


def _pair_skill_score(required: str, candidate: str) -> float:
    """Score in [0, 1] for one required skill against one user skill."""
    a, b = _normalize_phrase(required), _normalize_phrase(candidate)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if len(a) >= 3 and (a in b or b in a):
        return 0.88
    ta, tb = _word_tokens(required), _word_tokens(candidate)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    if union == 0:
        return 0.0
    jaccard = inter / union
    if jaccard >= 0.5:
        return min(1.0, 0.72 + 0.28 * jaccard)
    if inter > 0:
        return 0.4 + 0.35 * jaccard
    return 0.0


class ProjectMatchingService:
    """Service for matching projects with community members."""

    def score_match_for_user(self, project: ProjectLead, user) -> float:
        """How well ``user`` fits ``project`` (same weighting as bulk user matching)."""
        raw_skills = getattr(user, 'skills', None)
        user_skills = raw_skills if isinstance(raw_skills, list) else []
        skill_match = self._calculate_skill_match(project.skills_required or [], user_skills)
        category_match = self._category_match(project, user_skills)
        combined_skill = min(1.0, skill_match + 0.12 * category_match)
        priority = getattr(user, 'priority_level', 1) or 1
        priority_bonus = priority / 10.0
        rel = float(project.relevance_score or 0.0)
        qual = float(project.quality_score or 0.0)
        project_quality = (rel + qual) / 2.0
        match_score = (combined_skill * 0.6) + (priority_bonus * 0.2) + (project_quality * 0.2)
        return min(1.0, match_score)
    
    def find_matches(self, project: ProjectLead, limit: int = 10) -> List[ProjectMatch]:
        """
        Find best matching users for a project based on skills and other factors.
        """
        # Get all active community members
        users = User.objects.filter(is_community_member=True, is_active=True)
        
        matches = []
        for user in users:
            match_score = self.score_match_for_user(project, user)
            
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
        """How well user skills cover required skills (mean best match per requirement)."""
        required = _flatten_skills(required_skills)
        user_flat = _flatten_skills(user_skills)
        if not required:
            return 0.5
        if not user_flat:
            return 0.0
        total = 0.0
        for req in required:
            best = max(_pair_skill_score(req, u) for u in user_flat)
            total += best
        return total / len(required)

    def _category_match(self, project: ProjectLead, user_skills: List[str]) -> float:
        """Optional alignment between job categories and user skills (0–1)."""
        user_flat = _flatten_skills(user_skills)
        if not user_flat:
            return 0.0
        names = []
        for c in project.categories.all():
            name = getattr(c, 'name', None) or ''
            name = str(name).strip()
            if name:
                names.append(name)
        if not names:
            return 0.0
        total = 0.0
        for cat in names:
            best = max(_pair_skill_score(cat, u) for u in user_flat)
            total += best
        return total / len(names)
