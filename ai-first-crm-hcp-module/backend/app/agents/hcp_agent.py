from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from app.agents.state import AgentState
from app.tools.log_interaction import log_interaction
from app.tools.edit_interaction import edit_interaction
from app.tools.search_interactions import search_interactions
from app.tools.summarize_interaction import summarize_interaction
from app.tools.suggest_next_action import suggest_next_action
from app.services.groq_service import (
    extract_edit_modifications as groq_extract_edit_modifications,
    extract_interaction as groq_extract_interaction,
)


# Define the tools
tools = [log_interaction, edit_interaction, search_interactions, summarize_interaction, suggest_next_action]
tool_node = ToolNode(tools)


def analyze_user_input(state: AgentState) -> AgentState:
    """
    Analyze the user's input and determine which tool to use.
    This is the decision-making node of the agent.
    """
    user_input = state["user_input"].lower()
    
    # Determine the appropriate tool based on user intent
    if state.get("recommendation_context") is not None:
        state["selected_tool"] = "suggest_next_action"
    elif state.get("interaction_id") is not None:
        # A route with an interaction ID explicitly requests an edit, even if
        # the natural-language instruction does not contain an edit keyword.
        state["selected_tool"] = "edit_interaction"
    elif any(keyword in user_input for keyword in ["log", "record", "new interaction", "create interaction", "add interaction"]):
        state["selected_tool"] = "log_interaction"
    elif any(keyword in user_input for keyword in ["edit", "update", "modify", "change interaction"]):
        state["selected_tool"] = "edit_interaction"
    elif any(keyword in user_input for keyword in ["search", "find", "retrieve", "get interactions", "previous interactions", "history"]):
        state["selected_tool"] = "search_interactions"
    elif any(keyword in user_input for keyword in ["summarize", "summary", "summarize interaction", "meeting summary"]):
        state["selected_tool"] = "summarize_interaction"
    elif any(keyword in user_input for keyword in ["suggest", "recommend", "next action", "follow-up", "what should i do"]):
        state["selected_tool"] = "suggest_next_action"
    else:
        # Default to log interaction for conversational logging
        state["selected_tool"] = "log_interaction"
    
    # Add analysis to conversation history
    state["conversation_history"].append(
        AIMessage(content=f"Analyzing input... Selected tool: {state['selected_tool']}")
    )
    
    return state


def route_to_tool(state: AgentState) -> Literal["log_interaction", "edit_interaction", "search_interactions", "summarize_interaction", "suggest_next_action", "end"]:
    """
    Route to the appropriate tool based on the selected tool.
    """
    selected_tool = state["selected_tool"]
    
    if selected_tool == "log_interaction":
        return "log_interaction"
    elif selected_tool == "edit_interaction":
        return "edit_interaction"
    elif selected_tool == "search_interactions":
        return "search_interactions"
    elif selected_tool == "summarize_interaction":
        return "summarize_interaction"
    elif selected_tool == "suggest_next_action":
        return "suggest_next_action"
    else:
        return "end"


def execute_log_interaction(state: AgentState) -> AgentState:
    """
    Execute the log_interaction tool using Groq LLM for structured extraction.
    """
    user_input = state["user_input"]
    
    # Use Groq LLM to extract structured information
    try:
        extraction_result = groq_extract_interaction(user_input)
        
        if extraction_result.get("success"):
            extracted_data = extraction_result["data"]
            
            # Map extracted data to log_interaction parameters
            hcp_name = extracted_data.get("doctor_name") or extract_hcp_name(user_input)
            discussion = user_input
            interaction_type = "call"  # Default, could be enhanced with LLM detection
            interaction_date = extracted_data.get("interaction_date")
            summary = extracted_data.get("summary")
            follow_up_date = extracted_data.get("follow_up_date")
            
            # Call the tool with LLM-extracted data
            result = log_interaction.invoke({
                "hcp_name": hcp_name or "Unknown HCP",
                "discussion": discussion,
                "interaction_type": interaction_type,
                "interaction_date": interaction_date,
                "summary": summary,
                "follow_up_date": follow_up_date
            })
            
            # Enhance response with LLM-extracted insights
            state["tool_result"] = str(result)
            state["response"] = format_log_response_with_extraction(result, extracted_data)
        else:
            # Fallback to simple extraction if Groq fails
            hcp_name = extract_hcp_name(user_input)
            result = log_interaction.invoke({
                "hcp_name": hcp_name or "Unknown HCP",
                "discussion": user_input,
                "interaction_type": "call"
            })
            state["tool_result"] = str(result)
            state["response"] = format_log_response(result)
            state["response"] += f"\n\n⚠️ Note: AI extraction unavailable. Using basic extraction."
            
    except Exception as e:
        # Fallback to simple extraction on error
        hcp_name = extract_hcp_name(user_input)
        result = log_interaction.invoke({
            "hcp_name": hcp_name or "Unknown HCP",
            "discussion": user_input,
            "interaction_type": "call"
        })
        state["tool_result"] = str(result)
        state["response"] = format_log_response(result)
        state["response"] += f"\n\n⚠️ AI extraction error: {str(e)}. Using basic extraction."
    
    # Add to conversation history
    state["conversation_history"].append(AIMessage(content=state["response"]))
    
    return state


