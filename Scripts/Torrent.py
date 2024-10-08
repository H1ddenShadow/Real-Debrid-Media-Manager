import os
import pickle
import requests
import json
import re
from datetime import datetime

def load_cached_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            if file_path.endswith('.pkl'):
                return pickle.load(file)
            elif file_path.endswith('.json'):
                return json.load(file)
    return []

def fetch_yts_movie(title, year):
    url = f"https://yts.mx/api/v2/list_movies.json?query_term={title}&year={year}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['data']['movie_count'] > 0:
            return data['data']['movies'][0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching YTS data: {e}")
        return None

def get_best_torrent(torrents):
    # Prioritize 4K, then 1080p, then 720p, and so on
    quality_order = ['2160p', '1080p', '720p']
    for quality in quality_order:
        for torrent in torrents:
            if quality in torrent['quality']:
                return torrent
    return torrents[0] if torrents else None

def save_json(data, json_path):
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def cache_data(data, cache_path):
    with open(cache_path, 'wb') as file:
        pickle.dump(data, file)

def log_not_found(log_data, title, year, reason):
    entry = {'title': title, 'year': year, 'reason': reason}
    if entry not in log_data:
        log_data.append(entry)

def extract_movie_info(item):
    title, year = None, None
    if item['type'] == 'movie':
        title = item['movie'].get('title')
        year = item['movie'].get('year')
    elif item['type'] == 'episode':
        title = item['episode'].get('title')
        year = item['episode']['ids'].get('tmdb')  # Using tmdb id as a placeholder for year
    
    # Use regex to clean and extract title and year if necessary
    if title:
        title_match = re.match(r"^(.*?)(?:\s+\((\d{4})\))?$", title)
        if title_match:
            title = title_match.group(1).strip()
            if not year and title_match.group(2):
                year = title_match.group(2)
    
    return title, year

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    cached_data_path = os.path.join(base_path, '..', 'Cached Data')
    media_path = os.path.join(base_path, '..', 'Media')
    log_path = os.path.join(base_path, '..', 'Logs', 'not_found.json')

    watchlist_path = os.path.join(cached_data_path, 'watchlist.pkl')
    favourites_path = os.path.join(cached_data_path, 'favourites.pkl')

    watchlist = load_cached_data(watchlist_path)
    favourites = load_cached_data(favourites_path)

    all_movies = watchlist + favourites
    all_movies = sorted(all_movies, key=lambda x: x.get('movie', {}).get('title', ''))

    retrieved_data = []
    not_found = load_cached_data(log_path)

    for item in all_movies:
        title, year = extract_movie_info(item)
        if title and year:
            yts_movie = fetch_yts_movie(title, year)
            if yts_movie:
                best_torrent = get_best_torrent(yts_movie['torrents'])
                if best_torrent:
                    magnet_link = f"magnet:?xt=urn:btih:{best_torrent['hash']}&dn={title}&tr=udp://tracker.openbittorrent.com:80/announce"
                    retrieved_data.append({
                        'id': len(retrieved_data) + 1,
                        'timestamp': datetime.now().isoformat(),
                        'title': title,
                        'year': year,
                        'yts_magnet_link': best_torrent['url'],
                        'magnet_link': magnet_link,
                        'quality': best_torrent['quality']
                    })
                else:
                    log_not_found(not_found, title, year, 'No suitable torrent found on YTS')
            else:
                log_not_found(not_found, title, year, 'Not found on YTS')
        else:
            log_not_found(not_found, title if title else 'Unknown', year if year else 'Unknown', 'Missing title or year')

    save_json(retrieved_data, os.path.join(media_path, 'retrieved_data.json'))
    save_json(not_found, log_path)
    cache_data(retrieved_data, os.path.join(cached_data_path, 'retrieved_data.pkl'))
    cache_data(not_found, os.path.join(cached_data_path, 'not_found.pkl'))

    print("Data retrieval and caching completed successfully.")

if __name__ == "__main__":
    main()
