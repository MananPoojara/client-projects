import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Union, List, Dict

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.board_id = self.config.get("board_id", "unknown")
        self.name = self.config.get("name", "Unknown")
        self.base_url = self.config.get("base_url", "")
        self.throttle = self.config.get("throttle", {})
        
        self.delay = self.throttle.get("delay_seconds", 2)
        self.max_concurrency = self.throttle.get("max_concurrency", 1)
        self.max_retries = self.throttle.get("max_retries", 3)
        self.timeout = self.throttle.get("request_timeout_seconds", 30)

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        if not config_path:
            config_path = Path(__file__).parent.parent.parent / "config" / "boards" / f"{self.board_id}.json"
        
        config_file = Path(config_path) if config_path else None
        if config_file and config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {}

    @abstractmethod
    def scrape(self, keywords: list[str], location: str = "", **kwargs) -> Union[list[dict], Any]:
        """Scrape jobs from the job board. Can be sync or async."""
        pass

    def _create_job_record(
        self,
        job_board_id: str,
        title: str,
        company: str,
        source_url: str,
        **kwargs
    ) -> dict:
        """Create a job record in common schema format."""
        from datetime import datetime, timezone
        
        record = {
            "job_board_id": job_board_id,
            "title": title,
            "company": company,
            "source_url": source_url,
            "source": self.board_id,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "work_type": kwargs.get("work_type", "unknown"),
            "job_type": kwargs.get("job_type", "unknown"),
        }
        
        for key in [
            "location", "description", "short_description", 
            "salary_min", "salary_max", "salary_currency",
            "skills", "posted_date", "application_url"
        ]:
            if key in kwargs and kwargs[key] is not None:
                record[key] = kwargs[key]
        
        return record

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return " ".join(text.split()).strip()

    def _extract_skills(self, text: str, max_skills: int = 10) -> list[str]:
        common_skills = [
            "python", "javascript", "java", "typescript", "react", "node.js",
            "django", "flask", "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes", "git",
            "rest api", "graphql", "machine learning", "tensorflow",
            "reactjs", "angular", "vue", "express", "fastapi", "spring",
            "ruby", "rails", "golang", "rust", "c++", "c#", "php", "laravel"
        ]
        
        if not text:
            return []
        
        text_lower = text.lower()
        found = [skill for skill in common_skills if skill in text_lower]
        return list(set(found))[:max_skills]
