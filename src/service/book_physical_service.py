from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.base_service import BaseService
from src.repository.book_physical_repository import BooksPhysicalRepository
from src.dto.book_physical_dto import (
    BooksPhysicalCreateDTO,
    BooksPhysicalUpdateDTO,
    BooksPhysicalDTO,
)
from src.models.relationship_models import BookStatus


class BooksPhysicalService(
    BaseService[BooksPhysicalCreateDTO, BooksPhysicalUpdateDTO, BooksPhysicalDTO, BooksPhysicalRepository]
):
    def __init__(self):
        super().__init__(BooksPhysicalRepository(), response_model=BooksPhysicalDTO)

    async def get_by_barcode(self, db: AsyncSession, barcode: str) -> Optional[BooksPhysicalDTO]:
        return await self.repo.get_by_barcode(db, barcode)

    async def get_by_book_id(self, db: AsyncSession, book_id: UUID) -> List[BooksPhysicalDTO]:
        return await self.repo.get_by_book_id(db, book_id)

    async def get_by_status(self, db: AsyncSession, status: BookStatus) -> List[BooksPhysicalDTO]:
        """Get all physical books with a specific status"""
        return await self.repo.get_by_status(db, status)

    async def get_available_by_book_id(self, db: AsyncSession, book_id: UUID) -> List[BooksPhysicalDTO]:
        """Get all available physical copies of a specific book"""
        return await self.repo.get_available_by_book_id(db, book_id)

    async def update_status(
        self, db: AsyncSession, book_physical_id: UUID, new_status: BookStatus
    ) -> BooksPhysicalDTO:
        """Update the status of a physical book"""
        update_data = BooksPhysicalUpdateDTO(status=new_status)
        return await self.update(db, book_physical_id, update_data)

    async def create_with_barcode_check(
        self, db: AsyncSession, create_dto: BooksPhysicalCreateDTO
    ) -> BooksPhysicalDTO:
        """Create a physical book with barcode uniqueness validation"""
        # Check if barcode already exists
        existing = await self.get_by_barcode(db, create_dto.barcode)
        if existing:
            raise ValueError(f"Barcode {create_dto.barcode} already exists")
        
        return await self.create(db, create_dto)

    async def create_bulk(
        self, db: AsyncSession, create_dtos: List[BooksPhysicalCreateDTO]
    ) -> List[BooksPhysicalDTO]:
        """Create multiple physical books with validation"""
        results = []
        
        for create_dto in create_dtos:
            # Check barcode uniqueness for each book
            existing = await self.get_by_barcode(db, create_dto.barcode)
            if existing:
                raise ValueError(f"Barcode {create_dto.barcode} already exists")
            
            result = await self.create(db, create_dto)
            results.append(result)
        
        return results

    async def count_by_book_id(self, db: AsyncSession, book_id: UUID) -> int:
        """Count physical copies of a specific book"""
        books = await self.get_by_book_id(db, book_id)
        return len(books)

    async def count_available_by_book_id(self, db: AsyncSession, book_id: UUID) -> int:
        """Count available physical copies of a specific book"""
        available_books = await self.get_available_by_book_id(db, book_id)
        return len(available_books)