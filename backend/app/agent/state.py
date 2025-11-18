from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph.message import AnyMessage


class AgentState(TypedDict, total=False):
    """State for the cooking agent workflow"""
    ingredients: List[str]
    craving: Optional[str]
    recipes: List[Dict[str, Any]]
    selected_recipe: Optional[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    user_preferences: Dict[str, Any]
    serving_size: Optional[int]
    utensils: Optional[List[str]]
    cooking_method: Optional[str]  # gas, oven, stovetop, etc.
    current_step: str
    error: Optional[str]
    image_data: Optional[bytes]
    search_query: Optional[str]

