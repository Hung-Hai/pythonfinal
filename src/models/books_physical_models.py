import uuid
from sqlalchemy import Column, UUID, DateTime, Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship, Mapped
from src.models.publisher_models import PublishersModel
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin
from src.models.relationship_models import BookStatus


class BooksPhysicalModel(Base, TimestampMixin):
    __tablename__ = "physical"
    __eager_loads__ = ["books"]

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    barcode = Column(String, nullable=False,unique=True)
    shelf_location = Column(String, nullable=False)
    status = Column(Enum(BookStatus))

    # Foreign key
    book_id = Column(UUID, ForeignKey('books.id'))

    # Relationship
    books = relationship("BooksModel", back_populates="physical")
    physical_loan = relationship("PhysicalLoansModel", back_populates="books")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author}, published_year={self.published_year}, publisher={self.publisher}, current_quantity={self.current_quantity}, total_quantity={self.total_quantity})>"