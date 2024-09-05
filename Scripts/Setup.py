import os
import json
import requests
import pickle
import subprocess
import time

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def run_check_script():
    """Run the Check.py script."""
    try:
        subprocess.run(['python', 'Check.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error running Check.py: {e}')
        exit(1)

def get_api_keys(api_keys_path):
    """Request API keys from the user and save them."""
    keys = {
        "Trakt Client ID": input("Enter your Trakt Client ID: ").strip(),
        "Trakt Client Secret": input("Enter your Trakt Client Secret: ").strip(),
        "Trakt Authorization Code": input("Enter your Trakt Authorization Code: ").strip(),
        "Real-Debrid API Key": input("Enter your Real-Debrid API Key: ").strip(),
        "TMDB API KEY": input("Enter your TMDB API Key (optional): ").strip()
    }
    save_api_keys(keys, api_keys_path)
    return keys

def save_api_keys(keys, api_keys_path):
    """Save API keys to a file and exchange Trakt Authorization Code for Access Token."""
    if "Trakt Authorization Code" in keys and "Trakt Client ID" in keys and "Trakt Client Secret" in keys:
        # Exchange Trakt Authorization Code for Access Token
        trakt_token_url = "https://api.trakt.tv/oauth/token"
        payload = {
            "code": keys["Trakt Authorization Code"],
            "client_id": keys["Trakt Client ID"],
            "client_secret": keys["Trakt Client Secret"],
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code"
        }
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                response = requests.post(trakt_token_url, json=payload)
                response.raise_for_status()
                response_data = response.json()
                keys["Trakt Client Access Token"] = response_data.get("access_token", "")
                # Remove sensitive information
                keys.pop("Trakt Client Secret", None)
                keys.pop("Trakt Authorization Code", None)
                break
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt < MAX_RETRIES:
                    print(f"Error exchanging Trakt Authorization Code for Access Token: {e}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"Failed to exchange Trakt Authorization Code after {MAX_RETRIES} attempts.")
                    raise
    with open(api_keys_path, 'w') as file:
        json.dump(keys, file, indent=4)

def fetch_user_data(api_key):
    """Fetch user data from Real-Debrid with retry mechanism."""
    url = 'https://api.real-debrid.com/rest/1.0/user'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            attempt += 1
            if attempt < MAX_RETRIES:
                print(f'Error fetching user data: {e}. Retrying in {RETRY_DELAY} seconds...')
                time.sleep(RETRY_DELAY)
            else:
                print(f'Failed to fetch user data after {MAX_RETRIES} attempts.')
                return None

def cache_data(data, cache_path):
    """Cache user data."""
    with open(cache_path, 'wb') as file:
        pickle.dump(data, file)

def read_pkl_and_save_json(pkl_path, json_path):
    """Read cached data from a pickle file and save it as JSON."""
    with open(pkl_path, 'rb') as file:
        data = pickle.load(file)
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def mask_key(key):
    """Mask API key for display."""
    return key[:6] + '*' * (len(key) - 6)

def update_api_keys(api_keys_path):
    """Update existing API keys."""
    keys = {}
    try:
        if os.path.getsize(api_keys_path) > 0:
            with open(api_keys_path, 'r') as file:
                keys = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading API keys file: {e}")
        return
    
    print("Which keys would you like to update? (leave blank to keep current value)")
    for key in keys:
        if key == "Trakt Client ID":
            new_id = input(f"{key} (current: {mask_key(keys[key])}): ").strip()
            if new_id:
                keys[key] = new_id
                # Request new secret and authorization code
                keys["Trakt Client Secret"] = input("Enter your new Trakt Client Secret: ").strip()
                keys["Trakt Authorization Code"] = input("Enter your new Trakt Authorization Code: ").strip()
                # Exchange for new access token
                trakt_token_url = "https://api.trakt.tv/oauth/token"
                payload = {
                    "code": keys["Trakt Authorization Code"],
                    "client_id": keys["Trakt Client ID"],
                    "client_secret": keys["Trakt Client Secret"],
                    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                    "grant_type": "authorization_code"
                }
                attempt = 0
                while attempt < MAX_RETRIES:
                    try:
                        response = requests.post(trakt_token_url, json=payload)
                        response.raise_for_status()
                        response_data = response.json()
                        keys["Trakt Client Access Token"] = response_data.get("access_token", "")
                        # Remove sensitive information
                        keys.pop("Trakt Client Secret", None)
                        keys.pop("Trakt Authorization Code", None)
                        break
                    except requests.exceptions.RequestException as e:
                        attempt += 1
                        if attempt < MAX_RETRIES:
                            print(f"Error exchanging Trakt Authorization Code for Access Token: {e}. Retrying in {RETRY_DELAY} seconds...")
                            time.sleep(RETRY_DELAY)
                        else:
                            print(f"Failed to exchange Trakt Authorization Code after {MAX_RETRIES} attempts.")
                            raise
        else:
            masked_key = mask_key(keys[key])
            new_value = input(f"{key} (current: {masked_key}): ").strip()
            if new_value:
                keys[key] = new_value
    
    save_api_keys(keys, api_keys_path)

def main():
    """Main function to run the script."""
    # Define paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)  # Go up one level to the root directory
    api_keys_path = os.path.join(root_dir, 'Api Keys', 'api_keys.json')
    profile_path = os.path.join(root_dir, 'Profile', 'real_debrid_data.json')
    rd_key_path = os.path.join(root_dir, 'Profile', 'api_key.json')
    cache_path = os.path.join(root_dir, 'Cached Data', 'user_data.pkl')

    # Ensure necessary directories exist
    os.makedirs(os.path.dirname(api_keys_path), exist_ok=True)
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    os.makedirs(os.path.dirname(rd_key_path), exist_ok=True)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    # Run Check.py script
    run_check_script()

    if os.path.exists(api_keys_path):
        try:
            if os.path.getsize(api_keys_path) > 0:
                with open(api_keys_path, 'r') as file:
                    keys = json.load(file)
                
                if not any(keys.values()):  # Check if all values are empty
                    print("API keys file is empty. Requesting new API keys...")
                    get_api_keys(api_keys_path)
                else:
                    update_choice = input("API keys already exist. Would you like to update them? (yes/no): ").strip().lower()
                    if update_choice == 'yes':
                        update_api_keys(api_keys_path)
            else:
                print("API keys file is empty. Requesting new API keys...")
                get_api_keys(api_keys_path)
        except json.JSONDecodeError as e:
            print(f"Error reading API keys file: {e}")
            get_api_keys(api_keys_path)
    else:
        print("API keys file does not exist. Requesting new API keys...")
        get_api_keys(api_keys_path)
    
    with open(api_keys_path, 'r') as file:
        keys = json.load(file)
    
    rd_key = keys.get("Real-Debrid API Key")
    user_data = fetch_user_data(rd_key)
    
    if user_data:
        cache_data(user_data, cache_path)
        read_pkl_and_save_json(cache_path, profile_path)
        with open(rd_key_path, 'w') as file:
            json.dump({"Real-Debrid API Key": rd_key}, file, indent=4)
        print("User data fetched and saved successfully!")

        # Run Run.py script
        try:
            subprocess.run(['python', 'Run.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error running Run.py: {e}')
            exit(1)
    else:
        print("Failed to fetch user data.")

if __name__ == "__main__":
    main()
