import logging
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentEditRequest,
    AgentEditResponse,
    AgentRecommendationRequest,
    AgentRecommendationResponse,
    EditModificationData,
    StructuredInteractionData,
)
from app.agents.hcp_agent import run_hcp_agent
from app.services.groq_service import extract_interaction as groq_extract_interaction
from app.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["AI Agent"])


@router.post("/chat", response_model=AgentChatResponse, status_code=status.HTTP_200_OK)
async def agent_chat(request: AgentChatRequest, db: Session = Depends(get_db)) -> AgentChatResponse:
    """
    Chat with the AI-powered HCP Agent.
    
    The agent analyzes the user's message and decides which tool to execute:
    - Log Interaction: Extracts structured data and stores in database
    - Edit Interaction: Updates existing interactions
    - Search Interactions: Retrieves previous interactions
    - Summarize Interaction: Generates meeting summaries
    - Suggest Next Action: Recommends follow-up actions
    
    When Log Interaction is selected, the agent:
    1. Uses Groq LLM (gemma2-9b-it) to extract structured data
    2. Looks up or creates the HCP record in the database
    3. Creates the Interaction record linked to the HCP
    4. Returns the interaction ID and confirmation
    
    Args:
        request: Chat request containing the user message and optional conversation history
        db: Database session for database operations
    
    Returns:
        Agent response with tool used, structured data, and reply message
    """
    try:
        logger.info(f"Received agent chat request: {request.message[:100]}...")
        
        # Convert conversation history to LangChain format if provided
        conversation_history = []
        if request.conversation_history:
            from langchain_core.messages import HumanMessage, AIMessage
            for msg in request.conversation_history:
                if msg.get("role") == "user":
                    conversation_history.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    conversation_history.append(AIMessage(content=msg.get("content", "")))
        
        # Run the LangGraph agent
        logger.info("Running LangGraph HCP Agent...")
        agent_result = run_hcp_agent(request.message, conversation_history)
        
        # Extract information from agent result
        selected_tool = agent_result.get("selected_tool", "unknown")
        reply = agent_result.get("response", "No response generated")
        tool_result = agent_result.get("tool_result", "")
        
        logger.info(f"Agent used tool: {selected_tool}")
        
        # If Log Interaction tool was used, extract structured data with Groq and store in database
        structured_data = None
        interaction_id = None
        
        if selected_tool == "log_interaction":
            logger.info("Extracting structured data with Groq LLM and storing in database...")
            try:
                # Extract structured data with Groq
                extraction_result = groq_extract_interaction(request.message)
                
                if extraction_result.get("success"):
                    extracted = extraction_result.get("data", {})
                    structured_data = StructuredInteractionData(
                        doctor_name=extracted.get("doctor_name"),
                        hospital=extracted.get("hospital"),
                        interaction_date=extracted.get("interaction_date"),
                        products_discussed=extracted.get("products_discussed"),
                        doctor_feedback=extracted.get("doctor_feedback"),
                        follow_up_date=extracted.get("follow_up_date"),
                        meeting_outcome=extracted.get("meeting_outcome"),
                        summary=extracted.get("summary")
                    )
                    
                    # Store interaction in database using the log_interaction tool
                    from app.tools.log_interaction import log_interaction
                    from datetime import datetime
                    
                    # Parse dates for database storage
                    interaction_date = None
                    if extracted.get("interaction_date"):
                        try:
                            interaction_date = extracted.get("interaction_date")
                        except:
                            interaction_date = datetime.now().isoformat()
                    
                    follow_up_date = None
                    if extracted.get("follow_up_date"):
                        try:
                            follow_up_date = extracted.get("follow_up_date")
                        except:
                            follow_up_date = None
                    
                    # Call log_interaction with database session
                    db_result = log_interaction.invoke({
                        "hcp_name": extracted.get("doctor_name") or "Unknown",
                        "discussion": request.message,
                        "interaction_type": "call",
                        "interaction_date": interaction_date,
                        "summary": extracted.get("summary"),
                        "follow_up_date": follow_up_date,
                        "hospital": extracted.get("hospital"),
                        "db": db
                    })
                    
                    if db_result.get("success"):
                        interaction_id = db_result.get("interaction_id")
                        logger.info(f"Interaction stored successfully with ID: {interaction_id}")
                        reply = f"✅ {db_result.get('message')} Interaction ID: {interaction_id}"
                    else:
                        logger.warning(f"Failed to store interaction: {db_result.get('message')}")
                        reply += f"\n\n⚠️ Note: {db_result.get('message')}"
                    
                    logger.info("Structured data extracted successfully")
                else:
                    logger.warning(f"Groq extraction failed: {extraction_result.get('error')}")
                    # Still return success but without structured data
                    reply += "\n\nNote: AI-powered extraction unavailable. Using basic processing."
                    
            except Exception as extraction_error:
                logger.error(f"Error during Groq extraction or database storage: {str(extraction_error)}")
                reply += "\n\nNote: AI-powered extraction encountered an error. Using basic processing."
        
        # Convert conversation history back to dict format for response
        response_history = None
        if agent_result.get("conversation_history"):
            response_history = []
            for msg in agent_result["conversation_history"]:
                if hasattr(msg, 'type'):
                    response_history.append({
                        "role": msg.type,
                        "content": msg.content
                    })
        
        # Build response
        response = AgentChatResponse(
            success=True,
            tool_used=selected_tool.replace("_", " ").title(),
            interaction_id=interaction_id,
            structured_data=structured_data,
            reply=reply,
            conversation_history=response_history
        )
        
        logger.info("Agent chat request completed successfully")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in agent chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in agent chat: {str(e)}", exc_info=True)
        return AgentChatResponse(
            success=False,
            tool_used=None,
            structured_data=None,
            reply="An unexpected error occurred while processing your request. Please try again.",
            error=str(e)
        )


