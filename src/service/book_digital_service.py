from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.service.base_service import BaseService
from src.repository.book_digital_repository import BooksDigitalRepository
from src.dto.book_digital_dto import (
    BooksDigitalCreateDTO,
    BooksDigitalUpdateDTO,
    BooksDigitalDTO,
    FileFormat,
    LicenseType,
    BookStatus
)


class BooksDigitalService(
    BaseService[BooksDigitalCreateDTO, BooksDigitalUpdateDTO, BooksDigitalDTO, BooksDigitalRepository]
):
    def __init__(self):
        super().__init__(BooksDigitalRepository(), response_model=BooksDigitalDTO)

    async def get_by_book_id(self, db: AsyncSession, book_id: UUID) -> List[BooksDigitalDTO]:
        return await self.repo.get_by_book_id(db, book_id)

    async def get_by_file_format(self, db: AsyncSession, file_format: FileFormat) -> List[BooksDigitalDTO]:
        return await self.repo.get_by_file_format(db, file_format)

    async def get_by_license_type(self, db: AsyncSession, license_type: LicenseType) -> List[BooksDigitalDTO]:
        return await self.repo.get_by_license_type(db, license_type)

    async def get_by_status(self, db: AsyncSession, status: BookStatus) -> List[BooksDigitalDTO]:
        return await self.repo.get_by_status(db, status)

    async def get_expiring_licenses(
        self, 
        db: AsyncSession, 
        days_threshold: int = 30
    ) -> List[BooksDigitalDTO]:
        return await self.repo.get_expiring_licenses(db, days_threshold)

    async def get_expired_licenses(self, db: AsyncSession) -> List[BooksDigitalDTO]:
        return await self.repo.get_expired_licenses(db)

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
        return await self.repo.search_by_criteria(
            db,
            file_format=file_format,
            license_type=license_type,
            status=status,
            skip=skip,
            limit=limit
        )

    async def get_active_digital_books(self, db: AsyncSession) -> List[BooksDigitalDTO]:
        return await self.repo.get_active_digital_books(db)

    async def bulk_update_status(
        self,
        db: AsyncSession,
        ids: List[UUID],
        status: BookStatus
    ) -> int:
        return await self.repo.bulk_update_status(db, ids, status)

    async def count_by_format(self, db: AsyncSession) -> Dict[str, int]:
        return await self.repo.count_by_format(db)

    async def create_with_validation(
        self,
        db: AsyncSession,
        obj_in: BooksDigitalCreateDTO
    ) -> BooksDigitalDTO:
        """Create digital book with additional validation."""
        # Check if the same format already exists for this book
        if obj_in.book_id:
            existing_formats = await self.repo.get_by_book_id(db, obj_in.book_id)
            for existing in existing_formats:
                if existing.file_format == obj_in.file_format:
                    raise ValueError(f"Digital book with format {obj_in.file_format} already exists for this book")
        
        return await self.create(db, obj_in)

    async def update_license_expiration(
        self,
        db: AsyncSession,
        id: UUID,
        new_expiration: datetime
    ) -> Optional[BooksDigitalDTO]:
        """Update only the license expiration date."""
        update_data = BooksDigitalUpdateDTO(license_expiration=new_expiration)
        return await self.update(db, id, update_data)

    async def renew_license(
        self,
        db: AsyncSession,
        id: UUID,
        extension_days: int = 365
    ) -> Optional[BooksDigitalDTO]:
        """Renew a license by extending its expiration date."""
        digital_book = await self.get(db, id)
        if not digital_book:
            return None
        
        from datetime import datetime, timedelta
        new_expiration = digital_book.license_expiration + timedelta(days=extension_days)
        
        return await self.update_license_expiration(db, id, new_expiration)