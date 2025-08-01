from enum import Enum as PythonEnum
from sqlalchemy import Column, UUID, DateTime,Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin

class BorrowStatus(PythonEnum):
    CHECKOUT = "checkout"
    RETURNED = "returned"
    OVERDUE = "overdue"

class BorrowModel(Base, TimestampMixin):
    __tablename__ = "borrow"

    id: Column = Column(UUID, primary_key=True)
    borrow_date: Column = Column(DateTime, nullable=False)
    due_date: Column = Column(DateTime, nullable=False)
    return_date = Column(DateTime)
    status = Column(Enum(BorrowStatus), nullable=False)

    # Foreign key
    user_id = Column(UUID, ForeignKey('users.id'))
    book_id = Column(UUID, ForeignKey('books.id'))

    #Relationship
    user = relationship("CustomersModel", back_populates="borrows")
    book = relationship("BooksModel", back_populates="borrows")

    def __repr__(self):
        return f"<Borrow(borrow_id={self.borrow_id}, customer_id={self.customer_id}, book_id={self.book_id}, status={self.status})>"
