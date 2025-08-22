import uuid
from sqlalchemy import Column, UUID, DateTime, String, text
from sqlalchemy.orm import relationship
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin

class PublishersModel(Base, TimestampMixin):
    __tablename__ = "publisher"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=False)

    # Relationship
    books = relationship("BooksModel", back_populates="publisher")
    
    def __repr__(self):
        return f"<Book(id={self.id}, name={self.name}, description={self.description}"