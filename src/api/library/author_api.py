# src/api/author_api.py
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.api.library.base_api import BaseAPI
from src.dto.author_dto import AuthorCreateDTO, AuthorUpdateDTO, AuthorDTO
from src.service.author_service import AuthorService
from src.utils.db_utils import create_database_session


def get_author_service() -> AuthorService:
    return AuthorService()


author_api = BaseAPI[AuthorDTO, AuthorCreateDTO, AuthorUpdateDTO, AuthorService](
    prefix="/authors", service_provider=get_author_service, tags=["Authors"]
)

# register generic CRUD routes
author_api.register_crud_routes()

router = author_api.router
# ----- Custom endpoints -----

@author_api.router.get(
    "/search/",
    response_model=List[AuthorDTO],
    summary="Search authors by first/last name"
)
async def search_authors(
    first_name: str = Query(..., description="First name to search"),
    last_name: str | None = Query(None, description="Optional last name to search"),
    db: AsyncSession = Depends(create_database_session),
    service: AuthorService = Depends(get_author_service),
):
    authors = await service.get_by_name(db, first_name, last_name)
    if not authors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No authors found matching criteria"
        )
    return authors
