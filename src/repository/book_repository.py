# src/repositories/Books.py
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.books_models import BooksModel
from src.dto.book_dto import BookCreateDTO, BookUpdateDTO, BookDTO
from src.repository.base_repository import BaseRepository

class BookRepository(BaseRepository[BooksModel, BookCreateDTO, BookUpdateDTO, BookDTO]):
    def __init__(self):
        super().__init__(BooksModel)

    def _model_to_dto(self, db_obj: BooksModel) -> BookDTO:
        if not db_obj:
            return None
        return BookDTO.from_orm(db_obj) 
    
    async def get_by_isbn(self, db: AsyncSession, isbn: str) -> Optional[BookDTO]:
        result = await db.execute(select(self.model).filter(self.model.ISBN == isbn))
        db_obj = result.scalars().first()
        return self._model_to_dto(db_obj)
    
    async def get_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        value: Any,
        operator: str = "eq"
    ) -> List[BookDTO]:
        """
        Generic method to search books by any field with various operators
        
        Args:
            field_name: Name of the field to filter by
            value: Value to compare against
            operator: Comparison operator ("eq", "contains", "gt", "lt", etc.)
            
        Returns:
            List of matching BookDTOs
        """
        if not hasattr(self.model, field_name):
            return []
            
        field = getattr(self.model, field_name)
        query = select(self.model)
        
        # Handle different comparison operators
        if operator == "eq":
            query = query.where(field == value)
        elif operator == "contains":
            query = query.where(field.contains(value))
        elif operator == "gt":
            query = query.where(field > value)
        elif operator == "lt":
            query = query.where(field < value)
        elif operator == "gte":
            query = query.where(field >= value)
        elif operator == "lte":
            query = query.where(field <= value)
        else:
            query = query.where(field == value)  # Default to equality
            
        result = await db.execute(query)
        db_objs = result.scalars().all()
        return [self._model_to_dto(db_obj) for db_obj in db_objs]

    async def decrease_quantity(self, db: AsyncSession, id: UUID) -> Optional[BookDTO]:
        """Decrease current quantity by 1 (when a book is borrowed)"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        db_obj = result.scalars().first()
        if not db_obj:
            return None
            
        if db_obj.current_quantity > 0:
            db_obj.current_quantity -= 1
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            
        return self._model_to_dto(db_obj)

    async def increase_quantity(self, db: AsyncSession, id: UUID) -> Optional[BookDTO]:
        """Increase current quantity by 1 (when a book is returned)"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        db_obj = result.scalars().first()
        if not db_obj:
            return None
            
        if db_obj.current_quantity < db_obj.total_quantity:
            db_obj.current_quantity += 1
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            
        return self._model_to_dto(db_obj)