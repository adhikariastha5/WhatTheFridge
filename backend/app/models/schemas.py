from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class IngredientInput(BaseModel):
    ingredients: List[str]
    craving: Optional[str] = None
    image_url: Optional[str] = None


class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class Recipe(BaseModel):
    title: str
    source: str
    url: str
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    video_id: Optional[str] = None
    transcript: Optional[str] = None
    steps: Optional[List[str]] = None


class RecipeResponse(BaseModel):
    recipes: List[Recipe]
    conversation_id: str


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    updated_recipes: Optional[List[Recipe]] = None


class TranscriptRequest(BaseModel):
    video_id: str

