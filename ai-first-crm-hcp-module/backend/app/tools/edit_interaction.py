from typing import Dict, Any
from datetime import datetime
from langchain_core.tools import tool
from sqlalchemy.orm import Session
import re

from app.services.interaction_service import InteractionService
from app.schemas.interaction import InteractionUpdate


@tool
def edit_interaction(
    interaction_id: int,
    discussion: str = None,
    summary: str = None,
    follow_up_date: str = None,
    interaction_date: str = None,
    db: Session = None
) -> Dict[str, Any]:
    """
    Update an existing interaction with new information in the database.
    
    Args:
        interaction_id: The ID of the interaction to update
        discussion: Updated discussion notes
        summary: Updated summary
        follow_up_date: Updated follow-up date (ISO format)
        interaction_date: Updated interaction date (ISO format)
        db: Database session for database operations
    
    Returns:
        Dictionary containing the updated interaction data
    """
    if db is None:
        return {
            "success": False,
            "interaction_id": interaction_id,
            "message": "Database session not provided. Cannot update interaction."
        }
    
    try:
        # Parse interaction date if provided
        parsed_interaction_date = None
        if interaction_date:
            try:
                parsed_interaction_date = datetime.fromisoformat(interaction_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                parsed_interaction_date = None
        
        # Parse follow-up date if provided
        parsed_follow_up = None
        if follow_up_date:
            try:
                parsed_follow_up = datetime.fromisoformat(follow_up_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                parsed_follow_up = None
        
        # Initialize service
        interaction_service = InteractionService(db)
        
        # Build update data with only provided fields
        update_data = InteractionUpdate()
        
        if discussion is not None:
            update_data.discussion = discussion.strip()
            # Auto-generate summary if discussion is updated but summary is not
            if summary is None:
                update_data.summary = generate_summary(discussion)
        
        if summary is not None:
            update_data.summary = summary.strip()
        
        if parsed_follow_up:
            update_data.follow_up_date = parsed_follow_up
        
        if parsed_interaction_date:
            update_data.interaction_date = parsed_interaction_date
        
        # Update the interaction in database
        updated_interaction = interaction_service.update_interaction(interaction_id, update_data)
        
        if updated_interaction is None:
            return {
                "success": False,
                "interaction_id": interaction_id,
                "message": f"Interaction {interaction_id} not found"
            }
        
        # Commit the transaction
        db.commit()
        
        return {
            "success": True,
            "interaction_id": interaction_id,
            "message": f"Interaction {interaction_id} updated successfully",
            "data": {
                "id": updated_interaction.id,
                "hcp_id": updated_interaction.hcp_id,
                "interaction_date": updated_interaction.interaction_date.isoformat() if updated_interaction.interaction_date else None,
                "discussion": updated_interaction.discussion,
                "summary": updated_interaction.summary,
                "follow_up_date": updated_interaction.follow_up_date.isoformat() if updated_interaction.follow_up_date else None
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "interaction_id": interaction_id,
            "message": f"Failed to update interaction: {str(e)}"
        }


def generate_summary(discussion: str) -> str:
    """
    Generate a concise summary from the discussion text.
    """
    sentences = re.split(r'[.!?]+', discussion)
    summary_sentences = [s.strip() for s in sentences if s.strip()][:2]
    summary = ' '.join(summary_sentences)
    
    if len(summary) > 150:
        summary = summary[:147] + "..."
    
    return summary if summary else discussion[:150]


def extract_entities(discussion: str) -> Dict[str, list]:
    """
    Extract entities from the discussion text.
    """
    entities = {
        "medications": [],
        "products": [],
        "concerns": [],
        "outcomes": []
    }
    
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
    """
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
