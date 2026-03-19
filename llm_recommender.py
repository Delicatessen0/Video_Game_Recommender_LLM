import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from steam_data import fetch_steam_game_details

# Load .env so HF_TOKEN is available regardless of import order
load_dotenv()

# Lazily resolve the token so it is read after dotenv is loaded
def _get_client():
    api_key = os.environ.get("HF_TOKEN", "")
    if api_key:
        return InferenceClient(api_key=api_key)
    return None

def get_recommendations(query):
    client = _get_client()
    if not client:
        return get_mock_recommendations(query)

    prompt = f"""
    Suggest 3 video games for a user who asked: "{query}".
    Focus on games available on Steam. Make sure to recommend games relevant to the query — do NOT always suggest the same games.
    Return ONLY a valid JSON array of objects, with no extra text before or after.
    For each game, include exactly these fields:
    - title: The exact name of the game as listed on Steam
    - reason: A short 1-2 sentence reason why it fits the user's query

    Example response format:
    [
        {{"title": "Stardew Valley", "reason": "A highly relaxing farming sim..."}}
    ]
    Only output the JSON array. Do not include any explanation or markdown.
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        text = response.choices[0].message.content
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
