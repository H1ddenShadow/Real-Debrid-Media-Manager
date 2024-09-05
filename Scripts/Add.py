import os
import json
import pickle
import requests

def load_cached_data(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)

def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def load_api_key(api_key_path, key_name):
    with open(api_key_path, 'r') as file:
        keys = json.load(file)
    return keys.get(key_name, '')

def add_magnet_to_rd(api_key, magnet_link):
    url = 'https://api.real-debrid.com/rest/1.0/torrents/addMagnet'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'magnet': magnet_link
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get('id')
    except requests.exceptions.RequestException as e:
        print(f"Error adding magnet to Real-Debrid: {e}")
        return None

def get_file_ids(api_key, torrent_id):
    url = f'https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        files = response.json().get('files', [])
        file_ids = [str(file['id']) for file in files]
        return ','.join(file_ids)
    except requests.exceptions.RequestException as e:
        print(f"Error getting file IDs from Real-Debrid: {e}")
        return None

def select_files_and_start_torrent(api_key, torrent_id, file_ids):
    url = f'https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'files': file_ids
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.status_code == 204
    except requests.exceptions.RequestException as e:
        print(f"Error starting torrent on Real-Debrid: {e}")
        return None

def log_data(log_path, data):
    with open(log_path, 'w') as file:
        json.dump(data, file, indent=4)

def cache_data(data, cache_path):
    with open(cache_path, 'wb') as file:
        pickle.dump(data, file)

def is_unique(item, added_data):
    for data in added_data:
        if item['title'] == data['title'] or item['magnet_link'] == data['magnet_link']:
            return False
    return True

def format_skipped_item(item, reason):
    # Keep all fields but add a reason
    return {
        'id': item.get('id'),
        'timestamp': item.get('timestamp'),
        'title': item.get('title'),
        'year': item.get('year'),
        'yts_magnet_link': item.get('yts_magnet_link'),
        'magnet_link': item.get('magnet_link'),
        'quality': item.get('quality'),
        'reason': reason
    }

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    api_keys_path = os.path.join(base_path, '..', 'Api Keys', 'api_keys.json')
    profile_path = os.path.join(base_path, '..', 'Profile', 'api_key.json')
    cached_data_path = os.path.join(base_path, '..', 'Cached Data')
    media_path = os.path.join(base_path, '..', 'Media')
    logs_path = os.path.join(base_path, '..', 'Logs')

    retrieved_data_pkl_path = os.path.join(cached_data_path, 'retrieved_data.pkl')
    retrieved_data_json_path = os.path.join(media_path, 'retrieved_data.json')
    added_data_cache_path = os.path.join(cached_data_path, 'added_data.pkl')

    added_data_log_path = os.path.join(logs_path, 'added_data.json')
    skipped_titles_log_path = os.path.join(logs_path, 'skipped_titles.json')
    error_log_path = os.path.join(logs_path, 'errors.json')

    os.makedirs(logs_path, exist_ok=True)

    # Load API Key
    api_key_from_profile = load_json_data(profile_path).get('Real-Debrid API Key', '')
    api_key_from_keys = load_json_data(api_keys_path).get('Real-Debrid API Key', '')
    rd_api_key = api_key_from_profile if api_key_from_profile else api_key_from_keys

    if not rd_api_key:
        print("Real-Debrid API Key not found.")
        return

    # Load Data
    retrieved_data = load_cached_data(retrieved_data_pkl_path)
    try:
        added_data = load_cached_data(added_data_cache_path)
    except FileNotFoundError:
        added_data = []

    errors = []
    skipped_titles = []

    for item in retrieved_data:
        if is_unique(item, added_data):
            magnet_link = item['magnet_link']
            torrent_id = add_magnet_to_rd(rd_api_key, magnet_link)
            if torrent_id:
                file_ids = get_file_ids(rd_api_key, torrent_id)
                if file_ids:
                    result = select_files_and_start_torrent(rd_api_key, torrent_id, file_ids)
                    if result:
                        added_data.append(item)
                    else:
                        errors.append(item)
                else:
                    errors.append(item)
            else:
                errors.append(item)
        else:
            # Format and add skipped item with reason
            skipped_titles.append(format_skipped_item(item, 'Duplicate entry'))

    log_data(added_data_log_path, added_data)
    cache_data(added_data, added_data_cache_path)
    log_data(error_log_path, errors)
    log_data(skipped_titles_log_path, skipped_titles)

    print("Magnet links processed and logged successfully.")

if __name__ == "__main__":
    main()
