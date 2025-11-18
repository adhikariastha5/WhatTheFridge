from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import AgentNodes


class CookingAgentGraph:
    def __init__(self):
        self.nodes = AgentNodes()
        self.graph = self._build_graph()
        self.chat_graph = self._build_chat_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for ingredient processing"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for ingredient processing flow
        workflow.add_node("process_ingredients", self.nodes.process_ingredients)
        workflow.add_node("search_recipes", self.nodes.search_recipes)
        workflow.add_node("extract_details", self.nodes.extract_recipe_details)
        
        # Set entry point
        workflow.set_entry_point("process_ingredients")
        
        # Add edges for main flow
        workflow.add_edge("process_ingredients", "search_recipes")
        workflow.add_edge("search_recipes", "extract_details")
        workflow.add_edge("extract_details", END)
        
        return workflow.compile()
    
    def _build_chat_graph(self) -> StateGraph:
        """Build a separate graph for chat interactions"""
        workflow = StateGraph(AgentState)
        workflow.add_node("chat_agent", self.nodes.chat_agent)
        workflow.set_entry_point("chat_agent")
        workflow.add_edge("chat_agent", END)
        return workflow.compile()

    def process_ingredients_flow(self, ingredients: list, craving: str = None, image_data: bytes = None) -> dict:
        """Run the full ingredient processing flow"""
        initial_state: AgentState = {
            'ingredients': ingredients,
            'craving': craving,
            'recipes': [],
            'selected_recipe': None,
            'conversation_history': [],
            'user_preferences': {},
            'serving_size': None,
            'utensils': None,
            'cooking_method': None,
            'current_step': 'start',
            'error': None
        }
        
        if image_data:
            initial_state['image_data'] = image_data
        
        result = self.graph.invoke(initial_state)
        return result

    def chat(self, message: str, state: dict) -> dict:
        """Handle chat interaction"""
        state['conversation_history'].append({
            'role': 'user',
            'content': message
        })
        
        result = self.chat_graph.invoke(state)
        return result

