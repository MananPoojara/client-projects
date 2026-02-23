from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.job import Job


class IJobRepository(ABC):
    @abstractmethod
    async def save(self, job: Job) -> None:
        pass

    @abstractmethod
    async def save_many(self, jobs: list[Job]) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, job_id: str) -> Optional[Job]:
        pass

    @abstractmethod
    async def find_by_job_board_id(self, job_board_id: str, source: str) -> Optional[Job]:
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Job]:
        pass

    @abstractmethod
    async def delete_older_than(self, days: int) -> int:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass
