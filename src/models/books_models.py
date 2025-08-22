import uuid
from sqlalchemy import Column, UUID, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship, Mapped
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin
from src.models.relationship_models import book_category_table

class BooksModel(Base, TimestampMixin):
    __tablename__ = "books"
    __eager_loads__ = ["author"]

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    isbn = Column(String, nullable=False)
    title = Column(String, nullable=False)
    published_year = Column(Integer)
    language = Column(String, nullable=False)
    edition = Column(String)
    description = Column(String)
    cover_image_url = Column(String)

    # Foreign key
    publisher_id = Column(UUID, ForeignKey('publisher.id'))

    # Relationship
    reservation = relationship("ReservationModel", back_populates="books")
    rating = relationship("RatingModel", back_populates="books")
    category = relationship("CategoriesModel",secondary=book_category_table, back_populates="books")
    publisher = relationship("PublishersModel", back_populates="books")
    author = relationship("AuthorBookModel", back_populates="books")
    physical = relationship("BooksPhysicalModel", back_populates="books")
    digital = relationship("BooksDigitalModel", back_populates="books")

    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author}, published_year={self.published_year}, publisher={self.publisher}, current_quantity={self.current_quantity}, total_quantity={self.total_quantity})>"