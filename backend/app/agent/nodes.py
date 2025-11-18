from typing import Dict, Any
from .state import AgentState
from ..services.gemini_service import GeminiService
from ..services.youtube_service import YouTubeService
from ..services.web_search_service import WebSearchService
from ..services.image_service import ImageService


class AgentNodes:
    def __init__(self):
        self.gemini = GeminiService()
        self.youtube = YouTubeService()
        self.web_search = WebSearchService()
        self.image_service = ImageService()

    def process_ingredients(self, state: AgentState) -> AgentState:
        """Process ingredients from text or image"""
        try:
            # If image is provided, use vision API
            if 'image_data' in state and state.get('image_data'):
                ingredients = self.gemini.recognize_ingredients_from_image(state['image_data'])
                state['ingredients'] = ingredients
            
            # Process ingredients into search query
            if state.get('ingredients'):
                search_query = self.gemini.process_ingredients(
                    state['ingredients'],
                    state.get('craving')
                )
                state['search_query'] = search_query
                state['current_step'] = 'ingredients_processed'
            
            return state
        except Exception as e:
            state['error'] = f"Error processing ingredients: {str(e)}"
            return state

    def search_recipes(self, state: AgentState) -> AgentState:
        """Search for recipes from YouTube and web"""
        try:
            query = state.get('search_query', '')
            if not query:
                query = self.gemini.process_ingredients(
                    state.get('ingredients', []),
                    state.get('craving')
                )
            
            recipes = []
            
            # Search YouTube
            youtube_results = self.youtube.search_recipes(query, max_results=3)
            recipes.extend(youtube_results)
            
            # Search web
            web_results = self.web_search.search_recipes(query, max_results=2)
            recipes.extend(web_results)
            
            state['recipes'] = recipes
            state['current_step'] = 'recipes_found'
            
            return state
        except Exception as e:
            state['error'] = f"Error searching recipes: {str(e)}"
            return state

    def extract_recipe_details(self, state: AgentState) -> AgentState:
        """Extract detailed recipe information"""
        try:
            recipes = state.get('recipes', [])
            
            for recipe in recipes:
                if recipe.get('source') == 'youtube' and recipe.get('video_id'):
                    # Get transcript
                    transcript = self.youtube.get_transcript(recipe['video_id'])
                    if transcript:
                        recipe['transcript'] = transcript
                        # Extract steps from transcript
                        steps = self.youtube.extract_steps_from_transcript(transcript)
                        recipe['steps'] = steps
                
                elif recipe.get('source') == 'web' and recipe.get('url'):
                    # Extract from web page
                    recipe_data = self.web_search.extract_recipe_from_url(recipe['url'])
                    if recipe_data:
                        recipe.update(recipe_data)
                        # Use Gemini to format steps better
                        if recipe_data.get('instructions'):
                            recipe['steps'] = recipe_data['instructions']
            
            state['recipes'] = recipes
            state['current_step'] = 'details_extracted'
            
            return state
        except Exception as e:
            state['error'] = f"Error extracting recipe details: {str(e)}"
            return state

    def chat_agent(self, state: AgentState) -> AgentState:
        """Handle chat interactions with Gemini"""
        try:
            conversation_history = state.get('conversation_history', [])
            last_message = conversation_history[-1] if conversation_history else None
            
            if last_message and last_message.get('role') == 'user':
                user_message = last_message.get('content', '')
                
                # Build context-aware prompt
                context = f"""You are a helpful cooking assistant. The user has these ingredients: {', '.join(state.get('ingredients', []))}
                They are looking for: {state.get('craving', 'a recipe')}
                """
                
                if state.get('recipes'):
                    context += f"\nAvailable recipes: {[r.get('title') for r in state['recipes']]}"
                
                if state.get('serving_size'):
                    context += f"\nServing size: {state['serving_size']} people"
                
                if state.get('cooking_method'):
                    context += f"\nCooking method available: {state['cooking_method']}"
                
                full_message = context + f"\n\nUser: {user_message}\nAssistant:"
                
                response = self.gemini.chat(full_message, conversation_history[:-1])
                
                conversation_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
                # Check if user wants to customize recipe
                if any(keyword in user_message.lower() for keyword in ['change', 'modify', 'adjust', 'customize', 'edit']):
                    if state.get('selected_recipe'):
                        customized = self.gemini.customize_recipe(
                            str(state['selected_recipe']),
                            user_message,
                            state.get('serving_size')
                        )
                        state['selected_recipe']['customized'] = customized
                
                state['conversation_history'] = conversation_history
                state['current_step'] = 'chat_completed'
            
            return state
        except Exception as e:
            state['error'] = f"Error in chat: {str(e)}"
            return state

