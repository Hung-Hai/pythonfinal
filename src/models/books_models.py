from sqlalchemy import Column, UUID, DateTime, Integer, String
from sqlalchemy.orm import relationship
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin

class BooksModel(Base, TimestampMixin):
    __tablename__ = "books"

    id = Column(UUID, primary_key=True)
    isbn = Column(String, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String)
    published_year = Column(Integer)
    current_quantity = Column(Integer, nullable=False)
    total_quantity = Column(Integer, nullable=False)
    publisher = Column(String)
    image_url_s = Column(String)
    image_url_m = Column(String)
    image_url_l = Column(String)

    # Relationship
    borrows = relationship("BorrowModel", back_populates="book")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author}, published_year={self.published_year}, publisher={self.publisher}, current_quantity={self.current_quantity}, total_quantity={self.total_quantity})>"