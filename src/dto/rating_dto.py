from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from src.dto.timemixin import TimestampMixin

class RatingDTO(TimestampMixin):
    id: UUID
    rating: Annotated[int, Field(strict=True, ge=0, le=5)]
    review_date: datetime
    comment: str
    is_approved: Optional[bool] = None
    user_id: Optional[UUID]
    book_id: Optional[UUID]
    
class RatingCreateDTO(BaseModel):
    rating: Annotated[int, Field(strict=True, ge=0, le=5)]
    review_date: Optional[datetime] = None
    comment: str
    is_approved: bool = False
    user_id: Optional[UUID]
    book_id: Optional[UUID]

class RatingUpdateDTO(BaseModel):
    rating: Optional[Annotated[int, Field(strict=True, ge=0, le=5)]] = None
    review_date: Optional[datetime] = None
    comment: Optional[str] = None
    is_approved: Optional[bool] = None
    user_id: Optional[UUID] = None
    book_id: Optional[UUID] = None
