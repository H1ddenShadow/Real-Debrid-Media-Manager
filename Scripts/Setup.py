import os
import json
import requests
import pickle
import subprocess

def run_check_script():
    """Run the Check.py script before continuing with the main operations."""
    check_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Scripts', 'Check.py')
    result = subprocess.run(['python', check_script_path], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running Check.py:\n{result.stderr}")
        exit(1)
    else:
        print(f"Check.py output:\n{result.stdout}")

def get_api_keys(api_keys_path):
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
        response = requests.post(trakt_token_url, json=payload)
        response_data = response.json()
        keys["Trakt Client Access Token"] = response_data.get("access_token", "")

        # Remove sensitive information
        keys.pop("Trakt Client Secret", None)
        keys.pop("Trakt Authorization Code", None)

    with open(api_keys_path, 'w') as file:
        json.dump(keys, file, indent=4)

def fetch_user_data(api_key):
    url = 'https://api.real-debrid.com/rest/1.0/user'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error fetching user data: {e}')
        return None

def cache_data(data, cache_path):
    with open(cache_path, 'wb') as file:
        pickle.dump(data, file)

def read_pkl_and_save_json(pkl_path, json_path):
    with open(pkl_path, 'rb') as file:
        data = pickle.load(file)
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def mask_key(key):
    return key[:6] + '*' * (len(key) - 6)

def update_api_keys(api_keys_path):
    with open(api_keys_path, 'r') as file:
        keys = json.load(file)
    
    print("Which keys would you like to update? (leave blank to keep current value)")
    for key in keys:
        masked_key = mask_key(keys[key]) if keys[key] else 'Not Set'
        new_value = input(f"{key} (current: {masked_key}): ").strip()
        if new_value:
            keys[key] = new_value
    
    save_api_keys(keys, api_keys_path)

def main():
    # Run Check.py script
    run_check_script()
    
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

    # Check if the API keys file exists and is valid
    if os.path.exists(api_keys_path):
        with open(api_keys_path, 'r') as file:
            try:
                keys = json.load(file)
                # Check if required keys are present
                required_keys = [
                    "Trakt Client ID", "Trakt Client Secret", "Trakt Authorization Code",
                    "Real-Debrid API Key", "TMDB API KEY"
                ]
                if any(key not in keys or not keys[key] for key in required_keys):
                    print("API keys file is missing some required data or is invalid.")
                    update_choice = input("Would you like to update the API keys? (yes/no): ").strip().lower()
                    if update_choice == 'yes':
                        update_api_keys(api_keys_path)
                else:
                    print("API keys are valid.")
            except json.JSONDecodeError:
                print("API keys file is corrupted or invalid JSON.")
                update_api_keys(api_keys_path)
    else:
        get_api_keys(api_keys_path)

    # Proceed with fetching and processing user data
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
    else:
        print("Failed to fetch user data.")

if __name__ == "__main__":
    main()
