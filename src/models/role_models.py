import uuid
from sqlalchemy import Column, UUID, DateTime, String, text
from sqlalchemy.orm import relationship
from src.utils.db_utils import Base
from src.models.mixin import TimestampMixin
from src.models.relationship_models import user_role_table

class RoleModel(Base, TimestampMixin):
    __tablename__ = "role"
    __eager_loads__ = ["users"]

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # This generates UUID automatically
        server_default=text("gen_random_uuid()")  # For PostgreSQL
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # Relationship
    users = relationship("UsersModel",secondary=user_role_table, back_populates="roles")

    def __repr__(self):
        return f"<Book(id={self.id}, name={self.name}, description={self.description}"