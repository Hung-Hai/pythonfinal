# src/services/role_service.py
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.role_repository import RoleRepository
from src.dto.role_dto import RoleCreateDTO, RoleUpdateDTO, RoleDTO
from src.service.base_service import BaseService


class RoleService(BaseService[RoleCreateDTO, RoleUpdateDTO, RoleDTO, RoleRepository]):
    def __init__(self):
        super().__init__(RoleRepository(), response_model=RoleDTO)

    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[RoleDTO]:
        """Get all roles assigned to a specific user."""
        return await self.repo.get_by_user(db, user_id)
