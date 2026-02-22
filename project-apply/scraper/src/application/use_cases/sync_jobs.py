import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional
from src.domain.entities.job import Job
from src.domain.repositories.job_repository import IJobRepository

logger = logging.getLogger(__name__)


class SyncJobsUseCase:
    def __init__(self, job_repository: IJobRepository):
        self.job_repository = job_repository

    async def execute(self, jobs_data: list[dict]) -> dict:
        saved_count = 0
        duplicate_count = 0
        error_count = 0

        for job_data in jobs_data:
            try:
                job = self._create_job_from_dict(job_data)
                
                existing = await self.job_repository.find_by_job_board_id(
                    job.job_board_id, job.source
                )
                
                if existing:
                    duplicate_count += 1
                    logger.debug(f"Duplicate job: {job.job_board_id}")
                    continue

                await self.job_repository.save(job)
                saved_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error saving job: {e}")

        return {
            "total": len(jobs_data),
            "saved": saved_count,
            "duplicates": duplicate_count,
            "errors": error_count,
        }

    def _create_job_from_dict(self, data: dict) -> Job:
        job_id = data.get("id") or self._generate_job_id(data.get("source_url", ""))
        
        posted_date = None
        if data.get("posted_date"):
            try:
                posted_date = datetime.fromisoformat(data["posted_date"].replace("Z", "+00:00"))
            except Exception:
                pass

        return Job(
            id=job_id,
            job_board_id=data.get("job_board_id", ""),
            title=data.get("title", ""),
            company=data.get("company", ""),
            location=data.get("location"),
            description=data.get("description"),
            short_description=data.get("short_description"),
            work_type=data.get("work_type", "unknown"),
            job_type=data.get("job_type", "unknown"),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            salary_currency=data.get("salary_currency"),
            skills=data.get("skills", []),
            source_url=data.get("source_url", ""),
            source=data.get("source", ""),
            posted_date=posted_date,
            scraped_at=datetime.now(timezone.utc),
            application_url=data.get("application_url"),
        )

    def _generate_job_id(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()[:16]
