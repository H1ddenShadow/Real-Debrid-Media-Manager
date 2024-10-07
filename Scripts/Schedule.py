import os
import json
import time
from datetime import datetime, timedelta
import threading
import subprocess

# Define paths
base_path = os.path.dirname(os.path.abspath(__file__))
scheduled_runs_path = os.path.join(base_path, '..', 'Scheduled Runs', 'scheduled_runs.json')
logs_path = os.path.join(base_path, '..', 'Logs', 'execution_log.json')
lock_file_path = os.path.join(base_path, '..', 'Logs', 'lock_file.lock')

# Define the scripts to run
scripts_to_run = [
    'Data.py',
    'Torrent.py',
    'Add.py'
]
archiver_script = 'Archiver.py'

# Define the lock wait time
lock_wait_time = timedelta(minutes=2)
# Define the delay before running Archiver.py
archiver_delay = timedelta(minutes=1)

# Function to create the JSON configuration file
def create_schedule_config():
    if not os.path.exists(scheduled_runs_path):
        schedule_config = {
            "enabled": True,  # Set to True to enable scheduling
            "times": [
                "08:00",
                "12:00",
                "18:00"
            ]
        }
        os.makedirs(os.path.dirname(scheduled_runs_path), exist_ok=True)
        with open(scheduled_runs_path, 'w') as file:
            json.dump(schedule_config, file, indent=4)
        print(f"Schedule configuration file created at {scheduled_runs_path}")

# Function to load the schedule configuration
def load_schedule_config():
    if not os.path.exists(scheduled_runs_path):
        create_schedule_config()
    
    with open(scheduled_runs_path, 'r') as file:
        return json.load(file)

# Function to get the next scheduled time
def get_next_scheduled_time(schedule_times):
    now = datetime.now()
    today = now.date()
    
    # Convert schedule times to datetime objects for today
    schedule_datetimes = [datetime.strptime(time_str, "%H:%M").replace(year=today.year, month=today.month, day=today.day) for time_str in schedule_times]
    
    # Find the next scheduled time
    future_times = [time for time in schedule_datetimes if time > now]
    if future_times:
        return min(future_times)
    else:
        # If no future times today, return the first time for tomorrow
        return min(schedule_datetimes) + timedelta(days=1)

# Function to log messages to the JSON log file
def log_message(message):
    os.makedirs(os.path.dirname(logs_path), exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    }
    
    try:
        if os.path.exists(logs_path):
            with open(logs_path, 'r') as file:
                logs = json.load(file)
        else:
            logs = []
    except (json.JSONDecodeError, IOError):
        logs = []  # Handle case where the file is empty or corrupt

    logs.append(log_entry)

    try:
        with open(logs_path, 'w') as file:
            json.dump(logs, file, indent=4)
    except IOError as e:
        print(f"Error writing to log file: {e}")

# Function to create or check the lock file
def acquire_lock():
    if os.path.exists(lock_file_path):
        with open(lock_file_path, 'r') as file:
            last_lock_time = datetime.fromisoformat(file.read().strip())
        now = datetime.now()
        if now - last_lock_time < lock_wait_time:
            return False
    with open(lock_file_path, 'w') as file:
        file.write(datetime.now().isoformat())
    return True

# Function to release the lock file
def release_lock():
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)

# Function to run a script and log its output
def run_script(script_name):
    script_path = os.path.join(base_path, script_name)
    log_message(f"Running {script_path}...")
    print(f"Running {script_path}...")
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    log_message(f"Output of {script_name}: {result.stdout}")
    print(f"Output of {script_name}:")
    print(result.stdout)
    if result.returncode != 0:
        log_message(f"Error running {script_name}: {result.stderr}")
        print(f"Error running {script_name}:")
        print(result.stderr)

# Function to run the Archiver.py script
def run_archiver():
    script_path = os.path.join(base_path, archiver_script)
    log_message(f"Running {script_path}...")
    print(f"Running {script_path}...")
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    log_message(f"Output of {archiver_script}: {result.stdout}")
    print(f"Output of {archiver_script}:")
    print(result.stdout)
    if result.returncode != 0:
        log_message(f"Error running {archiver_script}: {result.stderr}")
        print(f"Error running {archiver_script}:")
        print(result.stderr)

# Function to check if the current time matches any of the scheduled times
def check_schedule():
    schedule_config = load_schedule_config()
    
    if not schedule_config.get("enabled", False):
        log_message("Scheduled runs are disabled.")
        print("Scheduled runs are disabled.")
        return  # Exit without running Manual.py if scheduling is disabled
    
    current_time = datetime.now().strftime("%H:%M")
    scheduled_times = schedule_config.get("times", [])
    
    if current_time in scheduled_times:
        log_message(f"Running scheduled task at {current_time}")
        print(f"Running scheduled task at {current_time}")
        main_task()
    else:
        log_message(f"No scheduled task at {current_time}")

# Function to run the main task
def main_task():
    # Acquire lock before running scripts
    if acquire_lock():
        try:
            for script in scripts_to_run:
                run_script(script)
            # After running the main scripts, check if it's time to run Archiver.py
            schedule_config = load_schedule_config()
            last_time = max(schedule_config.get("times", []))
            now = datetime.now()
            last_time_dt = datetime.strptime(last_time, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            
            # Calculate the time when Archiver.py should run
            archiver_run_time = last_time_dt + archiver_delay
            
            if now >= archiver_run_time and now < archiver_run_time + timedelta(minutes=1):
                run_archiver()
        finally:
            release_lock()
    else:
        log_message("Lock not acquired. Another process might be running.")

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule_config = load_schedule_config()
        if not schedule_config.get("enabled", False):
            log_message("Scheduled runs are disabled. Exiting scheduler.")
            print("Scheduled runs are disabled. Exiting scheduler.")
            return  # Exit the function to stop the scheduler
        
        next_time = get_next_scheduled_time(schedule_config.get("times", []))
        sleep_duration = (next_time - datetime.now()).total_seconds()
        
        log_message(f"Next scheduled task at {next_time}. Sleeping for {sleep_duration} seconds.")
        print(f"Next scheduled task at {next_time}. Sleeping for {sleep_duration} seconds.")
        time.sleep(sleep_duration)
        
        check_schedule()

# Entry point
if __name__ == "__main__":
    # Create the schedule configuration file if it doesn't exist
    create_schedule_config()
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Keep the main thread alive only if the scheduler is running
    schedule_config = load_schedule_config()
    if schedule_config.get("enabled", False):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Interrupted by user. Exiting.")
            log_message("Script interrupted by user. Exiting.")
