from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.interaction import InteractionCreate, InteractionUpdate, InteractionResponse, InteractionListResponse
from app.services.interaction_service import InteractionService

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.get("", response_model=InteractionListResponse)
def get_interactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    hcp_id: Optional[int] = Query(None, description="Filter by HCP ID"),
    db: Session = Depends(get_db)
):
    """
    Get all interactions with optional filtering and pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 100)
    - **hcp_id**: Filter interactions by HCP ID
    """
    interaction_service = InteractionService(db)
    interactions, total = interaction_service.get_all_interactions(
        skip=skip, 
        limit=limit, 
        hcp_id=hcp_id
    )
    
    return InteractionListResponse(
        interactions=interactions,
        total=total
    )


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """
    Get a single interaction by ID.
    
    - **interaction_id**: The ID of the interaction to retrieve
    """
    interaction_service = InteractionService(db)
    interaction = interaction_service.get_interaction_by_id(interaction_id)
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    return interaction


@router.post("", response_model=InteractionResponse, status_code=201)
def create_interaction(interaction_data: InteractionCreate, db: Session = Depends(get_db)):
    """
    Create a new interaction.
    
    - **hcp_id**: ID of the HCP
    - **interaction_date**: Date and time of the interaction
    - **discussion**: Detailed discussion notes
    - **summary**: Optional summary of the interaction
    - **follow_up_date**: Optional follow-up date
    """
    interaction_service = InteractionService(db)
    interaction = interaction_service.create_interaction(interaction_data)
    return interaction


@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(interaction_id: int, interaction_data: InteractionUpdate, db: Session = Depends(get_db)):
    """
    Update an existing interaction.
    
    - **interaction_id**: The ID of the interaction to update
    - All fields are optional
    """
    interaction_service = InteractionService(db)
    interaction = interaction_service.update_interaction(interaction_id, interaction_data)
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    return interaction


@router.delete("/{interaction_id}", status_code=204)
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """
    Delete an interaction.
    
    - **interaction_id**: The ID of the interaction to delete
    """
    interaction_service = InteractionService(db)
    success = interaction_service.delete_interaction(interaction_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    return None


@router.get("/hcp/{hcp_id}", response_model=InteractionListResponse)
def get_interactions_by_hcp(
    hcp_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all interactions for a specific HCP.
    
    - **hcp_id**: The ID of the HCP
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 100)
    """
    interaction_service = InteractionService(db)
    
    # Verify HCP exists
    from app.services.hcp_service import HCPService
    hcp_service = HCPService(db)
    hcp = hcp_service.get_hcp_by_id(hcp_id)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    
    interactions, total = interaction_service.get_all_interactions(
        skip=skip, 
        limit=limit, 
        hcp_id=hcp_id
    )
    
    return InteractionListResponse(
        interactions=interactions,
        total=total
    )
