import React, { useState } from 'react';
import './RecipeCard.css';

function RecipeCard({ recipe }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="recipe-card">
      {recipe.thumbnail && (
        <div className="recipe-thumbnail">
          <img src={recipe.thumbnail} alt={recipe.title} />
        </div>
      )}
      
      <div className="recipe-content">
        <h3 className="recipe-title">{recipe.title}</h3>
        <p className="recipe-source">Source: {recipe.source}</p>
        
        {recipe.description && (
          <p className="recipe-description">{recipe.description}</p>
        )}

        {recipe.url && (
          <a
            href={recipe.url}
            target="_blank"
            rel="noopener noreferrer"
            className="recipe-link"
          >
            View {recipe.source === 'youtube' ? 'Video' : 'Recipe'} →
          </a>
        )}

        {recipe.steps && recipe.steps.length > 0 && (
          <div className="recipe-steps">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="toggle-steps-btn"
            >
              {showDetails ? 'Hide' : 'Show'} Steps ({recipe.steps.length})
            </button>
            
            {showDetails && (
              <ol className="steps-list">
                {recipe.steps.map((step, index) => (
                  <li key={index} className="step-item">
                    {step}
                  </li>
                ))}
              </ol>
            )}
          </div>
        )}

        {recipe.transcript && (
          <details className="transcript-section">
            <summary>View Full Transcript</summary>
            <p className="transcript-text">{recipe.transcript.substring(0, 500)}...</p>
          </details>
        )}
      </div>
    </div>
  );
}

export default RecipeCard;

