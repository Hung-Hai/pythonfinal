from enum import Enum as PythonEnum
import uuid
from sqlalchemy import Column, UUID, DateTime,Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship, declarative_mixin, declared_attr

from src.models.mixin import TimestampMixin

class LoanStatus(PythonEnum):
    CHECKOUT = "CHECKOUT"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    EXPIRED = "EXPIRED"

@declarative_mixin
class LoansModel(TimestampMixin):
    """Abstract base for all loan types."""

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True), 
            primary_key=True, 
            default=uuid.uuid4,  # This generates UUID automatically
            server_default=text("gen_random_uuid()")  # For PostgreSQL
        )

    @declared_attr
    def loan_date(cls):
        return Column(DateTime, nullable=False)

    @declared_attr
    def due_date(cls):
        return Column(DateTime, nullable=False)

    @declared_attr
    def status(cls):
        return Column(Enum(LoanStatus), nullable=False)

    @declared_attr
    def user_id(cls):
        return Column(UUID, ForeignKey('users.id'), nullable=False)

    @declared_attr
    def user(cls):
        if cls.__name__ == "DigitalLoansModel":
            return relationship("UsersModel", back_populates="digital_loans")
        elif cls.__name__ == "PhysicalLoansModel":
            return relationship("UsersModel", back_populates="physical_loans")

