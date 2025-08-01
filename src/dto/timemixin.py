from datetime import datetime

from pydantic import BaseModel

class TimestampMixin(BaseModel):
    """Mixin that adds timestamp columns to a model."""
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True