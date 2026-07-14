from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.hcp import HCPCreate, HCPUpdate, HCPResponse, HCPListResponse
from app.services.hcp_service import HCPService

router = APIRouter(prefix="/hcp", tags=["HCP"])


@router.get("", response_model=HCPListResponse)
def get_hcps(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for doctor name, hospital, specialization, city, or email"),
    db: Session = Depends(get_db)
):
    """
    Get all HCPs with optional search and pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 100)
    - **search**: Search term to filter results
    """
    hcp_service = HCPService(db)
    hcps, total = hcp_service.get_all_hcps(skip=skip, limit=limit, search=search)
    
    return HCPListResponse(
        hcps=hcps,
        total=total
    )


@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """
    Get a single HCP by ID.
    
    - **hcp_id**: The ID of the HCP to retrieve
    """
    hcp_service = HCPService(db)
    hcp = hcp_service.get_hcp_by_id(hcp_id)
    
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    
    return hcp


@router.post("", response_model=HCPResponse, status_code=201)
def create_hcp(hcp_data: HCPCreate, db: Session = Depends(get_db)):
    """
    Create a new HCP.
    
    - **doctor_name**: Name of the doctor
    - **hospital**: Hospital/organization name
    - **specialization**: Medical specialization
    - **city**: City where the HCP is located
    - **phone**: Phone number
    - **email**: Email address (must be unique)
    """
    hcp_service = HCPService(db)
    
    try:
        hcp = hcp_service.create_hcp(hcp_data)
        return hcp
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{hcp_id}", response_model=HCPResponse)
def update_hcp(hcp_id: int, hcp_data: HCPUpdate, db: Session = Depends(get_db)):
    """
    Update an existing HCP.
    
    - **hcp_id**: The ID of the HCP to update
    - All fields are optional
    """
    hcp_service = HCPService(db)
    
    try:
        hcp = hcp_service.update_hcp(hcp_id, hcp_data)
        if not hcp:
            raise HTTPException(status_code=404, detail="HCP not found")
        return hcp
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{hcp_id}", status_code=204)
def delete_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """
    Delete an HCP.
    
    - **hcp_id**: The ID of the HCP to delete
    """
    hcp_service = HCPService(db)
    success = hcp_service.delete_hcp(hcp_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="HCP not found")
    
    return None