def execute_edit_interaction(state: AgentState) -> AgentState:
    """
    Execute the edit_interaction tool.
    """
    user_input = state["user_input"]
    
    # The dedicated edit endpoint supplies the ID in graph state. Chat-based
    # edits still support extracting it from the user's wording.
    interaction_id = state.get("interaction_id") or extract_interaction_id(user_input)
    
    if not interaction_id:
        state["response"] = "Please provide the interaction ID you want to edit."
        state["conversation_history"].append(AIMessage(content=state["response"]))
        return state
    
    try:
        extraction_result = groq_extract_edit_modifications(user_input)
    except Exception as exc:
        state["tool_result"] = {
            "success": False,
            "interaction_id": interaction_id,
            "message": f"Could not extract changes from the edit request: {exc}",
        }
        state["response"] = "I couldn't identify the requested changes. Please specify the field and its new value."
        state["conversation_history"].append(AIMessage(content=state["response"]))
        return state

    modifications = extraction_result.get("data", {}) if extraction_result.get("success") else {}

    # Do not update a record when no edit could be extracted.
    if not any(modifications.values()):
        state["tool_result"] = {
            "success": False,
            "interaction_id": interaction_id,
            "message": "No changes were found in the edit request."
        }
        state["response"] = "Please specify at least one field to change (discussion, summary, interaction date, or follow-up date)."
        state["conversation_history"].append(AIMessage(content=state["response"]))
        return state

    # Call the tool with the request-scoped database session when available.
    result = edit_interaction.invoke({
        "interaction_id": interaction_id,
        "discussion": modifications.get("discussion"),
        "summary": modifications.get("summary"),
        "follow_up_date": modifications.get("follow_up_date"),
        "interaction_date": modifications.get("interaction_date"),
        "db": state.get("db"),
    })
    
    state["tool_result"] = result
    state["response"] = format_edit_response(result)
    
    state["conversation_history"].append(AIMessage(content=state["response"]))
    
    return state


def execute_search_interactions(state: AgentState) -> AgentState:
    """
    Execute the search_interactions tool.
    """
    user_input = state["user_input"]
    
    # Extract search parameters (simplified)
    hcp_name = extract_hcp_name(user_input)
    
    # Call the tool
    result = search_interactions.invoke({
        "hcp_name": hcp_name,
        "limit": 10
    })
    
    state["tool_result"] = str(result)
    state["response"] = format_search_response(result)
    
    state["conversation_history"].append(AIMessage(content=state["response"]))
    
    return state


def execute_summarize_interaction(state: AgentState) -> AgentState:
    """
    Execute the summarize_interaction tool.
    """
    user_input = state["user_input"]
    
    # Extract discussion text
    discussion = extract_discussion(user_input)
    hcp_name = extract_hcp_name(user_input)
    
    # Call the tool
    result = summarize_interaction.invoke({
        "discussion": discussion,
        "hcp_name": hcp_name,
        "include_key_points": True,
        "include_outcome": True
    })
    
    state["tool_result"] = str(result)
    state["response"] = format_summarize_response(result)
    
    state["conversation_history"].append(AIMessage(content=state["response"]))
    
    return state


def execute_suggest_next_action(state: AgentState) -> AgentState:
    """
    Execute the suggest_next_action tool.
    """
    user_input = state["user_input"]
    
    # The recommendation endpoint supplies the current meeting and prior
    # interaction history. Chat requests continue to work without context.
    recommendation_context = state.get("recommendation_context") or {}
    discussion = recommendation_context.get("discussion") or extract_discussion(user_input)
    hcp_name = recommendation_context.get("hcp_name") or extract_hcp_name(user_input)
    
    # Call the tool
    result = suggest_next_action.invoke({
        "discussion": discussion,
        "hcp_name": hcp_name,
        "interaction_type": recommendation_context.get("interaction_type", "call"),
        "previous_interactions": recommendation_context.get("previous_interactions", []),
    })
    
    state["tool_result"] = result
    state["response"] = format_suggest_response(result)
    
    state["conversation_history"].append(AIMessage(content=state["response"]))
    
    return state


