from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.api.library.base_api import BaseAPI
from src.service.rating_service import RatingService
from src.dto.rating_dto import RatingCreateDTO, RatingUpdateDTO, RatingDTO
from src.utils.db_utils import create_database_session

def get_rating_service() -> RatingService:
    return RatingService()

# Base CRUD endpoints
rating_api = BaseAPI[RatingCreateDTO, RatingUpdateDTO, RatingDTO, RatingService](
    prefix="/ratings",
    service_provider=get_rating_service,
    tags=["Rating"],
)
rating_api.register_crud_routes()

router = rating_api.router


# --- Extra routes ---
@router.get("/user/{user_id}", response_model=List[RatingDTO])
async def get_ratings_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    return await service.get_by_user(db, user_id)


@router.get("/book/{book_id}", response_model=List[RatingDTO])
async def get_ratings_by_book(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    return await service.get_by_book(db, book_id)


@router.get("/book/{book_id}/approved", response_model=List[RatingDTO])
async def get_approved_ratings(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    return await service.get_approved(db, book_id)

@router.patch("/{rating_id}/approve", response_model=RatingDTO)
async def approve_rating(
    rating_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Approve a specific rating"""
    rating = await service.get(db, onj_id=rating_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating with id {rating_id} not found"
        )
    
    return await service.update(db, rating_id, {"is_approved": True})


@router.patch("/{rating_id}/reject", response_model=RatingDTO)
async def reject_rating(
    rating_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Reject (unapprove) a specific rating"""
    rating = await service.get(db, onj_id=rating_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating with id {rating_id} not found"
        )
    
    return await service.update(db, rating_id, {"is_approved": False})


@router.get("/pending/approval", response_model=List[RatingDTO])
async def get_pending_approval_ratings(
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Get all ratings pending approval"""
    return await service.get_pending_approval(db)


@router.get("/user/{user_id}/approved", response_model=List[RatingDTO])
async def get_approved_ratings_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Get approved ratings for a specific user"""
    return await service.get_approved_by_user(db, user_id)


@router.get("/user/{user_id}/pending", response_model=List[RatingDTO])
async def get_pending_ratings_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Get pending approval ratings for a specific user"""
    return await service.get_pending_by_user(db, user_id)


@router.get("/book/{book_id}/average", response_model=dict)
async def get_average_rating_for_book(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Get average rating and count for a specific book"""
    ratings = await service.get_approved(db, book_id)
    
    if not ratings:
        return {"book_id": book_id, "average_rating": 0, "total_ratings": 0}
    
    total_rating = sum(rating.rating for rating in ratings)
    average_rating = total_rating / len(ratings)
    
    return {
        "book_id": book_id,
        "average_rating": round(average_rating, 2),
        "total_ratings": len(ratings)
    }


@router.get("/book/{book_id}/stats", response_model=dict)
async def get_rating_stats_for_book(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Get detailed rating statistics for a specific book"""
    ratings = await service.get_approved(db, book_id)
    
    if not ratings:
        return {
            "book_id": book_id,
            "average_rating": 0,
            "total_ratings": 0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
    
    total_rating = sum(rating.rating for rating in ratings)
    average_rating = total_rating / len(ratings)
    
    # Count ratings by star value
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings:
        if 1 <= rating.rating <= 5:
            distribution[rating.rating] += 1
    
    return {
        "book_id": book_id,
        "average_rating": round(average_rating, 2),
        "total_ratings": len(ratings),
        "rating_distribution": distribution
    }


@router.delete("/user/{user_id}/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_rating_for_book(
    user_id: UUID,
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: RatingService = Depends(RatingService),
):
    """Delete a specific user's rating for a specific book"""
    rating = await service.get_by_user_and_book(db, user_id, book_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating for user {user_id} and book {book_id} not found"
        )
    
    await service.delete(db, rating.id)