@router.put("/edit/{interaction_id}", response_model=AgentEditResponse)
async def agent_edit(
    interaction_id: int,
    request: AgentEditRequest,
    db: Session = Depends(get_db),
) -> AgentEditResponse:
    """Extract and apply an edit request through the LangGraph HCP agent."""
    try:
        logger.info("Received agent edit request for interaction %s", interaction_id)
        agent_result = run_hcp_agent(
            request.message,
            interaction_id=interaction_id,
            db=db,
        )
        result = agent_result.get("tool_result") or {}
        updated_interaction = result.get("data") if result.get("success") else None

        return AgentEditResponse(
            success=bool(result.get("success")),
            interaction_id=interaction_id,
            modification_data=(
                EditModificationData(**updated_interaction)
                if updated_interaction
                else None
            ),
            updated_interaction=updated_interaction,
            reply=agent_result.get("response", "No response generated"),
            error=None if result.get("success") else result.get("message"),
        )
    except ValueError as e:
        logger.error("Validation error in agent edit: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request: {e}")
    except Exception as e:
        logger.error("Unexpected error in agent edit: %s", e, exc_info=True)
        return AgentEditResponse(
            success=False,
            interaction_id=interaction_id,
            reply="An unexpected error occurred while processing your edit request. Please try again.",
            error=str(e),
        )


@router.post("/recommendation", response_model=AgentRecommendationResponse)
async def agent_recommendation(
    request: AgentRecommendationRequest,
    db: Session = Depends(get_db),
) -> AgentRecommendationResponse:
    """Generate next actions from the current and previous HCP meetings."""
    if not request.interaction_id and not request.hcp_id and not request.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide interaction_id, hcp_id, or message to generate recommendations.",
        )

    from app.services.hcp_service import HCPService
    from app.services.interaction_service import InteractionService

    interaction_service = InteractionService(db)
    hcp_service = HCPService(db)
    interaction = None
    hcp_id = request.hcp_id

    if request.interaction_id:
        interaction = interaction_service.get_interaction_by_id(request.interaction_id)
        if not interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
        if hcp_id and hcp_id != interaction.hcp_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="interaction_id does not belong to the supplied hcp_id.",
            )
        hcp_id = interaction.hcp_id

    hcp = hcp_service.get_hcp_by_id(hcp_id) if hcp_id else None
    if hcp_id and not hcp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HCP not found")

    previous_interactions = []
    if hcp_id:
        previous_interactions = [
            {
                "id": meeting.id,
                "discussion": meeting.discussion,
                "summary": meeting.summary,
                "interaction_date": meeting.interaction_date.isoformat() if meeting.interaction_date else None,
                "follow_up_date": meeting.follow_up_date.isoformat() if meeting.follow_up_date else None,
            }
            for meeting in interaction_service.get_interactions_by_hcp_id(hcp_id)
            if not interaction or meeting.id != interaction.id
        ]

    discussion = request.message or (interaction.discussion if interaction else "")
    agent_result = run_hcp_agent(
        discussion,
        db=db,
        recommendation_context={
            "discussion": discussion,
            "hcp_name": hcp.doctor_name if hcp else None,
            "interaction_type": "meeting",
            "previous_interactions": previous_interactions,
        },
    )
    result = agent_result.get("tool_result") or {}
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Unable to generate recommendations."),
        )

    return AgentRecommendationResponse(
        recommendations=result.get("recommended_actions", []),
    )


@router.get("/health", status_code=status.HTTP_200_OK)
async def agent_health():
    """
    Health check endpoint for the AI Agent service.
    
    Returns:
        Status of the agent service
    """
    try:
        # Check if Groq service is available
        from app.services.groq_service import get_groq_service
        groq_service = get_groq_service()
        
        return {
            "status": "healthy",
            "service": "AI Agent",
            "groq_available": True,
            "model": groq_service.model
        }
    except Exception as e:
        logger.error(f"Agent health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "AI Agent",
            "groq_available": False,
            "error": str(e)
        }
