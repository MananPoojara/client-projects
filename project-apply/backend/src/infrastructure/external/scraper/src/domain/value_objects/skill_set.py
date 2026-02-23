from dataclasses import dataclass


@dataclass(frozen=True)
class SkillSet:
    skills: tuple[str, ...]

    def __init__(self, skills: list[str]):
        normalized = tuple(sorted(set(s.lower() for s in skills)))
        object.__setattr__(self, 'skills', normalized)

    def calculate_match_score(self, required_skills: list[str]) -> float:
        if not required_skills:
            return 1.0
        required = set(s.lower() for s in required_skills)
        matched = required.intersection(set(self.skills))
        return len(matched) / len(required)

    def to_list(self) -> list[str]:
        return list(self.skills)
