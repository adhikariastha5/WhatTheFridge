import React, { useState } from 'react';
import './IngredientInput.css';

function IngredientInput({ onSubmit, loading }) {
  const [ingredients, setIngredients] = useState(['']);
  const [craving, setCraving] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const handleIngredientChange = (index, value) => {
    const newIngredients = [...ingredients];
    newIngredients[index] = value;
    setIngredients(newIngredients);
  };

  const addIngredientField = () => {
    setIngredients([...ingredients, '']);
  };

  const removeIngredientField = (index) => {
    if (ingredients.length > 1) {
      const newIngredients = ingredients.filter((_, i) => i !== index);
      setIngredients(newIngredients);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const validIngredients = ingredients.filter(ing => ing.trim() !== '');
    if (validIngredients.length === 0 && !imageFile) {
      alert('Please enter at least one ingredient or upload an image');
      return;
    }
    onSubmit(validIngredients, craving, imageFile);
  };

  return (
    <div className="ingredient-input-container">
      <form onSubmit={handleSubmit} className="ingredient-form">
        <div className="form-section">
          <h3>What ingredients do you have?</h3>
          {ingredients.map((ingredient, index) => (
            <div key={index} className="ingredient-field">
              <input
                type="text"
                value={ingredient}
                onChange={(e) => handleIngredientChange(index, e.target.value)}
                placeholder="Enter an ingredient..."
                className="ingredient-input"
              />
              {ingredients.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeIngredientField(index)}
                  className="remove-btn"
                >
                  ×
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addIngredientField}
            className="add-btn"
          >
            + Add Another Ingredient
          </button>
        </div>

        <div className="form-section">
          <h3>Or upload an image of your ingredients</h3>
          <div className="image-upload">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="file-input"
              id="image-upload"
            />
            <label htmlFor="image-upload" className="file-label">
              {imagePreview ? 'Change Image' : 'Choose Image'}
            </label>
            {imagePreview && (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" />
                <button
                  type="button"
                  onClick={() => {
                    setImageFile(null);
                    setImagePreview(null);
                  }}
                  className="remove-image-btn"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="form-section">
          <h3>What are you craving? (Optional)</h3>
          <input
            type="text"
            value={craving}
            onChange={(e) => setCraving(e.target.value)}
            placeholder="e.g., pasta, dessert, spicy food..."
            className="craving-input"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="submit-btn"
        >
          {loading ? 'Finding Recipes...' : 'Find Recipes'}
        </button>
      </form>
    </div>
  );
}

export default IngredientInput;

