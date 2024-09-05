import os
import json
import requests
import pickle
import subprocess

def load_api_keys(api_keys_path):
    with open(api_keys_path, 'r') as file:
        keys = json.load(file)
    return keys

def fetch_trakt_data(client_id, access_token, endpoint):
    url = f"https://api.trakt.tv/users/me/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "trakt-api-version": "2",
        "trakt-api-key": client_id
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Trakt data: {e}")
        return None

def fetch_rd_torrents(api_key):
    url = 'https://api.real-debrid.com/rest/1.0/torrents'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error fetching Real-Debrid torrents: {e}')
        return None

def cache_data(data, cache_path):
    with open(cache_path, 'wb') as file:
        pickle.dump(data, file)

def save_json(data, json_path):
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    api_keys_path = os.path.join(base_path, '..', 'Api Keys', 'api_keys.json')
    cached_data_path = os.path.join(base_path, '..', 'Cached Data')
    media_path = os.path.join(base_path, '..', 'Media')
    torrent_list_path = os.path.join(base_path, '..', 'Torrent List')

    os.makedirs(cached_data_path, exist_ok=True)
    os.makedirs(media_path, exist_ok=True)
    os.makedirs(torrent_list_path, exist_ok=True)

    keys = load_api_keys(api_keys_path)
    
    trakt_client_id = keys.get("Trakt Client ID")
    trakt_access_token = keys.get("Trakt Client Access Token")
    rd_api_key = keys.get("Real-Debrid API Key")

    if trakt_client_id and trakt_access_token:
        watchlist = fetch_trakt_data(trakt_client_id, trakt_access_token, 'watchlist')
        favourites = fetch_trakt_data(trakt_client_id, trakt_access_token, 'favorites')
        
        if watchlist:
            cache_data(watchlist, os.path.join(cached_data_path, 'watchlist.pkl'))
            save_json(watchlist, os.path.join(media_path, 'watchlist.json'))
            print("Watchlist data cached and saved successfully.")
        if favourites:
            cache_data(favourites, os.path.join(cached_data_path, 'favourites.pkl'))
            save_json(favourites, os.path.join(media_path, 'favourites.json'))
            print("Favourites data cached and saved successfully.")
    
    if rd_api_key:
        torrents = fetch_rd_torrents(rd_api_key)
        if torrents:
            cache_data(torrents, os.path.join(cached_data_path, 'torrents.pkl'))
            save_json(torrents, os.path.join(torrent_list_path, 'torrents.json'))
            print("Torrent list cached and saved successfully.")
    
    # Run the secondary script
    subprocess.run(['python', os.path.join(base_path, 'Torrent.py')])

if __name__ == "__main__":
    main()
