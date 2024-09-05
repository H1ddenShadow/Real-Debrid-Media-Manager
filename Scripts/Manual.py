import os
import subprocess

# Define paths and scripts
base_path = os.path.dirname(os.path.abspath(__file__))
scripts_to_run = [
    'Data.py',
    'Torrent.py',
    'Add.py'
]

def main_task():
    for script in scripts_to_run:
        script_path = os.path.join(base_path, script)
        print(f"Running {script_path}...")
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        print(f"Output of {script}:")
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error running {script}:")
            print(result.stderr)
            break  # Stop execution if any script fails

if __name__ == "__main__":
    main_task()
