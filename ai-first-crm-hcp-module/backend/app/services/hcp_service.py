from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.hcp import HCP
from app.schemas.hcp import HCPCreate, HCPUpdate


class HCPService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_hcps(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> tuple[List[HCP], int]:
        """Get all HCPs with optional search and pagination"""
        query = self.db.query(HCP)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    HCP.doctor_name.ilike(search_pattern),
                    HCP.hospital.ilike(search_pattern),
                    HCP.specialization.ilike(search_pattern),
                    HCP.city.ilike(search_pattern),
                    HCP.email.ilike(search_pattern)
                )
            )
        
        total = query.count()
        hcps = query.offset(skip).limit(limit).all()
        
        return hcps, total

    def get_hcp_by_id(self, hcp_id: int) -> Optional[HCP]:
        """Get a single HCP by ID"""
        return self.db.query(HCP).filter(HCP.id == hcp_id).first()

    def get_hcp_by_email(self, email: str) -> Optional[HCP]:
        """Get a single HCP by email"""
        return self.db.query(HCP).filter(HCP.email == email).first()

    def get_hcp_by_name(self, name: str) -> Optional[HCP]:
        """Get a single HCP by doctor name (case-insensitive partial match)"""
        return self.db.query(HCP).filter(HCP.doctor_name.ilike(f"%{name}%")).first()

    def create_hcp(self, hcp_data: HCPCreate) -> HCP:
        """Create a new HCP"""
        # Check if email already exists
        existing_hcp = self.get_hcp_by_email(hcp_data.email)
        if existing_hcp:
            raise ValueError(f"HCP with email {hcp_data.email} already exists")
        
        db_hcp = HCP(**hcp_data.model_dump())
        self.db.add(db_hcp)
        self.db.commit()
        self.db.refresh(db_hcp)
        return db_hcp

    def update_hcp(self, hcp_id: int, hcp_data: HCPUpdate) -> Optional[HCP]:
        """Update an existing HCP"""
        db_hcp = self.get_hcp_by_id(hcp_id)
        if not db_hcp:
            return None
        
        # If email is being updated, check if it's already taken
        if hcp_data.email and hcp_data.email != db_hcp.email:
            existing_hcp = self.get_hcp_by_email(hcp_data.email)
            if existing_hcp:
                raise ValueError(f"HCP with email {hcp_data.email} already exists")
        
        update_data = hcp_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_hcp, field, value)
        
        self.db.commit()
        self.db.refresh(db_hcp)
        return db_hcp

    def delete_hcp(self, hcp_id: int) -> bool:
        """Delete an HCP"""
        db_hcp = self.get_hcp_by_id(hcp_id)
        if not db_hcp:
            return False
        
        self.db.delete(db_hcp)
        self.db.commit()
        return True
