# src/services/book_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.service.base_service import BaseService
from src.dto.book_dto import AuthorBookLinkDTO, BookCreateDTO, BookUpdateDTO, BookDTO
from src.repository.book_repository import BookRepository

class BookService(BaseService[BookCreateDTO, BookUpdateDTO, BookDTO, BookRepository]):
    def __init__(self):
        super().__init__(BookRepository(), response_model=BookDTO)

    async def search_books(self, db: AsyncSession, field: str, value: str) -> List[BookDTO]:
        books = await self.repo.get_by_field(db, field_name=field, value=value)
        return [self._book_to_dto(book) for book in books]

    # Override list to automatically convert ORM objects
    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[BookDTO]:
        books = await self.repo.get_multi(db, skip=skip, limit=limit)
        return [self._book_to_dto(book) for book in books]

    # Override list_all to automatically convert ORM objects
    async def list_all(self, db: AsyncSession) -> List[BookDTO]:
        books = await self.repo.get_all(db)
        return [self._book_to_dto(book) for book in books]

    # Override get to automatically convert ORM object
    async def get(self, db: AsyncSession, obj_id) -> Optional[BookDTO]:
        book = await self.repo.get(db, id=obj_id)
        if book:
            return self._book_to_dto(book)
        return None

    # Internal helper to convert a Book ORM object to BookDTO
    def _book_to_dto(self, book) -> BookDTO:
        authors = [
            AuthorBookLinkDTO(
                author_id=link.author_id,
                primary_author=link.primary_author
            )
            for link in getattr(book, "authors", [])
        ]
        # build the DTO
        return BookDTO.model_validate({
            **book.__dict__,
            "authors": authors
        })

    async def get_books_by_author(
        self, 
        db: AsyncSession, 
        author_name: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BookDTO]:
        """Get books by specific author name"""
        books = await self.repo.get_by_author(db, author_name=author_name, skip=skip, limit=limit)
        return [self._book_to_dto(book) for book in books]

    async def get_books_by_genre(
        self, 
        db: AsyncSession, 
        genre: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BookDTO]:
        """Get books by genre"""
        books = await self.repo.get_by_genre(db, genre=genre, skip=skip, limit=limit)
        return [self._book_to_dto(book) for book in books]

    async def get_books_by_year(
        self, 
        db: AsyncSession, 
        year: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BookDTO]:
        """Get books published in a specific year"""
        books = await self.repo.get_by_year(db, year=year, skip=skip, limit=limit)
        return [self._book_to_dto(book) for book in books]

    async def get_count(self, db: AsyncSession) -> int:
        """Get total count of books"""
        return await self.repo.get_count(db)