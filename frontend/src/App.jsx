import React, { useState } from 'react';
import './App.css';
import IngredientInput from './components/IngredientInput';
import RecipeCard from './components/RecipeCard';
import ChatInterface from './components/ChatInterface';

function App() {
  const [recipes, setRecipes] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleIngredientsSubmit = async (ingredients, craving, imageFile) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      ingredients.forEach(ing => formData.append('ingredients', ing));
      if (craving) formData.append('craving', craving);
      if (imageFile) formData.append('image', imageFile);

      const response = await fetch('http://localhost:8000/api/ingredients', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recipes');
      }

      const data = await response.json();
      console.log('Recipes response:', data);
      console.log('Number of recipes:', data.recipes?.length || 0);
      
      if (data.recipes && data.recipes.length > 0) {
        setRecipes(data.recipes);
        setConversationId(data.conversation_id);
      } else {
        setError('No recipes found. Please try different ingredients or check your connection.');
        setConversationId(data.conversation_id); // Still set conversation ID for chat
      }
    } catch (err) {
      console.error('Error fetching recipes:', err);
      setError(err.message || 'Failed to fetch recipes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🍳 WhatTheFridge</h1>
        <p>Your AI Cooking Assistant</p>
      </header>

      <main className="App-main">
        <IngredientInput 
          onSubmit={handleIngredientsSubmit}
          loading={loading}
        />

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {recipes.length > 0 && (
          <div className="recipes-section">
            <h2>Suggested Recipes</h2>
            <div className="recipes-grid">
              {recipes.map((recipe, index) => (
                <RecipeCard key={index} recipe={recipe} />
              ))}
            </div>
          </div>
        )}

        {conversationId && (
          <ChatInterface conversationId={conversationId} />
        )}
      </main>
    </div>
  );
}

export default App;

