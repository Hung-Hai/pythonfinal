# src/repositories/role_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.role_models import RoleModel
from src.dto.role_dto import RoleCreateDTO, RoleUpdateDTO, RoleDTO
from src.repository.base_repository import BaseRepository


class RoleRepository(BaseRepository[RoleModel, RoleCreateDTO, RoleUpdateDTO, RoleDTO]):
    def __init__(self):
        super().__init__(RoleModel)

    def _model_to_dto(self, db_obj: RoleModel) -> RoleDTO:
        """Convert UserModel -> UserDTO"""
        user_ids = [u.id for u in db_obj.users]  # UsersModel list
        users = [{"id": users.id, "name": users.name} for users in db_obj.users] if db_obj.users else []
        return RoleDTO(
            id=db_obj.id,
            name=db_obj.name,
            description=db_obj.description,
            user_ids=user_ids,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
            users=users,
        )

    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[RoleDTO]:
        """Get all roles assigned to a specific user."""
        stmt = (
            select(RoleModel)
            .join(RoleModel.users)
            .where(RoleModel.users.any(id=user_id))
        )
        stmt = self._apply_eager_loads(stmt)
        result = await db.execute(stmt)
        roles = result.scalars().all()
        return [self._model_to_dto(r) for r in roles]
