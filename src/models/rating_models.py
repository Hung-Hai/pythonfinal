from enum import Enum as PythonEnum
import uuid
from sqlalchemy import Column, UUID, DateTime, Boolean, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin


class RatingModel(Base, TimestampMixin):
    __tablename__ = "rating"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    rating: Column = Column(Integer, nullable=False)
    review_date: Column = Column(DateTime, nullable=False)
    comment = Column(String, nullable=False)
    is_approved: Column = Column(Boolean, nullable=True)

    # Foreign key
    user_id = Column(UUID, ForeignKey('users.id'))
    book_id = Column(UUID, ForeignKey('books.id'))

    #Relationship
    user = relationship("UsersModel", back_populates="rating")
    books = relationship("BooksModel", back_populates="rating")

    def __repr__(self):
        return f"<Borrow(borrow_id={self.borrow_id}, customer_id={self.customer_id}, book_id={self.book_id}, status={self.status})>"
