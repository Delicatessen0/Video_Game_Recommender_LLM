import requests
import time

def search_steam_game(title):
    # Using the Steam Storefront API to search
    url = f"https://store.steampowered.com/api/storesearch/?term={title}&l=english&cc=US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('total', 0) > 0 and 'items' in data:
            # Get the first matching item
            item = data['items'][0]
            appid = item['id']
            return get_game_details(appid)
    except Exception as e:
        print(f"Error searching Steam for '{title}': {e}")
    return None

def get_game_details(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=US&l=english"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        key = str(appid)
        if data.get(key, {}).get('success'):
            game_data = data[key]['data']
            
            # Extract relevant info
            price_overview = game_data.get('price_overview', {})
            if game_data.get('is_free'):
                price = "Free to Play"
            elif price_overview:
                # Prefer pre-formatted USD price; fall back to computing from cents
                price = price_overview.get('final_formatted') or \
                        f"${price_overview.get('final', 0) / 100:.2f} USD"
            else:
                price = "Price Unavailable"
                
            return {
                "steam_id": appid,
                "steam_url": f"https://store.steampowered.com/app/{appid}/",
                "image_url": game_data.get('header_image', ''),
                "price": price,
                "genres": [g['description'] for g in game_data.get('genres', [])]
            }
    except Exception as e:
        print(f"Error fetching details for appid {appid}: {e}")
    return None

def fetch_steam_game_details(title):
    # Add a small delay to avoid rate limiting
    time.sleep(0.5)
    return search_steam_game(title)
