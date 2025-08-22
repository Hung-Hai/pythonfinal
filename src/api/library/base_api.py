# src/api/base_api.py
from fastapi import APIRouter, Body, Depends, HTTPException, status, Query
from typing import List, TypeVar, Generic, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.utils.db_utils import create_database_session

DTO = TypeVar("DTO")
CreateDTO = TypeVar("CreateDTO")
UpdateDTO = TypeVar("UpdateDTO")
ServiceT = TypeVar("ServiceT")


class BaseAPI(Generic[DTO, CreateDTO, UpdateDTO, ServiceT]):
    def __init__(self, prefix: str, service_provider: Callable[[], ServiceT], tags: List[str] = None):
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self.get_service = service_provider

    def register_crud_routes(self):
        @self.router.get("/", response_model=List[DTO])
        async def list_items(
            skip: int = Query(0, ge=0),
            limit: int = Query(100, ge=1, le=1000),
            db: AsyncSession = Depends(create_database_session),
            service: ServiceT = Depends(self.get_service),
        ):
            items = await service.list(db, skip, limit)
            if not items:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found")
            return items

        @self.router.get("/all", response_model=List[DTO])
        async def list_all(
            db: AsyncSession = Depends(create_database_session),
            service: ServiceT = Depends(self.get_service),
        ):
            items = await service.list_all(db)
            if not items:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found")
            return items

        @self.router.get("/{obj_id}", response_model=DTO)
        async def get_item(
            obj_id: UUID,
            db: AsyncSession = Depends(create_database_session),
            service: ServiceT = Depends(self.get_service),
        ):
            obj = await service.get(db, obj_id)
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
            return obj

        @self.router.post("/", response_model=DTO, status_code=status.HTTP_201_CREATED)
        async def create_item(
            obj_in: CreateDTO = Body(...),
            db: AsyncSession = Depends(create_database_session),
            service: ServiceT = Depends(self.get_service),
        ):
            try:
                return await service.create(db, obj_in)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

        @self.router.put("/{obj_id}", response_model=DTO)
        async def update_item(
            obj_id: UUID,
            obj_in: UpdateDTO = Body(...),
            db: AsyncSession = Depends(create_database_session),
            service: ServiceT = Depends(self.get_service),
        ):
            obj = await service.update(db, obj_id, obj_in)
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found or update failed")
            return obj

        @self.router.delete("/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_item(
            obj_id: UUID,
            db: AsyncSession = Depends(create_database_session),
            service: ServiceT = Depends(self.get_service),
        ):
            success = await service.delete(db, obj_id)
            if not success:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found or delete failed")
