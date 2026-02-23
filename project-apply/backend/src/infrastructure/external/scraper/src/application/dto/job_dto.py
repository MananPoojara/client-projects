from dataclasses import dataclass
from src.domain.entities.job import Job


@dataclass
class JobDTO:
    id: str
    job_board_id: str
    title: str
    company: str
    location: str | None
    description: str | None
    short_description: str | None
    work_type: str
    job_type: str
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    skills: list[str]
    source_url: str
    source: str
    posted_date: str | None
    scraped_at: str
    application_url: str | None

    @classmethod
    def from_entity(cls, job: Job) -> "JobDTO":
        return cls(
            id=job.id,
            job_board_id=job.job_board_id,
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
            short_description=job.short_description,
            work_type=job.work_type,
            job_type=job.job_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            skills=job.skills,
            source_url=job.source_url,
            source=job.source,
            posted_date=job.posted_date.isoformat() if job.posted_date else None,
            scraped_at=job.scraped_at.isoformat(),
            application_url=job.application_url,
        )

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
            "posted_date": self.posted_date,
            "scraped_at": self.scraped_at,
            "application_url": self.application_url,
        }
