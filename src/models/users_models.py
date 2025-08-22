import uuid
from sqlalchemy import Boolean, Column, UUID, DateTime, String, func, text
from sqlalchemy.orm import relationship, Mapped
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin
from src.models.relationship_models import user_role_table

class UsersModel(Base, TimestampMixin):
    __tablename__ = "users"
    # __eager_loads__ = ["roles"]

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    username = Column(String, nullable=False, unique = True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    phone = Column(String)
    address = Column(String)
    is_active = Column(Boolean)
    last_login = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationship
    roles = relationship("RoleModel",secondary=user_role_table, back_populates="users")
    rating = relationship("RatingModel", back_populates="user")
    reservation = relationship("ReservationModel", back_populates="user")
    digital_loans = relationship("DigitalLoansModel", back_populates="user")
    physical_loans = relationship("PhysicalLoansModel", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"