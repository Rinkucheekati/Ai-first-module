from typing import Dict, Any
from langchain_core.tools import tool
import re


@tool
def summarize_interaction(
    discussion: str,
    hcp_name: str = None,
    interaction_type: str = None,
    include_key_points: bool = True,
    include_outcome: bool = True
) -> Dict[str, Any]:
    """
    Generate a concise medical meeting summary from the interaction discussion.
    
    Args:
        discussion: The full discussion text from the interaction
        hcp_name: Name of the Healthcare Professional (optional)
        interaction_type: Type of interaction (call, email, meeting, visit)
        include_key_points: Whether to include extracted key points
        include_outcome: Whether to include the interaction outcome
    
    Returns:
        Dictionary containing the structured summary
    """
    # Generate the main summary
    main_summary = generate_main_summary(discussion)
    
    # Extract key points
    key_points = []
    if include_key_points:
        key_points = extract_key_points(discussion)
    
    # Determine outcome
    outcome = None
    if include_outcome:
        outcome = determine_outcome(discussion)
    
    # Build the structured summary
    structured_summary = {
        "hcp_name": hcp_name,
        "interaction_type": interaction_type,
        "main_summary": main_summary,
        "key_points": key_points,
        "outcome": outcome,
        "sentiment": analyze_sentiment(discussion),
        "topics_discussed": extract_topics(discussion),
        "action_items": extract_action_items(discussion)
    }
    
    return {
        "success": True,
        "message": "Summary generated successfully",
        "summary": structured_summary
    }


def generate_main_summary(discussion: str) -> str:
    """
    Generate a concise main summary from the discussion.
    """
    # Remove extra whitespace
    discussion = ' '.join(discussion.split())
    
    # Extract key sentences
    sentences = re.split(r'[.!?]+', discussion)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= 2:
        return discussion[:200] + "..." if len(discussion) > 200 else discussion
    
    # Take first and last sentences for context
    first_sentence = sentences[0]
    last_sentence = sentences[-1]
    
    # Build summary
    summary = f"{first_sentence}. {last_sentence}."
    
    if len(summary) > 250:
        summary = summary[:247] + "..."
    
    return summary


def extract_key_points(discussion: str) -> list:
    """
    Extract key points from the discussion.
    """
    key_points = []
    
    # Pattern for key indicators
    key_indicators = [
        r'(?:important|key|notable|significant|main)\s+(?:point|topic|aspect|concern|issue)\s+(?:is|was|:)\s+([^.]+)',
        r'(?:discussed|mentioned|talked about)\s+([^.]+)',
        r'(?:focused|emphasized|highlighted)\s+(?:on|)\s+([^.]+)'
    ]
    
    for pattern in key_indicators:
        matches = re.findall(pattern, discussion, re.IGNORECASE)
        for match in matches:
            point = match.strip()
            if len(point) > 10 and len(point) < 150:
                key_points.append(point)
    
    # Limit to top 5 key points
    return key_points[:5]


def determine_outcome(discussion: str) -> str:
    """
    Determine the outcome of the interaction based on discussion content.
    """
    discussion_lower = discussion.lower()
    
    # Positive outcomes
    positive_outcomes = {
        'agreed to meet': 'Scheduled follow-up meeting',
        'interested in': 'Expressed interest',
        'agreed to': 'Reached agreement',
        'will try': 'Willing to try',
        'positive response': 'Positive response received',
        'confirmed': 'Confirmation received'
    }
    
    # Negative outcomes
    negative_outcomes = {
        'not interested': 'Not interested',
        'declined': 'Declined',
        'refused': 'Refused',
        'concerns about': 'Has concerns',
        'needs more time': 'Needs more time to decide'
    }
    
    # Check for positive outcomes
    for indicator, outcome in positive_outcomes.items():
        if indicator in discussion_lower:
            return outcome
    
    # Check for negative outcomes
    for indicator, outcome in negative_outcomes.items():
        if indicator in discussion_lower:
            return outcome
    
    # Default outcome
    return 'Discussion completed - follow-up required'


def analyze_sentiment(discussion: str) -> str:
    """
    Analyze the sentiment of the discussion.
    """
    positive_words = ['interested', 'positive', 'good', 'great', 'excellent', 'agree', 'happy', 'pleased', 'satisfied']
    negative_words = ['concern', 'worry', 'problem', 'issue', 'negative', 'bad', 'disagree', 'unhappy', 'dissatisfied']
    
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
        "Product Information": ['product', 'drug', 'medication', 'treatment', 'therapy', 'efficacy', 'safety'],
        "Pricing & Reimbursement": ['price', 'cost', 'budget', 'reimbursement', 'coverage', 'insurance'],
        "Clinical Data": ['clinical', 'trial', 'study', 'data', 'evidence', 'research'],
        "Competition": ['competitor', 'alternative', 'other', 'comparison'],
        "Education & Training": ['training', 'education', 'learn', 'understand', 'presentation'],
        "Patient Outcomes": ['patient', 'outcome', 'result', 'improvement', 'benefit']
    }
    
    discussion_lower = discussion.lower()
    topics = []
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in discussion_lower for keyword in keywords):
            topics.append(topic)
    
    return topics


def extract_action_items(discussion: str) -> list:
    """
    Extract action items from the discussion.
    """
    action_items = []
    
    # Pattern for action items
    action_patterns = [
        r'(?:will|shall|going to|need to)\s+(?:send|provide|schedule|arrange|follow up|contact|call|email)\s+([^.]+)',
        r'(?:please|kindly)\s+(?:send|provide|schedule|arrange)\s+([^.]+)',
        r'(?:next steps?|action items?|follow[- ]up)\s*(?:is|:|include)\s*([^.]+)'
    ]
    
    for pattern in action_patterns:
        matches = re.findall(pattern, discussion, re.IGNORECASE)
        for match in matches:
            action = match.strip()
            if len(action) > 5 and len(action) < 200:
                action_items.append(action)
    
    # Limit to top 5 action items
    return action_items[:5]
