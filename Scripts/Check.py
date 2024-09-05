import os

# Define the base directory (should be run from within the 'Scripts' folder)
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define the main directory and its sub-folders
sub_folders = [
    'Api Keys',
    'Media',
    'Logs/Archived',
    'Cached Data',
    'Profile',
    'Scheduled Runs',
    'Scripts',  # This is optional since the script is placed in this folder
    'Torrent List'
]

def create_directories(base_path, folders):
    for folder in folders:
        path = os.path.join(base_path, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")
        else:
            print(f"Directory already exists: {path}")

def main():
    # Create sub-folders relative to the base directory
    create_directories(base_directory, sub_folders)

if __name__ == "__main__":
    main()
