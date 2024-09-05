import os
import shutil
import zipfile
import json
import time
from datetime import datetime

# Define paths
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_path = os.path.join(base_path, 'Logs')
archived_path = os.path.join(logs_path, 'Archived')
archive_log_path = os.path.join(logs_path, 'archive_log.json')

# Define the size threshold in bytes (e.g., 5MB)
size_threshold = 1 * 1024 * 1024 * 1024  # 1GB

# Define lock retry settings
max_retries = 5
retry_delay = 2  # seconds

# Ensure the Archived directory exists
os.makedirs(archived_path, exist_ok=True)

def log_archiving_action(filename, archive_name):
    log_entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "filename": filename,
        "archive_name": archive_name
    }
    
    # Read existing log entries if the log file exists
    if os.path.exists(archive_log_path):
        with open(archive_log_path, 'r') as log_file:
            log_data = json.load(log_file)
    else:
        log_data = []

    # Append the new log entry
    log_data.append(log_entry)

    # Write the updated log data back to the log file
    with open(archive_log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)

def archive_file(file_path, filename):
    # Create a zip file named based on the current month
    archive_name = datetime.now().strftime('%Y-%m') + '.zip'
    archive_path = os.path.join(archived_path, archive_name)
    
    retries = 0
    while retries < max_retries:
        try:
            # Add the file to the zip archive
            with zipfile.ZipFile(archive_path, 'a') as archive:
                archive.write(file_path, arcname=filename)
            
            # Remove the original file after archiving
            os.remove(file_path)
            
            log_archiving_action(filename, archive_name)
            break  # Exit loop if successful
        except (PermissionError, FileNotFoundError) as e:
            print(f"Error archiving {filename}: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retries += 1

def check_and_archive_files():
    # Iterate over all files in the Logs directory
    for filename in os.listdir(logs_path):
        file_path = os.path.join(logs_path, filename)
        
        # Skip directories and the archive log file
        if os.path.isdir(file_path) or filename == os.path.basename(archive_log_path):
            continue
        
        # Check the size of the file
        file_size = os.path.getsize(file_path)
        
        # If the file size exceeds the threshold, archive it
        if file_size > size_threshold:
            archive_file(file_path, filename)
            print(f"Archived {filename} ({file_size} bytes)")

if __name__ == "__main__":
    check_and_archive_files()
