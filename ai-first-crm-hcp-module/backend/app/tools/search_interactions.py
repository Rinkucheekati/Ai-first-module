from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.services.interaction_service import InteractionService


@tool
def search_interactions(
    hcp_id: Optional[int] = None,
    hcp_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    interaction_type: Optional[str] = None,
    limit: int = 10,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Retrieve previous interactions based on search criteria from the database.
    
    Args:
        hcp_id: Filter by HCP ID
        hcp_name: Filter by HCP name (partial match)
        date_from: Filter interactions from this date (ISO format)
        date_to: Filter interactions until this date (ISO format)
        interaction_type: Filter by interaction type (call, email, meeting, visit)
        limit: Maximum number of results to return
        db: Database session for database operations
    
    Returns:
        Dictionary containing search results and metadata
    """
    if db is None:
        return {
            "success": False,
            "message": "Database session not provided. Cannot retrieve interactions.",
            "results": [],
            "total": 0
        }
    
    try:
        interaction_service = InteractionService(db)
        
        # Build search filters
        filters = {}
        
        if hcp_id is not None:
            filters["hcp_id"] = hcp_id
        
        if hcp_name:
            filters["hcp_name"] = hcp_name.strip()
        
        if interaction_type:
            filters["interaction_type"] = interaction_type.lower()
        
        # Parse date filters
        parsed_date_from = None
        if date_from:
            try:
                parsed_date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        parsed_date_to = None
        if date_to:
            try:
                parsed_date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        # Query database using service
        results = interaction_service.search_interactions(
            hcp_id=hcp_id,
            hcp_name=hcp_name,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            interaction_type=interaction_type,
            limit=limit
        )
        
        # Format results for response
        formatted_results = [
            {
                "id": interaction.id,
                "hcp_id": interaction.hcp_id,
                "hcp_name": interaction.hcp.doctor_name if interaction.hcp else "Unknown",
                "interaction_type": interaction.interaction_type,
                "interaction_date": interaction.interaction_date.isoformat() if interaction.interaction_date else None,
                "discussion": interaction.discussion,
                "summary": interaction.summary,
                "follow_up_date": interaction.follow_up_date.isoformat() if interaction.follow_up_date else None,
            }
            for interaction in results
        ]
        
        return {
            "success": True,
            "message": f"Found {len(formatted_results)} interactions matching criteria",
            "results": formatted_results,
            "total": len(formatted_results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error searching interactions: {str(e)}",
            "results": [],
            "total": 0
        }

