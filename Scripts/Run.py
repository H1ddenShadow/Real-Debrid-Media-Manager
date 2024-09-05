import subprocess

# Define the paths to your scripts
scripts = ['Data.py', 'Torrent.py', 'Add.py']

# Function to run a script
def run_script(script):
    try:
        result = subprocess.run(['python', script], check=True, capture_output=True, text=True)
        print(f"Output of {script}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}:\n{e.stderr}")

# Run the scripts in order
for script in scripts:
    run_script(script)
