from enum import Enum
from sqlalchemy import Column, UUID, ForeignKey, String, Table
from src.utils.db_utils import Base

class BookStatus(Enum):
    AVAILABLE = "AVAILABLE"
    CHECKOUT = "CHECKOUT"
    LOST = "LOST"
    MAINTENANCE = "MAINTENANCE"
    

book_category_table = Table(
    "category_book",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("category_id", ForeignKey("category.id"), primary_key=True)
)

user_role_table = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True)
)
