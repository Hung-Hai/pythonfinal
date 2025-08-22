from enum import Enum as PythonEnum
import uuid
from sqlalchemy import Column, UUID, DateTime, Enum, ForeignKey, Integer, String, func, text
from sqlalchemy.orm import relationship, Mapped
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin
from src.models.relationship_models import BookStatus

class FileFormat(PythonEnum):
    EPUB = "EPUB"
    PDF = "PDF"
    MOBI = "MOBI"

class LicenseType(PythonEnum):
    ONE = "ONEUSER"
    UNLI = "UNLIMITED"
    METER = "METERED"

class BooksDigitalModel(Base, TimestampMixin):
    __tablename__ = "digital"
    __eager_loads__ = ["books"]

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    file_format = Column(Enum(FileFormat))
    file_url = Column(String, nullable=False)
    status = Column(Enum(BookStatus))
    license_type = Column(Enum(LicenseType), nullable=False)
    license_expiration = Column(DateTime, server_default=func.now(), nullable=False)

    # Foreign key
    book_id = Column(UUID, ForeignKey('books.id'))

    # Relationship
    books = relationship("BooksModel", back_populates="digital")
    digital_loan = relationship("DigitalLoansModel", back_populates="books")
    
    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author}, published_year={self.published_year}, publisher={self.publisher}, current_quantity={self.current_quantity}, total_quantity={self.total_quantity})>"