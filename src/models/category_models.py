import uuid
from sqlalchemy import Column, UUID, DateTime, Integer, String, text
from sqlalchemy.orm import relationship, Mapped
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin
from src.models.relationship_models import book_category_table

class CategoriesModel(Base, TimestampMixin):
    __tablename__ = "category"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # Relationship
    books = relationship("BooksModel",secondary=book_category_table, back_populates="category")
    
    def __repr__(self):
        return f"<Book(id={self.id}, name={self.name}, description={self.description}"