import os
import google.generativeai as genai
from typing import List, Optional
import base64
from PIL import Image
import io


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        genai.configure(api_key=api_key)
        # Use gemini-1.5-flash for free tier (faster and free)
        # gemini-1.5-pro is also available but has rate limits
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Same model supports vision

    def chat(self, message: str, conversation_history: Optional[List[dict]] = None) -> str:
        """Send a chat message to Gemini and get response"""
        try:
            # Convert conversation history format if needed
            if conversation_history:
                # Filter and format history for Gemini
                formatted_history = []
                for msg in conversation_history:
                    if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                        formatted_history.append(msg)
                
                if formatted_history:
                    chat = self.model.start_chat(history=formatted_history)
                    response = chat.send_message(message)
                else:
                    response = self.model.generate_content(message)
            else:
                response = self.model.generate_content(message)
            
            if response and hasattr(response, 'text'):
                return response.text
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
        except Exception as e:
            import traceback
            print(f"Error in Gemini chat: {str(e)}")
            traceback.print_exc()
            return f"Error: {str(e)}"

    def recognize_ingredients_from_image(self, image_data: bytes) -> List[str]:
        """Use Gemini Vision to recognize ingredients from an image"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            prompt = """Analyze this image and list all the food ingredients you can see. 
            Return only a comma-separated list of ingredient names, nothing else.
            Example: tomato, onion, garlic, chicken, salt, pepper"""
            
            response = self.vision_model.generate_content([prompt, image])
            ingredients_text = response.text.strip()
            
            # Parse the comma-separated list
            ingredients = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]
            return ingredients
        except Exception as e:
            print(f"Error recognizing ingredients: {str(e)}")
            return []

    def process_ingredients(self, ingredients: List[str], craving: Optional[str] = None) -> str:
        """Process ingredients and craving into a search query"""
        ingredients_str = ", ".join(ingredients)
        if craving:
            return f"Recipe using {ingredients_str} for {craving}"
        return f"Recipe using {ingredients_str}"

    def extract_recipe_steps(self, recipe_text: str) -> List[str]:
        """Extract step-by-step instructions from recipe text using Gemini"""
        try:
            prompt = f"""Extract the step-by-step cooking instructions from this recipe text.
            Return only the steps, one per line, numbered. If no clear steps are found, return the main instructions broken into logical steps.
            
            Recipe text:
            {recipe_text}
            
            Format:
            1. Step one
            2. Step two
            etc."""
            
            response = self.model.generate_content(prompt)
            steps_text = response.text.strip()
            
            # Parse steps
            steps = []
            for line in steps_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering/bullets
                    step = line.split('.', 1)[-1].strip()
                    if step:
                        steps.append(step)
            
            return steps if steps else [recipe_text]
        except Exception as e:
            print(f"Error extracting steps: {str(e)}")
            return [recipe_text]

    def customize_recipe(self, recipe_text: str, user_request: str, serving_size: Optional[int] = None) -> str:
        """Customize recipe based on user preferences"""
        try:
            prompt = f"""Modify this recipe according to the user's request: {user_request}
            
            Original recipe:
            {recipe_text}
            
            {f'Adjust for {serving_size} servings.' if serving_size else ''}
            
            Provide the modified recipe with updated ingredients and instructions."""
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error customizing recipe: {str(e)}"

