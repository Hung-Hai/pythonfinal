from sqlalchemy import Column, UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from src.models.loan_models import LoansModel
from src.utils.db_utils import Base

class DigitalLoansModel(Base, LoansModel):
    __tablename__ = "digital_loan"

    access_token = Column(String, nullable=False)

    # Foreign key
    book_id = Column(UUID, ForeignKey('digital.id'), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)

    # Relationship
    books = relationship("BooksDigitalModel", back_populates="digital_loan")
    
    def __repr__(self):
        return f"<Book"