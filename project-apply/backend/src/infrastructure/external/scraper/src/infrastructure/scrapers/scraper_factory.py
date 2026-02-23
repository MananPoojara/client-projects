import logging
from typing import Optional
from src.infrastructure.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ScraperFactory:
    def __init__(self):
        self._scrapers: dict[str, type[BaseScraper]] = {}

    def register(self, board_id: str, scraper_class: type[BaseScraper]) -> None:
        self._scrapers[board_id.lower()] = scraper_class
        logger.info(f"Registered scraper: {board_id}")

    def get_scraper(self, board_id: str, config_path: Optional[str] = None) -> BaseScraper:
        scraper_class = self._scrapers.get(board_id.lower())
        if not scraper_class:
            raise ValueError(f"Unknown scraper: {board_id}")
        return scraper_class(config_path=config_path)

    def get_all_scrapers(self, config_path: Optional[str] = None) -> list[BaseScraper]:
        return [scraper_class(config_path=config_path) for scraper_class in self._scrapers.values()]

    def list_boards(self) -> list[str]:
        return list(self._scrapers.keys())
