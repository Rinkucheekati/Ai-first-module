from typing import Any, TypedDict, Annotated, Sequence
from operator import add
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class AgentState(TypedDict):
    """
    State for the HCP Agent using LangGraph.
    
    Attributes:
        user_input: The current input from the user
        conversation_history: List of messages in the conversation
        selected_tool: The tool selected for execution
        tool_result: The result from tool execution
        response: The final response to return to the user
        hcp_id: The ID of the HCP being discussed (optional)
        interaction_id: The ID of the interaction being edited (optional)
    """
    user_input: str
    conversation_history: Annotated[Sequence[BaseMessage], add]
    selected_tool: str
    tool_result: dict[str, Any] | None
    response: str
    hcp_id: int | None
    interaction_id: int | None
    db: Any | None
    recommendation_context: dict[str, Any] | None
