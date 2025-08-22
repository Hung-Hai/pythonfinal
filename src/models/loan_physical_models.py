from sqlalchemy import Column, UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from src.models.loan_models import LoansModel
from src.utils.db_utils import Base

class PhysicalLoansModel(Base, LoansModel):
    __tablename__ = "physical_loan"

    return_date: Column = Column(DateTime, nullable=True)

    # Foreign key
    book_id = Column(UUID, ForeignKey('physical.id'), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)

    # Relationship
    books = relationship("BooksPhysicalModel", back_populates="physical_loan")
    
    def __repr__(self):
        return f"<Book"