import os
import signal
import json
import time

# Define the base path and the path to the PID JSON file in the 'Scheduled Runs' folder
base_path = os.path.dirname(os.path.abspath(__file__))
scheduled_runs_path = os.path.join(base_path, '..', 'Scheduled Runs')
pid_file_path = os.path.join(scheduled_runs_path, 'schedule_pid.json')

# Check if the PID JSON file exists
if os.path.exists(pid_file_path):
    # Read the PID from the JSON file
    try:
        with open(pid_file_path, 'r') as pid_file:
            pid_data = json.load(pid_file)
            pid = pid_data.get("pid")
            
            if pid is not None:
                # Try to kill the process
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"Schedule.py with PID {pid} has been stopped.")
                    
                    # Add a small delay to ensure the process has terminated
                    time.sleep(2)
                except ProcessLookupError:
                    print(f"No process with PID {pid} found.")
                except Exception as e:
                    print(f"Failed to kill process with PID {pid}: {e}")
            else:
                print("PID not found in the JSON file.")
    except json.JSONDecodeError:
        print("Failed to decode the PID JSON file.")
    except IOError as e:
        print(f"Error reading PID JSON file: {e}")
else:
    print("PID JSON file not found. Is Schedule.py running?")
