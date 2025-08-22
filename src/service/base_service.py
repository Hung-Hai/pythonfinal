# src/services/base_service.py
from typing import Generic, TypeVar, List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

C = TypeVar("C")  # CreateDTO
U = TypeVar("U")  # UpdateDTO
R = TypeVar("R")  # ResponseDTO
RepoT = TypeVar("RepoT")  # Repository type


class BaseService(Generic[C, U, R, RepoT]):
    response_model: Optional[Type[R]] = None  # type of the DTO to convert to

    def __init__(self, repo: RepoT, response_model: Optional[Type[R]] = None):
        self.repo = repo
        self.response_model = response_model

    def _to_dto(self, obj) -> R:
        if self.response_model and obj is not None:
            # Add from_attributes=True to handle SQLAlchemy objects
            return self.response_model.model_validate(obj, from_attributes=True)
        return obj

    def _to_dto_list(self, objs: List) -> List[R]:
        if self.response_model:
            # Add from_attributes=True to handle SQLAlchemy objects
            return [self.response_model.model_validate(obj, from_attributes=True) for obj in objs]
        return objs

    async def list(self, db: AsyncSession, skip: int, limit: int) -> List[R]:
        objs = await self.repo.get_multi(db, skip=skip, limit=limit)
        return self._to_dto_list(objs)

    async def list_all(self, db: AsyncSession) -> List[R]:
        objs = await self.repo.get_all(db)
        return self._to_dto_list(objs)

    async def get(self, db: AsyncSession, obj_id: UUID) -> Optional[R]:
        obj = await self.repo.get(db, id=obj_id)
        return self._to_dto(obj)

    async def create(self, db: AsyncSession, obj_in: C) -> R:
        obj = await self.repo.create(db, obj_in=obj_in)
        return self._to_dto(obj)

    async def update(self, db: AsyncSession, obj_id: UUID, obj_in: U) -> Optional[R]:
        obj = await self.repo.update(db, id=obj_id, obj_in=obj_in)
        return self._to_dto(obj)

    async def delete(self, db: AsyncSession, obj_id: UUID) -> bool:
        return await self.repo.delete(db, id=obj_id)