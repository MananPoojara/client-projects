import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

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
        
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {}

    @abstractmethod
    async def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        """Scrape jobs from the job board."""
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
