from typing import Dict, Any
from datetime import datetime, timedelta
from langchain_core.tools import tool
import re


@tool
def suggest_next_action(
    discussion: str,
    hcp_name: str = None,
    interaction_type: str = None,
    previous_interactions: list = None,
    sentiment: str = None
) -> Dict[str, Any]:
    """
    Recommend follow-up actions for the sales representative based on the interaction.
    
    Args:
        discussion: The discussion text from the interaction
        hcp_name: Name of the Healthcare Professional
        interaction_type: Type of interaction (call, email, meeting, visit)
        previous_interactions: List of previous interactions with this HCP
        sentiment: Sentiment of the interaction (positive, negative, neutral)
    
    Returns:
        Dictionary containing recommended next actions with priorities and timelines
    """
    # Analyze the discussion to determine context
    previous_interactions = previous_interactions or []
    context = analyze_interaction_context(discussion, sentiment)
    context["meeting_history"] = analyze_meeting_history(previous_interactions)
    
    # Generate action recommendations
    actions = generate_action_recommendations(context, hcp_name, interaction_type, previous_interactions)
    
    # Prioritize actions
    prioritized_actions = prioritize_actions(actions)
    
    return {
        "success": True,
        "message": "Next actions recommended successfully",
        "hcp_name": hcp_name,
        "context": context,
        "recommended_actions": prioritized_actions,
        "summary": generate_action_summary(prioritized_actions)
    }


def analyze_interaction_context(discussion: str, sentiment: str = None) -> Dict[str, Any]:
    """
    Analyze the context of the interaction to inform action recommendations.
    """
    discussion_lower = discussion.lower()
    
    # Determine engagement level
    engagement_indicators = {
        'high': ['interested', 'excited', 'agree', 'positive', 'great', 'excellent', 'want to', 'would like'],
        'medium': ['maybe', 'consider', 'think about', 'discuss', 'review'],
        'low': ['not interested', 'decline', 'refuse', 'concern', 'worry', 'issue']
    }
    
    engagement_level = 'medium'
    for level, indicators in engagement_indicators.items():
        if any(indicator in discussion_lower for indicator in indicators):
            engagement_level = level
            break
    
    # Identify topics discussed
    topics = []
    topic_keywords = {
        "Product": ['product', 'drug', 'medication', 'treatment'],
        "Clinical Data": ['clinical', 'trial', 'study', 'data', 'evidence'],
        "Pricing": ['price', 'cost', 'budget', 'reimbursement'],
        "Competition": ['competitor', 'alternative', 'other'],
        "Education": ['training', 'education', 'learn', 'presentation']
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in discussion_lower for keyword in keywords):
            topics.append(topic)
    
    # Check for specific requests
    requests = []
    request_patterns = [
        r'(?:request|ask|want|need)\s+(?:for|to|)\s*(?:send|provide|schedule|arrange)\s+([^.]+)',
        r'(?:would like|interested in)\s+([^.]+)'
    ]
    
    for pattern in request_patterns:
        matches = re.findall(pattern, discussion, re.IGNORECASE)
        requests.extend(matches)
    
    return {
        "discussion": discussion,
        "engagement_level": engagement_level,
        "topics_discussed": topics,
        "specific_requests": requests,
        "sentiment": sentiment or analyze_sentiment(discussion),
        "has_concerns": any(word in discussion_lower for word in ['concern', 'worry', 'issue', 'problem'])
    }


