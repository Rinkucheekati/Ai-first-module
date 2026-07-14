from typing import Dict, Any, List
from datetime import datetime
from langchain_core.tools import tool


@tool
def search_interactions(
    hcp_id: int = None,
    hcp_name: str = None,
    date_from: str = None,
    date_to: str = None,
    interaction_type: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Retrieve previous interactions based on search criteria.
    
    Args:
        hcp_id: Filter by HCP ID
        hcp_name: Filter by HCP name (partial match)
        date_from: Filter interactions from this date (ISO format)
        date_to: Filter interactions until this date (ISO format)
        interaction_type: Filter by interaction type (call, email, meeting, visit)
        limit: Maximum number of results to return
    
    Returns:
        Dictionary containing search results and metadata
    """
    # Build search criteria
    search_criteria = {
        "limit": limit
    }
    
    if hcp_id:
        search_criteria["hcp_id"] = hcp_id
    
    if hcp_name:
        search_criteria["hcp_name"] = hcp_name.strip()
    
    if interaction_type:
        search_criteria["interaction_type"] = interaction_type.lower()
    
    # Parse date filters
    if date_from:
        try:
            parsed_date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            search_criteria["date_from"] = parsed_date_from.isoformat()
        except (ValueError, AttributeError):
            pass
    
    if date_to:
        try:
            parsed_date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            search_criteria["date_to"] = parsed_date_to.isoformat()
        except (ValueError, AttributeError):
            pass
    
    # In production, this would query the database
    # For now, return mock results
    mock_results = generate_mock_results(search_criteria)
    
    return {
        "success": True,
        "message": f"Found {len(mock_results)} interactions matching criteria",
        "criteria": search_criteria,
        "results": mock_results,
        "total": len(mock_results)
    }


def generate_mock_results(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate mock search results for demonstration.
    In production, this would query the actual database.
    """
    # Mock data - in production, replace with actual database query
    mock_interactions = [
        {
            "id": 1,
            "hcp_id": 1,
            "hcp_name": "Dr. Sarah Johnson",
            "interaction_type": "call",
            "interaction_date": "2024-01-15T10:30:00",
            "discussion": "Discussed new product features and upcoming conference presentation. Dr. Johnson expressed strong interest in the new features.",
            "summary": "Productive call with Dr. Johnson about new features",
            "follow_up_date": "2024-01-22T10:30:00",
            "sentiment": "positive"
        },
        {
            "id": 2,
            "hcp_id": 1,
            "hcp_name": "Dr. Sarah Johnson",
            "interaction_type": "meeting",
            "interaction_date": "2024-01-10T14:00:00",
            "discussion": "In-person meeting at City Hospital. Presented clinical data and case studies. Discussion focused on efficacy and safety profiles.",
            "summary": "Clinical presentation at City Hospital",
            "follow_up_date": None,
            "sentiment": "positive"
        },
        {
            "id": 3,
            "hcp_id": 2,
            "hcp_name": "Dr. Michael Chen",
            "interaction_type": "email",
            "interaction_date": "2024-01-08T09:00:00",
            "discussion": "Sent product information and research papers regarding new treatment options. Awaiting response.",
            "summary": "Initial outreach with supporting materials",
            "follow_up_date": "2024-01-15T09:00:00",
            "sentiment": "neutral"
        }
    ]
    
    # Filter based on criteria
    filtered_results = mock_interactions
    
    if "hcp_id" in criteria:
        filtered_results = [r for r in filtered_results if r["hcp_id"] == criteria["hcp_id"]]
    
    if "hcp_name" in criteria:
        name_lower = criteria["hcp_name"].lower()
        filtered_results = [r for r in filtered_results if name_lower in r["hcp_name"].lower()]
    
    if "interaction_type" in criteria:
        filtered_results = [r for r in filtered_results if r["interaction_type"] == criteria["interaction_type"]]
    
    if "date_from" in criteria:
        date_from = datetime.fromisoformat(criteria["date_from"])
        filtered_results = [r for r in filtered_results if datetime.fromisoformat(r["interaction_date"]) >= date_from]
    
    if "date_to" in criteria:
        date_to = datetime.fromisoformat(criteria["date_to"])
        filtered_results = [r for r in filtered_results if datetime.fromisoformat(r["interaction_date"]) <= date_to]
    
    # Apply limit
    limit = criteria.get("limit", 10)
    return filtered_results[:limit]
