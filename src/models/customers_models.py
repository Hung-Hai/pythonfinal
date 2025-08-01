from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin

class CustomersModel(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    
    # Relationship
    borrows = relationship("BorrowModel", back_populates="user")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, email={self.email})>"