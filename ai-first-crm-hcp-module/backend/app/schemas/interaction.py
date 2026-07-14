from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class InteractionBase(BaseModel):
    hcp_id: int = Field(..., gt=0)
    interaction_date: datetime
    discussion: str = Field(..., min_length=1)
    summary: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    hcp_id: Optional[int] = Field(None, gt=0)
    interaction_date: Optional[datetime] = None
    discussion: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteractionListResponse(BaseModel):
    interactions: list[InteractionResponse]
    total: int


class InteractionHistoryItem(BaseModel):
    id: int
    hcp_id: int
    doctor: str
    hospital: str
    interaction_date: datetime
    discussion: str
    summary: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    status: str


class InteractionHistoryResponse(BaseModel):
    interactions: list[InteractionHistoryItem]
    total: int
