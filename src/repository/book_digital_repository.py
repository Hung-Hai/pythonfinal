from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from src.models.books_digital_models import BooksDigitalModel
from src.dto.book_digital_dto import (
    BooksDigitalCreateDTO,
    BooksDigitalUpdateDTO,
    BooksDigitalDTO,
    FileFormat,
    LicenseType,
    BookStatus
)
from src.repository.base_repository import BaseRepository


class BooksDigitalRepository(
    BaseRepository[BooksDigitalModel, BooksDigitalCreateDTO, BooksDigitalUpdateDTO, BooksDigitalDTO]
):
    def __init__(self):
        super().__init__(BooksDigitalModel)

    def _model_to_dto(self, db_obj: BooksDigitalModel) -> Optional[BooksDigitalDTO]:
        """Convert SQLAlchemy model to DTO."""
        return BooksDigitalDTO.from_orm(db_obj) if db_obj else None

    async def get(self, db: AsyncSession, id: UUID) -> Optional[BooksDigitalDTO]:
        """Get a single digital book by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return self._model_to_dto(result.scalars().first())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None
    ) -> List[BooksDigitalDTO]:
        """Get multiple digital books with optional filters."""
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_book_id(self, db: AsyncSession, book_id: UUID) -> List[BooksDigitalDTO]:
        """Get all digital versions of a given book."""
        result = await db.execute(select(self.model).filter(self.model.book_id == book_id))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_file_format(self, db: AsyncSession, file_format: FileFormat) -> List[BooksDigitalDTO]:
        """Find digital books by file format (e.g., EPUB, PDF, MOBI)."""
        result = await db.execute(select(self.model).filter(self.model.file_format == file_format))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_license_type(self, db: AsyncSession, license_type: LicenseType) -> List[BooksDigitalDTO]:
        """Find digital books by license type."""
        result = await db.execute(select(self.model).filter(self.model.license_type == license_type))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_status(self, db: AsyncSession, status: BookStatus) -> List[BooksDigitalDTO]:
        """Find digital books by status."""
        result = await db.execute(select(self.model).filter(self.model.status == status))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_expiring_licenses(
        self, 
        db: AsyncSession, 
        days_threshold: int = 30
    ) -> List[BooksDigitalDTO]:
        """Get digital books with licenses expiring within the specified days."""
        from datetime import datetime, timedelta
        expiration_threshold = datetime.utcnow() + timedelta(days=days_threshold)
        
        result = await db.execute(
            select(self.model).filter(
                and_(
                    self.model.license_expiration <= expiration_threshold,
                    self.model.license_expiration >= datetime.utcnow()
                )
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_expired_licenses(self, db: AsyncSession) -> List[BooksDigitalDTO]:
        """Get digital books with expired licenses."""
        from datetime import datetime
        
        result = await db.execute(
            select(self.model).filter(self.model.license_expiration < datetime.utcnow())
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def search_by_criteria(
        self,
        db: AsyncSession,
        *,
        file_format: Optional[FileFormat] = None,
        license_type: Optional[LicenseType] = None,
        status: Optional[BookStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BooksDigitalDTO]:
        """Search digital books by multiple criteria."""
        query = select(self.model)
        
        filters = []
        if file_format:
            filters.append(self.model.file_format == file_format)
        if license_type:
            filters.append(self.model.license_type == license_type)
        if status:
            filters.append(self.model.status == status)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_active_digital_books(self, db: AsyncSession) -> List[BooksDigitalDTO]:
        """Get all active digital books."""
        result = await db.execute(
            select(self.model).filter(
                and_(
                    self.model.status == BookStatus.ACTIVE,
                    self.model.license_expiration > datetime.utcnow()
                )
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def bulk_update_status(
        self,
        db: AsyncSession,
        ids: List[UUID],
        status: BookStatus
    ) -> int:
        """Bulk update status for multiple digital books."""
        result = await db.execute(
            self.model.__table__.update()
            .where(self.model.id.in_(ids))
            .values(status=status)
        )
        await db.commit()
        return result.rowcount

    async def count_by_format(self, db: AsyncSession) -> dict:
        """Count digital books by file format."""
        from sqlalchemy import func
        
        result = await db.execute(
            select(self.model.file_format, func.count(self.model.id))
            .group_by(self.model.file_format)
        )
        return {row[0]: row[1] for row in result.all()}