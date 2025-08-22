# src/services/author_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.service.base_service import BaseService
from src.dto.author_dto import AuthorCreateDTO, AuthorUpdateDTO, AuthorDTO
from src.repository.author_repository import AuthorRepository


class AuthorService(BaseService[AuthorCreateDTO, AuthorUpdateDTO, AuthorDTO, AuthorRepository]):
    def __init__(self):
        super().__init__(AuthorRepository(), response_model=AuthorDTO)

    async def get_by_name(
        self, db: AsyncSession, first_name: str, last_name: Optional[str] = None
    ) -> List[AuthorDTO]:
        return await self.repo.get_by_name(db, first_name, last_name)
