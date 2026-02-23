from dataclasses import dataclass
from src.domain.entities.candidate import Candidate
from src.domain.entities.job import Job


@dataclass
class MatchScore:
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    is_qualified: bool

    def is_above_threshold(self, threshold: float) -> bool:
        return self.score >= threshold


class CandidateMatchingService:
    def __init__(self, min_match_threshold: float = 0.3):
        self.min_match_threshold = min_match_threshold

    def match_candidate_with_job(self, candidate: Candidate, job: Job) -> MatchScore:
        candidate_skills = set(s.lower() for s in candidate.skills)
        job_skills = set(s.lower() for s in job.skills)

        matched = candidate_skills.intersection(job_skills)
        missing = job_skills - candidate_skills

        if not job_skills:
            skill_score = 1.0
        else:
            skill_score = len(matched) / len(job_skills)

        exp_score = self._calculate_experience_score(candidate.experience_years, job.description or "")
        loc_score = self._calculate_location_score(job.work_type)

        weighted_score = skill_score * 0.5 + exp_score * 0.3 + loc_score * 0.2
        final_score = round(weighted_score, 3)

        is_qualified = final_score >= self.min_match_threshold and len(matched) >= 2

        return MatchScore(
            score=final_score,
            matched_skills=list(matched),
            missing_skills=list(missing),
            is_qualified=is_qualified
        )

    def _calculate_experience_score(self, years: int, description: str) -> float:
        desc_lower = description.lower()
        if "senior" in desc_lower or "lead" in desc_lower or "principal" in desc_lower:
            return 1.0 if years >= 5 else 0.5
        elif "junior" in desc_lower or "entry" in desc_lower:
            return 1.0 if years <= 2 else 0.8
        return 1.0 if years >= 2 else 0.6

    def _calculate_location_score(self, work_type: str) -> float:
        if not work_type or work_type.lower() == "remote":
            return 1.0
        if work_type.lower() == "hybrid":
            return 0.7
        return 0.5
