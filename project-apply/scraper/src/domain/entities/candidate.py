from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Candidate:
    id: str
    name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    skills: list[str]
    experience_years: int
    title: str
    summary: Optional[str]
    resume_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "skills": self.skills,
            "experience_years": self.experience_years,
            "title": self.title,
            "summary": self.summary,
            "resume_url": self.resume_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