def format_log_response(result: dict) -> str:
    """Format the log interaction response for the user."""
    if result.get("success"):
        data = result.get("data", {})
        return f"""
✅ Interaction logged successfully!

**HCP:** {data.get('hcp_name', 'Unknown')}
**Type:** {data.get('interaction_type', 'call')}
**Date:** {data.get('interaction_date', 'N/A')}
**Summary:** {data.get('summary', 'N/A')}
**Sentiment:** {data.get('sentiment', 'neutral')}
**Topics:** {', '.join(data.get('key_topics', []))}

The interaction has been prepared for database storage. Would you like to add any additional details or log another interaction?
"""
    else:
        return f"❌ Failed to log interaction: {result.get('message', 'Unknown error')}"


def format_log_response_with_extraction(result: dict, extracted_data: dict) -> str:
    """Format the log interaction response with LLM-extracted insights."""
    if result.get("success"):
        data = result.get("data", {})
        
        response = f"""
✅ Interaction logged successfully with AI-powered extraction!

**HCP:** {extracted_data.get('doctor_name') or data.get('hcp_name', 'Unknown')}
**Hospital:** {extracted_data.get('hospital') or 'N/A'}
**Type:** {data.get('interaction_type', 'call')}
**Date:** {extracted_data.get('interaction_date') or data.get('interaction_date', 'N/A')}
"""
        
        if extracted_data.get('products_discussed'):
            response += f"**Products Discussed:** {', '.join(extracted_data.get('products_discussed', []))}\n"
        
        if extracted_data.get('doctor_feedback'):
            response += f"**Doctor Feedback:** {extracted_data.get('doctor_feedback')}\n"
        
        response += f"""
**Summary:** {extracted_data.get('summary') or data.get('summary', 'N/A')}
**Meeting Outcome:** {extracted_data.get('meeting_outcome') or 'N/A'}
**Follow-up Date:** {extracted_data.get('follow_up_date') or 'N/A'}

**AI-Extracted Insights:**
- Sentiment: {data.get('sentiment', 'neutral')}
- Topics: {', '.join(data.get('key_topics', []))}
- Entities: {data.get('extracted_entities', {})}

The interaction has been prepared for database storage with enhanced AI extraction. Would you like to add any additional details or log another interaction?
"""
        return response
    else:
        return f"❌ Failed to log interaction: {result.get('message', 'Unknown error')}"


def format_edit_response(result: dict) -> str:
    """Format the edit interaction response for the user."""
    if result.get("success"):
        return f"""
✅ Interaction updated successfully!

**Interaction ID:** {result.get('data', {}).get('interaction_id', 'Unknown')}
**Changes:** {', '.join(result.get('data', {}).keys())}

The interaction has been updated. Would you like to make additional changes or perform another action?
"""
    else:
        return f"❌ Failed to update interaction: {result.get('message', 'Unknown error')}"


def format_search_response(result: dict) -> str:
    """Format the search response for the user."""
    if result.get("success"):
        results = result.get("results", [])
        total = result.get("total", 0)
        
        if total == 0:
            return "No interactions found matching your criteria."
        
        response = f"📋 Found {total} interaction(s):\n\n"
        for i, interaction in enumerate(results[:5], 1):
            response += f"""
**{i}.** {interaction.get('hcp_name', 'Unknown')}
   - Type: {interaction.get('interaction_type', 'N/A')}
   - Date: {interaction.get('interaction_date', 'N/A')}
   - Summary: {interaction.get('summary', 'N/A')}
   - Sentiment: {interaction.get('sentiment', 'neutral')}
"""
        
        if total > 5:
            response += f"\n... and {total - 5} more interactions."
        
        response += "\n\nWould you like to view more details or perform another action?"
        return response
    else:
        return f"❌ Search failed: {result.get('message', 'Unknown error')}"


def format_summarize_response(result: dict) -> str:
    """Format the summarize response for the user."""
    if result.get("success"):
        summary = result.get("summary", {})
        return f"""
📝 **Interaction Summary**

**HCP:** {summary.get('hcp_name', 'Unknown')}
**Type:** {summary.get('interaction_type', 'N/A')}

**Main Summary:**
{summary.get('main_summary', 'N/A')}

**Key Points:**
{chr(10).join(f"• {point}" for point in summary.get('key_points', []))}

**Outcome:** {summary.get('outcome', 'N/A')}
**Sentiment:** {summary.get('sentiment', 'neutral')}

**Topics Discussed:**
{', '.join(summary.get('topics_discussed', []))}

**Action Items:**
{chr(10).join(f"• {item}" for item in summary.get('action_items', []))}

Would you like to log this interaction or perform another action?
"""
    else:
        return f"❌ Failed to generate summary: {result.get('message', 'Unknown error')}"


