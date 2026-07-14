from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.interaction import Interaction
from app.models.hcp import HCP
from app.schemas.interaction import InteractionCreate, InteractionUpdate


class InteractionService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_interactions(
        self,
        skip: int = 0,
        limit: int = 100,
        hcp_id: Optional[int] = None
    ) -> tuple[List[Interaction], int]:
        """Get all interactions with optional filtering and pagination"""
        query = self.db.query(Interaction)
        
        if hcp_id:
            query = query.filter(Interaction.hcp_id == hcp_id)
        
        total = query.count()
        interactions = query.order_by(Interaction.interaction_date.desc()).offset(skip).limit(limit).all()
        
        return interactions, total

    def get_interaction_by_id(self, interaction_id: int) -> Optional[Interaction]:
        """Get a single interaction by ID"""
        return self.db.query(Interaction).filter(Interaction.id == interaction_id).first()

    def create_interaction(self, interaction_data: InteractionCreate) -> Interaction:
        """Create a new interaction"""
        db_interaction = Interaction(**interaction_data.model_dump())
        self.db.add(db_interaction)
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def update_interaction(self, interaction_id: int, interaction_data: InteractionUpdate) -> Optional[Interaction]:
        """Update an existing interaction"""
        db_interaction = self.get_interaction_by_id(interaction_id)
        if not db_interaction:
            return None
        
        update_data = interaction_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_interaction, field, value)
        
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def delete_interaction(self, interaction_id: int) -> bool:
        """Delete an interaction"""
        db_interaction = self.get_interaction_by_id(interaction_id)
        if not db_interaction:
            return False
        
        self.db.delete(db_interaction)
        self.db.commit()
        return True

    def get_interactions_by_hcp_id(self, hcp_id: int) -> List[Interaction]:
        """Get all interactions for a specific HCP"""
        return self.db.query(Interaction).filter(Interaction.hcp_id == hcp_id).order_by(Interaction.interaction_date.desc()).all()

    def get_interaction_history(self):
        """Return interactions joined with the HCP fields used by the history grid."""
        return self.db.query(Interaction, HCP.doctor_name, HCP.hospital).join(HCP).order_by(
            Interaction.interaction_date.desc()
        ).all()

    def search_interactions(
        self,
        hcp_id: Optional[int] = None,
        hcp_name: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        interaction_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Interaction]:
        """
        Search interactions with multiple filters.
        
        Args:
            hcp_id: Filter by HCP ID
            hcp_name: Filter by HCP name (partial match)
            date_from: Filter interactions from this date
            date_to: Filter interactions until this date
            interaction_type: Filter by interaction type (currently not stored in database)
            limit: Maximum number of results to return
        
        Returns:
            List of matching interactions
        """
        query = self.db.query(Interaction)
        
        # Filter by HCP ID if provided
        if hcp_id is not None:
            query = query.filter(Interaction.hcp_id == hcp_id)
        
        # Filter by HCP name if provided (partial match)
        if hcp_name:
            query = query.join(HCP).filter(HCP.doctor_name.ilike(f"%{hcp_name}%"))
        
        # Filter by date range if provided
        if date_from:
            query = query.filter(Interaction.interaction_date >= date_from)
        
        if date_to:
            query = query.filter(Interaction.interaction_date <= date_to)
        
        # Note: interaction_type is not currently stored in the database model
        # This filter is ignored to avoid errors. Can be added in future migrations.
        
        # Order by date descending and limit results
        results = query.order_by(Interaction.interaction_date.desc()).limit(limit).all()
        
        return results
