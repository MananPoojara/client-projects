from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    id: str
    job_board_id: str
    title: str
    company: str
    location: Optional[str]
    description: Optional[str]
    short_description: Optional[str]
    work_type: str
    job_type: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: Optional[str]
    skills: list[str]
    source_url: str
    source: str
    posted_date: Optional[datetime]
    scraped_at: datetime
    application_url: Optional[str]

    def __post_init__(self):
        if self.work_type not in ["remote", "hybrid", "onsite", "unknown"]:
            self.work_type = "unknown"
        if self.job_type not in ["full_time", "part_time", "contract", "internship", "unknown"]:
            self.job_type = "unknown"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_board_id": self.job_board_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "short_description": self.short_description,
            "work_type": self.work_type,
            "job_type": self.job_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "skills": self.skills,
            "source_url": self.source_url,
            "source": self.source,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "scraped_at": self.scraped_at.isoformat(),
            "application_url": self.application_url,
        }
