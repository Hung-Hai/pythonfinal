from enum import Enum as PythonEnum
import uuid
from sqlalchemy import Column, UUID, DateTime,Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin

class ReservationStatus(PythonEnum):
    PENDING = "PENDING"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class ReservationModel(Base, TimestampMixin):
    __tablename__ = "reservation"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    reservation_date: Column = Column(DateTime, nullable=False)
    expiration_date: Column = Column(DateTime, nullable=False)
    status = Column(Enum(ReservationStatus), nullable=False)
    position: Column = Column(Integer, nullable=False)

    # Foreign key
    user_id = Column(UUID, ForeignKey('users.id'))
    book_id = Column(UUID, ForeignKey('books.id'))

    #Relationship
    user = relationship("UsersModel", back_populates="reservation")
    books = relationship("BooksModel", back_populates="reservation")

    def __repr__(self):
        return (
            f"<Reservation(id={self.id}, user_id={self.user_id}, "
            f"book_id={self.book_id}, status={self.status}, position={self.position})>"
        )