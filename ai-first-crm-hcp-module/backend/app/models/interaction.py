from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_date = Column(DateTime(timezone=True), nullable=False)
    discussion = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with HCP
    hcp = relationship("HCP", backref="interactions")

    def __repr__(self):
        return f"<Interaction(id={self.id}, hcp_id={self.hcp_id}, interaction_date='{self.interaction_date}')>"