def generate_action_recommendations(context: Dict[str, Any], hcp_name: str, interaction_type: str, previous_interactions: list) -> list:
    """
    Generate action recommendations based on context.
    """
    actions = []
    engagement = context["engagement_level"]
    sentiment = context["sentiment"]
    topics = context["topics_discussed"]
    requests = context["specific_requests"]
    has_concerns = context["has_concerns"]
    
    history_text = " ".join(
        f"{meeting.get('discussion', '')} {meeting.get('summary', '')}"
        for meeting in previous_interactions
    ).lower()
    combined_text = f"{context['discussion']} {history_text}".lower()

    # Handle explicit sample requests before generic recommendations. This
    # produces a concrete, field-ready action for the sales representative.
    if "sample" in combined_text:
        actions.extend([
            {
                "action": "Send 10 sample packs",
                "priority": "high",
                "timeline": "Within 2 days",
                "description": f"Send 10 sample packs to {hcp_name or 'the HCP'}.",
                "reason": "The HCP requested samples during a recent meeting."
            },
            {
                "action": "Schedule follow-up in 7 days",
                "priority": "high",
                "timeline": "Within 7 days",
                "description": f"Confirm receipt of the samples with {hcp_name or 'the HCP'} and discuss feedback.",
                "reason": "A timely follow-up helps convert the sample request into product feedback."
            },
            {
                "action": "Share clinical study",
                "priority": "medium",
                "timeline": "Within 2 days",
                "description": "Share the most relevant clinical study and product evidence with the samples.",
                "reason": "Clinical evidence supports informed evaluation of the samples."
            },
        ])

    # High engagement - move forward
    if engagement == "high" and sentiment == "positive":
        actions.append({
            "action": "Schedule follow-up meeting",
            "priority": "high",
            "timeline": "Within 1 week",
            "description": f"Schedule a follow-up meeting with {hcp_name or 'the HCP'} to discuss next steps",
            "reason": "High engagement and positive sentiment indicate readiness to move forward"
        })
        
        actions.append({
            "action": "Send detailed information",
            "priority": "high",
            "timeline": "Within 2 days",
            "description": "Send detailed product information and relevant clinical data",
            "reason": "Support the HCP's interest with comprehensive information"
        })
    
    # Medium engagement - nurture
    elif engagement == "medium":
        actions.append({
            "action": "Send follow-up materials",
            "priority": "medium",
            "timeline": "Within 3-5 days",
            "description": "Send relevant materials based on topics discussed",
            "reason": "Provide additional information to support decision-making"
        })
        
        actions.append({
            "action": "Schedule check-in call",
            "priority": "medium",
            "timeline": "Within 2 weeks",
            "description": f"Schedule a check-in call with {hcp_name or 'the HCP'}",
            "reason": "Maintain engagement and address any questions"
        })
    
    # Low engagement or concerns - address barriers
    elif engagement == "low" or has_concerns:
        actions.append({
            "action": "Address concerns directly",
            "priority": "high",
            "timeline": "Within 1 week",
            "description": "Schedule a focused discussion to address specific concerns",
            "reason": "Proactively address barriers to engagement"
        })
        
        actions.append({
            "action": "Provide additional evidence",
            "priority": "medium",
            "timeline": "Within 3 days",
            "description": "Send additional clinical data or case studies addressing concerns",
            "reason": "Build confidence with evidence-based information"
        })
    
    # Handle specific requests
    for request in requests:
        actions.append({
            "action": f"Fulfill request: {request[:50]}",
            "priority": "high",
            "timeline": "Within 2 days",
            "description": f"Send/provide {request}",
            "reason": "Direct request from HCP"
        })
    
    # Topic-specific recommendations
    if "Clinical Data" in topics:
        actions.append({
            "action": "Share clinical evidence",
            "priority": "medium",
            "timeline": "Within 1 week",
            "description": "Share relevant clinical trial data and case studies",
            "reason": "Support clinical discussion with evidence"
        })
    
    if "Pricing" in topics:
        actions.append({
            "action": "Provide pricing information",
            "priority": "medium",
            "timeline": "Within 1 week",
            "description": "Provide detailed pricing and reimbursement information",
            "reason": "Address economic considerations"
        })
    
    if "Education" in topics:
        actions.append({
            "action": "Offer educational resources",
            "priority": "low",
            "timeline": "Within 2 weeks",
            "description": "Offer educational materials or training sessions",
            "reason": "Support ongoing education and awareness"
        })
    
    # Default action if no specific recommendations
    if not actions:
        actions.append({
            "action": "Schedule follow-up contact",
            "priority": "medium",
            "timeline": "Within 2 weeks",
            "description": f"Schedule a follow-up contact with {hcp_name or 'the HCP'}",
            "reason": "Maintain relationship and check for new opportunities"
        })
    
    # Remove duplicate recommendations while preserving priority order.
    unique_actions = []
    seen_actions = set()
    for action in actions:
        if action["action"] not in seen_actions:
            unique_actions.append(action)
            seen_actions.add(action["action"])

    return unique_actions


def analyze_meeting_history(previous_interactions: list) -> Dict[str, Any]:
    """Summarize prior meetings so recommendations account for open requests."""
    recent_meetings = previous_interactions[:10]
    text = " ".join(
        f"{meeting.get('discussion', '')} {meeting.get('summary', '')}"
        for meeting in recent_meetings
    ).lower()

    return {
        "meeting_count": len(recent_meetings),
        "requested_samples": "sample" in text,
        "requested_clinical_data": any(term in text for term in ("clinical", "study", "trial", "evidence")),
        "discussed_pricing": any(term in text for term in ("price", "pricing", "cost", "reimbursement")),
    }


def prioritize_actions(actions: list) -> list:
    """
    Prioritize actions based on priority and timeline.
    """
    priority_order = {"high": 0, "medium": 1, "low": 2}
    
    # Sort by priority, then by timeline
    sorted_actions = sorted(
        actions,
        key=lambda x: (priority_order.get(x["priority"], 3), x["timeline"])
    )
    
    return sorted_actions


def analyze_sentiment(discussion: str) -> str:
    """
    Analyze the sentiment of the discussion.
    """
    positive_words = ['interested', 'positive', 'good', 'great', 'excellent', 'agree', 'happy', 'pleased']
    negative_words = ['concern', 'worry', 'problem', 'issue', 'negative', 'bad', 'disagree', 'unhappy']
    
    discussion_lower = discussion.lower()
    positive_count = sum(1 for word in positive_words if word in discussion_lower)
    negative_count = sum(1 for word in negative_words if word in discussion_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def generate_action_summary(actions: list) -> str:
    """
    Generate a summary of recommended actions.
    """
    if not actions:
        return "No specific actions recommended at this time."
    
    high_priority = [a for a in actions if a["priority"] == "high"]
    medium_priority = [a for a in actions if a["priority"] == "medium"]
    low_priority = [a for a in actions if a["priority"] == "low"]
    
    summary_parts = []
    
    if high_priority:
        summary_parts.append(f"Complete {len(high_priority)} high-priority action(s)")
    if medium_priority:
        summary_parts.append(f"Complete {len(medium_priority)} medium-priority action(s)")
    if low_priority:
        summary_parts.append(f"Consider {len(low_priority)} low-priority action(s)")
    
    return f"Recommended: {', '.join(summary_parts)}. Focus on high-priority actions first."
