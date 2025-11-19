from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from typing import Optional, List
import uuid

from .models.schemas import (
    IngredientInput, ChatMessage, RecipeResponse, 
    ChatResponse, Recipe
)
from .agent.graph import CookingAgentGraph

load_dotenv()

app = FastAPI(title="WhatTheFridge API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent graph
agent_graph = CookingAgentGraph()

# Store conversation states (in production, use Redis or database)
conversation_states = {}


@app.get("/")
async def root():
    return {"message": "WhatTheFridge API is running"}


@app.post("/api/ingredients")
async def submit_ingredients(
    request: Request,
    image: Optional[UploadFile] = File(None)
):
    """Submit ingredients and get recipe suggestions"""
    try:
        # Parse form data
        form = await request.form()
        ingredients = form.getlist("ingredients")
        craving = form.get("craving")
        
        # Filter out empty ingredients
        ingredients = [ing for ing in ingredients if ing.strip()]
        
        image_data = None
        if image:
            image_data = await image.read()
            # Preprocess image if needed
            from ..services.image_service import ImageService
            image_service = ImageService()
            if image_service.validate_image(image_data):
                image_data = image_service.preprocess_image(image_data)
        
        # Process ingredients
        result = agent_graph.process_ingredients_flow(
            ingredients=ingredients,
            craving=craving,
            image_data=image_data
        )
        
        # Check for errors in the result
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        # Create conversation ID
        conversation_id = str(uuid.uuid4())
        conversation_states[conversation_id] = result
        
        # Convert recipes to response format
        recipes = []
        for recipe in result.get('recipes', []):
            recipes.append(Recipe(
                title=recipe.get('title', 'Unknown'),
                source=recipe.get('source', 'unknown'),
                url=recipe.get('url', ''),
                thumbnail=recipe.get('thumbnail'),
                description=recipe.get('description'),
                video_id=recipe.get('video_id'),
                transcript=recipe.get('transcript'),
                steps=recipe.get('steps', [])
            ))
        
        return RecipeResponse(
            recipes=recipes,
            conversation_id=conversation_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in submit_ingredients: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/chat")
async def chat_with_agent(message: ChatMessage):
    """Chat with the cooking agent"""
    try:
        conversation_id = message.conversation_id
        if not conversation_id or conversation_id not in conversation_states:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        state = conversation_states[conversation_id]
        
        # Process chat
        result = agent_graph.chat(message.message, state)
        conversation_states[conversation_id] = result
        
        # Extract response from conversation history
        response_text = ""
        if result.get('conversation_history'):
            last_message = result['conversation_history'][-1]
            if last_message.get('role') == 'assistant':
                response_text = last_message.get('content', '')
        
        # Check if recipes were updated
        updated_recipes = None
        if result.get('selected_recipe') and result['selected_recipe'].get('customized'):
            updated_recipes = [Recipe(
                title=result['selected_recipe'].get('title', 'Customized Recipe'),
                source='customized',
                url='',
                steps=[result['selected_recipe']['customized']]
            )]
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            updated_recipes=updated_recipes
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transcribe/{video_id}")
async def get_transcript(video_id: str):
    """Get transcript for a YouTube video"""
    try:
        from .services.youtube_service import YouTubeService
        youtube_service = YouTubeService()
        transcript = youtube_service.get_transcript(video_id)
        
        if transcript:
            return {"transcript": transcript, "video_id": video_id}
        else:
            raise HTTPException(status_code=404, detail="Transcript not available")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recipes")
async def get_recipes(conversation_id: str):
    """Get recipes for a conversation"""
    try:
        if conversation_id not in conversation_states:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        state = conversation_states[conversation_id]
        recipes = []
        
        for recipe in state.get('recipes', []):
            recipes.append(Recipe(
                title=recipe.get('title', 'Unknown'),
                source=recipe.get('source', 'unknown'),
                url=recipe.get('url', ''),
                thumbnail=recipe.get('thumbnail'),
                description=recipe.get('description'),
                video_id=recipe.get('video_id'),
                transcript=recipe.get('transcript'),
                steps=recipe.get('steps', [])
            ))
        
        return {"recipes": recipes}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

