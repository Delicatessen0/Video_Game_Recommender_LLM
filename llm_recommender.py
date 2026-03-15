import os
import json
import google.generativeai as genai
from steam_data import fetch_steam_game_details

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

def get_recommendations(query):
    # If no key, we try to use a mock for demonstration
    if not api_key:
        return get_mock_recommendations(query)

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Suggest 3 video games for a user who asked: "{query}".
    Focus on games available on Steam.
    Return ONLY a JSON array of objects representing the games.
    For each game, include exactly these fields:
    - title: The name of the game
    - reason: A short 1-2 sentence reason why it fits the user's query

    Example response format:
    [
        {{"title": "Stardew Valley", "reason": "A highly relaxing farming sim..."}}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean markdown formatting if present
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        
        games = json.loads(text.strip())
        
        # Enrich with Steam data
        enriched_games = []
        for game in games:
            details = fetch_steam_game_details(game['title'])
            if details:
                game.update(details)
            enriched_games.append(game)
            
        return enriched_games
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return get_mock_recommendations(query)

def get_mock_recommendations(query):
    # Fallback to mock data if API key is missing or fails
    print("Using MOCK data for recommendations.")
    games = [
        {"title": "Stardew Valley", "reason": "A perfect relaxing farming game that matches your vibe."},
        {"title": "Terraria", "reason": "Explore, build, and fight in a 2D sandbox world with deep progression."},
        {"title": "Factorio", "reason": "Automate everything and build massive factories."}
    ]
    
    enriched_games = []
    for game in games:
        details = fetch_steam_game_details(game['title'])
        if details:
            game.update(details)
        enriched_games.append(game)
        
    return enriched_games
