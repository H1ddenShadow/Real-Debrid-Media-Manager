import os
import subprocess
import sys

# Function to check if a module is installed
def check_and_install(module_name):
    try:
        __import__(module_name)
    except ImportError:
        print(f"{module_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

# Check for third-party modules
check_and_install('ttkbootstrap')

# Now you can safely import the modules
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import ttkbootstrap as tb

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
    all_exist = True
    created_directories = []
    for folder in folders:
        path = os.path.join(base_path, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            created_directories.append(folder)
            print(f"Created directory: {path}")
            all_exist = False
    if created_directories:
        print(f"Created directories: {', '.join(created_directories)}")
    if all_exist:
        print("All necessary directories already exist.")
    else:
        existing_directories = [folder for folder in folders if folder not in created_directories]
        if existing_directories:
            print(f"All other directories already exist: {', '.join(existing_directories)}")

def main():
    # Create sub-folders relative to the base directory
    create_directories(base_directory, sub_folders)

if __name__ == "__main__":
    main()
