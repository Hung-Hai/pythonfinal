from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.publisher_models import PublishersModel
from src.service.base_service import BaseService
from src.repository.publisher_repository import PublisherRepository
from src.dto.publisher_dto import (
    PublisherCreateDTO,
    PublisherUpdateDTO,
    PublisherDTO,
)


class PublisherService(
    BaseService[PublisherCreateDTO, PublisherUpdateDTO, PublisherDTO, PublisherRepository]
):
    def __init__(self):
        super().__init__(PublisherRepository(), response_model=PublisherDTO)

    async def get_by_name(self, db: AsyncSession, name: str) -> List[PublisherDTO]:
        return await self.repo.get_by_name(db, name)
    
    async def get_with_books(self, db: AsyncSession, publisher_id: UUID) -> Optional[PublishersModel]:
        return await self.repo.get_with_books(db, publisher_id)

    async def get_all_with_books(self, db: AsyncSession) -> List[PublishersModel]:
        return await self.repo.get_all_with_books(db)
