from fastapi import Depends, Query
from typing import List
from uuid import UUID

from src.api.library.base_api import BaseAPI
from src.service.publisher_service import PublisherService
from src.dto.publisher_dto import (
    PublisherDTO,
    PublisherCreateDTO,
    PublisherUpdateDTO,
    PublisherWithBooksDTO,
)
from src.utils.db_utils import create_database_session
from sqlalchemy.ext.asyncio import AsyncSession


def get_publisher_service() -> PublisherService:
    return PublisherService()


publisher_api = BaseAPI[PublisherDTO, PublisherCreateDTO, PublisherUpdateDTO, PublisherService](
    prefix="/publishers",
    service_provider=get_publisher_service,
    tags=["Publishers"],
)

# Register standard CRUD routes
publisher_api.register_crud_routes()

router = publisher_api.router

# Extend with custom endpoints
@publisher_api.router.get("/by-name/", response_model=List[PublisherDTO])
async def get_publishers_by_name(
    name: str = Query(..., description="Search publishers by (partial) name"),
    db: AsyncSession = Depends(create_database_session),
    service: PublisherService = Depends(get_publisher_service),
):
    return await service.get_by_name(db, name)

@publisher_api.router.get("/{publisher_id}/with-books", response_model=PublisherWithBooksDTO)
async def get_publisher_with_books(
    publisher_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PublisherService = Depends(get_publisher_service),
):
    publisher = await service.get_with_books(db, publisher_id)
    if not publisher:
        return None
    # FastAPI + Pydantic will map to PublisherWithBooksDTO since we have relationship
    return publisher


@publisher_api.router.get("/all/with-books", response_model=List[PublisherWithBooksDTO])
async def get_all_publishers_with_books(
    db: AsyncSession = Depends(create_database_session),
    service: PublisherService = Depends(get_publisher_service),
):
    publishers = await service.get_all_with_books(db)
    return publishers