from enum import Enum as PythonEnum
from sqlalchemy import Boolean, Column, UUID, DateTime,Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.utils.db_utils import Base

class AuthorBookModel(Base):
    __tablename__ = "author_book"
    primary_author = Column(Boolean, nullable=False)

    # Foreign key
    author_id = Column(UUID, ForeignKey('author.id'), primary_key=True)
    book_id = Column(UUID, ForeignKey('books.id'), primary_key=True)

    #Relationship
    author = relationship("AuthorModel", back_populates="books")
    books = relationship("BooksModel", back_populates="author")

    def __repr__(self):
        return f"<Borrow(, book_id={self.book_id}, status={self.status})>"
