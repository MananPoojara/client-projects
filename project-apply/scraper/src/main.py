import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.scrapers.scraper_factory import ScraperFactory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting scraper service...")
    
    factory = ScraperFactory()
    
    boards = factory.list_boards()
    logger.info(f"Available boards: {boards}")
    
    logger.info("Scraper service ready")


if __name__ == "__main__":
    asyncio.run(main())
