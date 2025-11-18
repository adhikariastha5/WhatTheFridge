import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re


class WebSearchService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search_recipes(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for recipes using DuckDuckGo or Google search"""
        try:
            # Using DuckDuckGo HTML search (free, no API key needed)
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}+recipe"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            recipes = []
            results = soup.find_all('a', class_='result__a', limit=max_results)
            
            for result in results:
                url = result.get('href', '')
                title = result.get_text(strip=True)
                
                if url and title:
                    recipes.append({
                        'title': title,
                        'url': url,
                        'source': 'web',
                        'thumbnail': None
                    })
            
            return recipes
        except Exception as e:
            print(f"Error searching web: {str(e)}")
            return []

    def extract_recipe_from_url(self, url: str) -> Optional[Dict]:
        """Extract recipe details from a blog/website URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find recipe content (common patterns)
            recipe_data = {
                'title': '',
                'ingredients': [],
                'instructions': [],
                'description': ''
            }
            
            # Find title
            title_tag = soup.find('h1') or soup.find('title')
            if title_tag:
                recipe_data['title'] = title_tag.get_text(strip=True)
            
            # Find ingredients (common class names)
            ingredient_patterns = [
                {'class': 'ingredient'},
                {'class': 'ingredients'},
                {'itemprop': 'recipeIngredient'},
                {'class': 'recipe-ingredient'}
            ]
            
            for pattern in ingredient_patterns:
                ingredients = soup.find_all('li', pattern)
                if ingredients:
                    recipe_data['ingredients'] = [ing.get_text(strip=True) for ing in ingredients]
                    break
            
            # Find instructions/steps
            instruction_patterns = [
                {'class': 'instruction'},
                {'class': 'instructions'},
                {'class': 'step'},
                {'itemprop': 'recipeInstructions'}
            ]
            
            for pattern in instruction_patterns:
                instructions = soup.find_all('li', pattern)
                if instructions:
                    recipe_data['instructions'] = [inst.get_text(strip=True) for inst in instructions]
                    break
            
            # If no structured data found, try to extract from paragraphs
            if not recipe_data['instructions']:
                # Look for numbered lists or paragraphs with cooking keywords
                all_text = soup.get_text()
                # Simple heuristic: split by common step indicators
                steps = re.split(r'\n\s*\d+[\.\)]\s*', all_text)
                if len(steps) > 1:
                    recipe_data['instructions'] = [s.strip() for s in steps[1:6] if len(s.strip()) > 20]
            
            return recipe_data if recipe_data['title'] or recipe_data['instructions'] else None
            
        except Exception as e:
            print(f"Error extracting recipe from URL: {str(e)}")
            return None