def format_suggest_response(result: dict) -> str:
    """Format the suggest next action response for the user."""
    if result.get("success"):
        actions = result.get("recommended_actions", [])
        summary = result.get("summary", "")
        
        response = f"""
🎯 **Recommended Next Actions**

**HCP:** {result.get('hcp_name', 'Unknown')}
**Engagement Level:** {result.get('context', {}).get('engagement_level', 'N/A')}
**Sentiment:** {result.get('context', {}).get('sentiment', 'neutral')}

**Actions:**
"""
        for i, action in enumerate(actions, 1):
            response += f"""
**{i}.** {action.get('action', 'Unknown')}
   - Priority: {action.get('priority', 'N/A')}
   - Timeline: {action.get('timeline', 'N/A')}
   - Description: {action.get('description', 'N/A')}
   - Reason: {action.get('reason', 'N/A')}
"""
        
        response += f"\n**Summary:** {summary}\n\nWould you like to proceed with any of these actions or perform another task?"
        return response
    else:
        return f"❌ Failed to generate recommendations: {result.get('message', 'Unknown error')}"


# Helper functions for parameter extraction (simplified - in production, use LLM)
def extract_hcp_name(text: str) -> str:
    """Extract HCP name from text (simplified)."""
    # In production, use proper NER/LLM
    import re
    patterns = [
        r'(?:with|for|to)\s+Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'(?:with|for|to)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


def extract_interaction_id(text: str) -> int:
    """Extract interaction ID from text (simplified)."""
    import re
    match = re.search(r'(?:interaction|id)\s*(?:#|:)?\s*(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_discussion(text: str) -> str:
    """Extract discussion text from user input."""
    # Remove common prefixes to get the actual discussion
    prefixes = [
        r'log interaction with',
        r'edit interaction',
        r'summarize',
        r'suggest next action for',
        r'search interactions for'
    ]
    
    import re
    for prefix in prefixes:
        text = re.sub(prefix, '', text, flags=re.IGNORECASE)
    
    return text.strip()


# Build the graph
def build_hcp_agent_graph():
    """
    Build the LangGraph StateGraph for the HCP Agent.
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze_input", analyze_user_input)
    workflow.add_node("log_interaction", execute_log_interaction)
    workflow.add_node("edit_interaction", execute_edit_interaction)
    workflow.add_node("search_interactions", execute_search_interactions)
    workflow.add_node("summarize_interaction", execute_summarize_interaction)
    workflow.add_node("suggest_next_action", execute_suggest_next_action)
    
    # Set the entry point
    workflow.set_entry_point("analyze_input")
    
    # Add conditional edges from analyze_input to tool nodes
    workflow.add_conditional_edges(
        "analyze_input",
        route_to_tool,
        {
            "log_interaction": "log_interaction",
            "edit_interaction": "edit_interaction",
            "search_interactions": "search_interactions",
            "summarize_interaction": "summarize_interaction",
            "suggest_next_action": "suggest_next_action",
            "end": END
        }
    )
    
    # Add edges from tool nodes to END
    workflow.add_edge("log_interaction", END)
    workflow.add_edge("edit_interaction", END)
    workflow.add_edge("search_interactions", END)
    workflow.add_edge("summarize_interaction", END)
    workflow.add_edge("suggest_next_action", END)
    
    # Compile the graph
    return workflow.compile()


# Create the agent instance
hcp_agent = build_hcp_agent_graph()


def run_hcp_agent(
    user_input: str,
    conversation_history: list = None,
    interaction_id: int = None,
    db=None,
    recommendation_context: dict = None,
) -> dict:
    """
    Run the HCP agent with the given user input.
    
    Args:
        user_input: The user's input message
        conversation_history: Optional list of previous messages
    
    Returns:
        The final state after agent execution
    """
    if conversation_history is None:
        conversation_history = []
    
    # Initialize the state
    initial_state = {
        "user_input": user_input,
        "conversation_history": conversation_history,
        "selected_tool": "",
        "tool_result": None,
        "response": "",
        "hcp_id": None,
        "interaction_id": interaction_id,
        "db": db,
        "recommendation_context": recommendation_context,
    }
    
    # Add user message to history
    initial_state["conversation_history"].append(HumanMessage(content=user_input))
    
    # Run the agent
    final_state = hcp_agent.invoke(initial_state)
    
    return final_state


if __name__ == "__main__":
    # Test the agent
    print("Testing HCP Agent...")
    
    test_inputs = [
        "Log interaction with Dr. Sarah Johnson. We discussed the new product features and she expressed strong interest.",
        "Search interactions for Dr. Michael Chen",
        "Summarize the interaction: Discussed clinical trial data with Dr. Johnson. She was impressed with the efficacy results.",
        "Suggest next action for Dr. Emily Davis. The meeting went well and she wants to schedule a demo.",
        "Edit interaction 123 with updated discussion: Added information about pricing concerns."
    ]
    
    for test_input in test_inputs:
        print(f"\n{'='*60}")
        print(f"User: {test_input}")
        print(f"{'='*60}")
        
        result = run_hcp_agent(test_input)
        print(f"Agent: {result['response']}")
