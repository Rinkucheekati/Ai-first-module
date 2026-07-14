from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class HCPBase(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=255)
    hospital: str = Field(..., min_length=1, max_length=255)
    specialization: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr


class HCPCreate(HCPBase):
    pass


class HCPUpdate(BaseModel):
    doctor_name: Optional[str] = Field(None, min_length=1, max_length=255)
    hospital: Optional[str] = Field(None, min_length=1, max_length=255)
    specialization: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None


class HCPResponse(HCPBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HCPListResponse(BaseModel):
    hcps: list[HCPResponse]
    total: int
