from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String(255), nullable=False, index=True)
    hospital = Column(String(255), nullable=False)
    specialization = Column(String(255), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<HCP(id={self.id}, doctor_name='{self.doctor_name}', email='{self.email}')>"
