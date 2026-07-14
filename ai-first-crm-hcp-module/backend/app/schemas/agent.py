from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class AgentChatRequest(BaseModel):
    """Request model for agent chat endpoint."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message to the AI agent")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional conversation history for context"
    )


class AgentEditRequest(BaseModel):
    """Request model for agent edit endpoint."""
    message: str = Field(..., min_length=1, max_length=5000, description="User's edit request")


class StructuredInteractionData(BaseModel):
    """Structured data extracted from interaction."""
    doctor_name: Optional[str] = Field(None, description="Name of the doctor/HCP")
    hospital: Optional[str] = Field(None, description="Hospital or organization name")
    interaction_date: Optional[str] = Field(None, description="Date of the interaction")
    products_discussed: Optional[List[str]] = Field(None, description="List of products discussed")
    doctor_feedback: Optional[str] = Field(None, description="Feedback from the doctor")
    follow_up_date: Optional[str] = Field(None, description="Date for follow-up")
    meeting_outcome: Optional[str] = Field(None, description="Outcome of the meeting")
    summary: Optional[str] = Field(None, description="Summary of the interaction")


class EditModificationData(BaseModel):
    """Data extracted from edit request."""
    discussion: Optional[str] = Field(None, description="Updated discussion text")
    summary: Optional[str] = Field(None, description="Updated summary")
    follow_up_date: Optional[str] = Field(None, description="Updated follow-up date")
    interaction_date: Optional[str] = Field(None, description="Updated interaction date")


class AgentChatResponse(BaseModel):
    """Response model for agent chat endpoint."""
    success: bool = Field(..., description="Whether the request was successful")
    tool_used: Optional[str] = Field(None, description="The tool that was executed")
    interaction_id: Optional[int] = Field(None, description="ID of the created interaction (if applicable)")
    structured_data: Optional[StructuredInteractionData] = Field(None, description="Structured data extracted from interaction")
    reply: str = Field(..., description="The agent's response message")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(None, description="Updated conversation history")
    error: Optional[str] = Field(None, description="Error message if the request failed")


class AgentEditResponse(BaseModel):
    """Response model for agent edit endpoint."""
    success: bool = Field(..., description="Whether the edit was successful")
    interaction_id: int = Field(..., description="ID of the updated interaction")
    modification_data: Optional[EditModificationData] = Field(None, description="Extracted modification data")
    updated_interaction: Optional[Dict[str, Any]] = Field(None, description="Updated interaction data")
    reply: str = Field(..., description="The agent's response message")
    error: Optional[str] = Field(None, description="Error message if the request failed")


class AgentRecommendationRequest(BaseModel):
    """Request a recommendation based on an interaction and its meeting history."""
    interaction_id: Optional[int] = Field(None, gt=0)
    hcp_id: Optional[int] = Field(None, gt=0)
    message: Optional[str] = Field(None, min_length=1, max_length=5000)


class Recommendation(BaseModel):
    action: str
    priority: str
    timeline: str
    description: str
    reason: str


class AgentRecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
