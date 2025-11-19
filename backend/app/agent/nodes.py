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
            
            print(f"Searching recipes with query: {query}")
            recipes = []
            
            # Search YouTube
            youtube_results = self.youtube.search_recipes(query, max_results=3)
            print(f"Found {len(youtube_results)} YouTube results")
            recipes.extend(youtube_results)
            
            # Search web
            web_results = self.web_search.search_recipes(query, max_results=2)
            print(f"Found {len(web_results)} web results")
            recipes.extend(web_results)
            
            print(f"Total recipes found: {len(recipes)}")
            state['recipes'] = recipes
            state['current_step'] = 'recipes_found'
            
            return state
        except Exception as e:
            import traceback
            print(f"Error searching recipes: {str(e)}")
            traceback.print_exc()
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
                context_parts = ["You are a helpful cooking assistant."]
                
                ingredients = state.get('ingredients', [])
                if ingredients:
                    context_parts.append(f"The user has these ingredients: {', '.join(ingredients)}")
                
                craving = state.get('craving')
                if craving:
                    context_parts.append(f"They are looking for: {craving}")
                
                recipes = state.get('recipes', [])
                if recipes:
                    recipe_titles = [r.get('title', 'Unknown') for r in recipes[:3]]
                    context_parts.append(f"Available recipes: {', '.join(recipe_titles)}")
                
                serving_size = state.get('serving_size')
                if serving_size:
                    context_parts.append(f"Serving size: {serving_size} people")
                
                cooking_method = state.get('cooking_method')
                if cooking_method:
                    context_parts.append(f"Cooking method available: {cooking_method}")
                
                # Use context only if we have meaningful context
                if len(context_parts) > 1:
                    context = "\n".join(context_parts)
                    # Prepare history without the last user message for context
                    history_for_chat = conversation_history[:-1] if len(conversation_history) > 1 else []
                    # Add system context as first message if we have history
                    if history_for_chat:
                        full_message = f"{context}\n\nUser: {user_message}"
                        response = self.gemini.chat(full_message, history_for_chat)
                    else:
                        full_message = f"{context}\n\nUser: {user_message}\n\nPlease help the user with their cooking question."
                        response = self.gemini.chat(full_message, None)
                else:
                    # No context, just chat normally
                    history_for_chat = conversation_history[:-1] if len(conversation_history) > 1 else None
                    response = self.gemini.chat(user_message, history_for_chat)
                
                conversation_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
                # Check if user wants to customize recipe
                customize_keywords = ['change', 'modify', 'adjust', 'customize', 'edit', 'don\'t have', 'dont have', 'no oven', 'no gas']
                if any(keyword in user_message.lower() for keyword in customize_keywords):
                    if recipes:
                        # Use first recipe if available
                        selected_recipe = recipes[0]
                        recipe_text = selected_recipe.get('transcript', selected_recipe.get('title', ''))
                        if recipe_text:
                            customized = self.gemini.customize_recipe(
                                recipe_text,
                                user_message,
                                serving_size
                            )
                            if 'customized' not in selected_recipe:
                                selected_recipe['customized'] = customized
                            state['selected_recipe'] = selected_recipe
                
                state['conversation_history'] = conversation_history
                state['current_step'] = 'chat_completed'
            
            return state
        except Exception as e:
            import traceback
            print(f"Error in chat_agent: {str(e)}")
            traceback.print_exc()
            state['error'] = f"Error in chat: {str(e)}"
            return state

