import uuid
from sqlalchemy import Column, UUID, Date, String, text
from sqlalchemy.orm import relationship
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin

class AuthorModel(Base, TimestampMixin):
    __tablename__ = "author"
    __eager_loads__ = ["books"]
    
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    bio = Column(String, nullable=False)
    birth_date = Column(Date)
    death_date = Column(Date, nullable=True)

    # Relationship
    books = relationship("AuthorBookModel", back_populates="author")
    
    def __repr__(self):
        return f"<Book(id={self.id}, name={self.name}, description={self.description}"