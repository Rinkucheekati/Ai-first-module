from typing import Dict, Any
from datetime import datetime
from langchain_core.tools import tool
from sqlalchemy.orm import Session
import re

from app.services.hcp_service import HCPService
from app.services.interaction_service import InteractionService
from app.schemas.hcp import HCPCreate
from app.schemas.interaction import InteractionCreate


@tool
def log_interaction(
    hcp_name: str,
    discussion: str,
    interaction_type: str = "call",
    interaction_date: str = None,
    summary: str = None,
    follow_up_date: str = None,
    hospital: str = None,
    db: Session = None
) -> Dict[str, Any]:
    """
    Extract structured information from user conversation and store it in the database.
    
    This function:
    1. Extracts structured information from the conversation
    2. Looks up or creates the HCP record
    3. Creates the Interaction record linked to the HCP
    4. Returns the interaction ID and confirmation
    
    Args:
        hcp_name: Name of the Healthcare Professional
        discussion: Detailed discussion notes from the interaction
        interaction_type: Type of interaction (call, email, meeting, visit)
        interaction_date: Date of the interaction (ISO format, defaults to now)
        summary: Optional summary of the interaction
        follow_up_date: Optional follow-up date (ISO format)
        hospital: Optional hospital/organization name
        db: Database session for database operations
    
    Returns:
        Dictionary containing interaction_id, doctor_name, and success message
    """
    if db is None:
        return {
            "success": False,
            "interaction_id": None,
            "doctor_name": hcp_name,
            "message": "Database session not provided. Cannot store interaction."
        }
    
    try:
        # Set default date if not provided
        if interaction_date is None:
            interaction_date = datetime.now().isoformat()
        
        # Parse and validate interaction date
        try:
            parsed_date = datetime.fromisoformat(interaction_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            parsed_date = datetime.now()
        
        # Parse follow-up date if provided
        parsed_follow_up = None
        if follow_up_date:
            try:
                parsed_follow_up = datetime.fromisoformat(follow_up_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                parsed_follow_up = None
        
        # Generate summary if not provided
        if not summary:
            summary = generate_summary(discussion)
        
        # Initialize services
        hcp_service = HCPService(db)
        interaction_service = InteractionService(db)
        
        # Look up or create HCP
        hcp = hcp_service.get_hcp_by_name(hcp_name.strip())
        
        if hcp is None:
            # Create new HCP record
            hcp_create_data = HCPCreate(
                doctor_name=hcp_name.strip(),
                hospital=hospital or "Unknown Hospital",
                specialization="General",  # Default, could be enhanced with LLM extraction
                city="Unknown",  # Default, could be enhanced with LLM extraction
                phone="000-000-0000",  # Default placeholder
                email=f"{hcp_name.strip().lower().replace(' ', '.')}@placeholder.com"  # Placeholder email
            )
            
            try:
                hcp = hcp_service.create_hcp(hcp_create_data)
            except ValueError as e:
                # If email conflict, try with a different approach
                hcp_create_data.email = f"hcp_{datetime.now().timestamp()}@placeholder.com"
                hcp = hcp_service.create_hcp(hcp_create_data)
        
        # Create Interaction record
        interaction_create_data = InteractionCreate(
            hcp_id=hcp.id,
            interaction_date=parsed_date,
            discussion=discussion.strip(),
            summary=summary.strip(),
            follow_up_date=parsed_follow_up
        )
        
        interaction = interaction_service.create_interaction(interaction_create_data)
        
        # Commit the transaction
        db.commit()
        
        return {
            "success": True,
            "interaction_id": interaction.id,
            "doctor_name": hcp.doctor_name,
            "message": "Interaction stored successfully."
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "interaction_id": None,
            "doctor_name": hcp_name,
            "message": f"Failed to store interaction: {str(e)}"
        }


def generate_summary(discussion: str) -> str:
    """
    Generate a concise summary from the discussion text.
    In production, this would use an LLM. For now, use a simple approach.
    """
    # Take first 2 sentences or first 150 characters
    sentences = re.split(r'[.!?]+', discussion)
    summary_sentences = [s.strip() for s in sentences if s.strip()][:2]
    summary = ' '.join(summary_sentences)
    
    if len(summary) > 150:
        summary = summary[:147] + "..."
    
    return summary if summary else discussion[:150]


def extract_entities(discussion: str) -> Dict[str, list]:
    """
    Extract entities from the discussion text.
    In production, this would use NER. For now, use simple patterns.
    """
    entities = {
        "medications": [],
        "products": [],
        "concerns": [],
        "outcomes": []
    }
    
    # Simple pattern matching (in production, use proper NER)
    medication_patterns = [r'\b(?:prescribed|recommended|mentioned)\s+(\w+)\b']
    concern_patterns = [r'\b(?:concern|worry|issue|problem)\s+(?:about|with)?\s+(\w+)\b']
    
    for pattern in medication_patterns:
        matches = re.findall(pattern, discussion, re.IGNORECASE)
        entities["medications"].extend(matches)
    
    for pattern in concern_patterns:
        matches = re.findall(pattern, discussion, re.IGNORECASE)
        entities["concerns"].extend(matches)
    
    return entities


def analyze_sentiment(discussion: str) -> str:
    """
    Analyze the sentiment of the discussion.
    In production, this would use a sentiment analysis model.
    """
    positive_words = ['interested', 'positive', 'good', 'great', 'excellent', 'agree', 'happy']
    negative_words = ['concern', 'worry', 'problem', 'issue', 'negative', 'bad', 'disagree']
    
    discussion_lower = discussion.lower()
    positive_count = sum(1 for word in positive_words if word in discussion_lower)
    negative_count = sum(1 for word in negative_words if word in discussion_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def extract_topics(discussion: str) -> list:
    """
    Extract key topics from the discussion.
    In production, this would use topic modeling.
    """
    # Simple keyword-based topic extraction
    topic_keywords = {
        "product": ['product', 'drug', 'medication', 'treatment', 'therapy'],
        "pricing": ['price', 'cost', 'budget', 'reimbursement'],
        "clinical": ['clinical', 'trial', 'study', 'efficacy', 'safety'],
        "competition": ['competitor', 'alternative', 'other'],
        "education": ['training', 'education', 'learn', 'understand']
    }
    
    discussion_lower = discussion.lower()
    topics = []
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in discussion_lower for keyword in keywords):
            topics.append(topic)
    
    return topics
