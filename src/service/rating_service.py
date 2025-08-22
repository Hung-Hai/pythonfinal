from src.service.base_service import BaseService
from src.repository.rating_repository import RatingRepository
from src.dto.rating_dto import RatingCreateDTO, RatingUpdateDTO, RatingDTO


class RatingService(
    BaseService[RatingCreateDTO, RatingUpdateDTO, RatingDTO, RatingRepository]
):
    def __init__(self):
        super().__init__(RatingRepository(), response_model=RatingDTO)

    # ---- custom methods beyond base CRUD ----
    async def get_by_user(self, db, user_id):
        return await self.repo.get_by_user(db, user_id)

    async def get_by_book(self, db, book_id):
        return await self.repo.get_by_book(db, book_id)

    async def get_approved(self, db, book_id):
        return await self.repo.get_approved(db, book_id)

    async def get_pending_approval(self, db):
        """Get all ratings pending approval"""
        return await self.list_all(db, filters={"is_approved": False})

    async def get_approved_by_user(self, db, user_id):
        """Get approved ratings for a specific user"""
        return await self.list_all(db, filters={"user_id": user_id, "is_approved": True})

    async def get_pending_by_user(self, db, user_id):
        """Get pending approval ratings for a specific user"""
        return await self.list_all(db, filters={"user_id": user_id, "is_approved": False})

    async def get_by_user_and_book(self, db, user_id, book_id):
        """Get a specific rating by user and book"""
        ratings = await self.list_all(db, filters={"user_id": user_id, "book_id": book_id})
        return ratings[0] if ratings else None