# src/api/role_api.py
from fastapi import Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.library.base_api import BaseAPI
from src.service.role_service import RoleService
from src.dto.role_dto import RoleDTO, RoleCreateDTO, RoleUpdateDTO
from src.utils.db_utils import create_database_session


def get_role_service() -> RoleService:
    return RoleService()


role_api = BaseAPI[RoleDTO, RoleCreateDTO, RoleUpdateDTO, RoleService](
    prefix="/roles",
    service_provider=get_role_service,
    tags=["Roles"],
)
role_api.register_crud_routes()

router = role_api.router

# --- Custom route: get roles by user ---
@role_api.router.get("/by-user/{user_id}", response_model=List[RoleDTO])
async def get_roles_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RoleService = Depends(get_role_service),
):
    roles = await service.get_by_user(db, user_id)
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No roles found for user {user_id}",
        )
    return roles
