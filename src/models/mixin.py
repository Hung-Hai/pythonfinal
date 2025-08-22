from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
class TimestampMixin:
    """Mixin that adds timestamp columns to a model."""
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )