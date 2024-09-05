import os
import subprocess
import json
import sys

# Define the path to the Schedule.py script
schedule_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Schedule.py')

# Define the base path and the path to the PID JSON file in the 'Scheduled Runs' folder
base_path = os.path.dirname(os.path.abspath(__file__))
scheduled_runs_path = os.path.join(base_path, '..', 'Scheduled Runs')
pid_file_path = os.path.join(scheduled_runs_path, 'schedule_pid.json')

# Ensure the directory for the PID file exists
os.makedirs(scheduled_runs_path, exist_ok=True)

try:
    # Start the Schedule.py script in the background
    process = subprocess.Popen([sys.executable, schedule_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Save the PID to a JSON file
    pid_data = {"pid": process.pid}
    with open(pid_file_path, 'w') as pid_file:
        json.dump(pid_data, pid_file)
    
    print(f"Schedule.py started with PID {process.pid}")
except Exception as e:
    print(f"Failed to start Schedule.py: {e}")
