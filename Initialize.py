import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import git
import shutil
import threading
import ttkbootstrap as tb

# List of necessary dependencies
REQUIRED_PACKAGES = [
    "requests",
    "pickle",
    "ttkbootstrap",
    "gitpython"
]

def install_packages():
    """Check and install required packages."""
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Call the function to install packages
install_packages()

# FAQ and Tutorial content
FAQ_CONTENT = """
FAQ Section:
1. How do I clone the repository?
   - Users may clone the repository by running the 'Initialize.py' script in their terminal and then selecting the 'Clone Repository' whereafter they are to follow the steps accordingly.

2. How do I download the folders?
   - On the 'GitHub' page, click the green 'Code' button which appears towards the top-right of a users screen and there, there should be a 'Download Zip' option which should allow users to download the folders and their data in a zip file. .

3. Where can I get help?
   - Visit the GitHub repository's issues section or contact support.

4. How do I retrieve my Api Keys?
   - Users who wish to retrieve their api keys may refrence the respective services' guides on how to retrieve your api keys.
   - Once retrieved, users may run the 'Setup.py' script to save said keys.

5. How does this script work?
   - The script works by utilizing various endpoints to connect to a users 'Trakt' account, retrieve their list data, 'Watchlist' and 'Favourites', and fetch the magnet counterparts of said media before adding it to their 'Real-Debrid' account.

6. Why am I facing errors with the 'Scheduled Runs' times as well as the relevant time fields not being updated?
  - The times present in the 'Schedule.py' script are merely default vaules and adjusting the values from there, after already having run the script, will lead to the changes being reflected unless the user: deletes the created 'scheduled_runs.json' file and stops the script, so users who wish to make changes to the times are suggested to either do so:
 
  1. Before running the respective script, initially (the first time) or
  2. By running the 'Stop.py' script and then editing the times in the 'scheduled_runs.json' file, which can be found in the 'Scheduled Runs' folder.

7. How do I run or start the script?
  - Users are provided with two options in terms of running the script, where they could either: run the script once, 'Run.py', or keep it running continuously, 'Start.py'; in the event that they wish to stop running the script, they may then run the following script: 'Stop.py' and should they wish to disable the script completetly, they may then update the 'enabled' field in the 'scheduled_runs.json' file to reflect the 'false' setting.
"""

TUTORIAL_CONTENT = """
Tutorial Section:
1. Getting Started.
   - Install the 'Initialize.py' script and run it in your terminal, alternatively, the necessary folders may be downloaded from 'https://github.com/H1ddenShadow/Real-Debrid-Media-Manager.git' and the 'Setup.py' script, found in the 'Scripts' folder, ran; it's highly suggested that users make use of the former script mentioned earlier and those who wish to make use of the latter option must rename the unzipped folder to 'Real Debrid Media Manager'.

Note: Users who choose to download the folders in a zip file from the 'GitHub' repository must rename the unzipped folder to 'Real Debrid Media Manager' or else this will cause issues with the program.

2. Cloning a Repository.
   - Select the 'Clone Repository' option after running the script and in the now opened window, select your preferred directoty..
   - Wait for the cloning process to complete; the relevant progress will be shown on the screen.
Note: ALthough a 'renaming' feature is present, it does not work as expected so it's rather suggested that users clone the repository in a non-empty directory (folder) so as to avoid issues when the program runs.

3. Retrieving a users Api Keys.
   - Trakt:
	- Users must create a 'Trakt' account, if not already existent, wherafter, they should head to the 'Settings' tab which should be found under their name/profile tab.
	- There, they should then find a 'Your API Apps' tab and select the 'New Application' option.
	- In the 'Name' field, a name of the users choosing must be used, whereafter, they must paste the second uri, 'urn:ietf:wg:oauth:2.0:oob', in the 'Redirect uri' field and lastly check both the available options for the 'Permissions' field.
	- Clicking on the 'Save App' button should allow users to create the app in question.
	- Users are to then note the 'Client ID' and 'Secret' of said app.
   - Authorization Code:
	- The 'Trakt Authorization Code' may be retrieved by clicking the 'Authorize' button under the 'Redirect URI:' field and should be noted as it'll be used later on in the program. 

   - Real-Debrid:
	- A 'Real-Debrid' account will have to be created/existent with an active subscription as well as a current session (logged in).
	- Users should then head to the respective API page to retrieve their API Key.

   - TMDB:
	- A 'TMDB' account is not necessary but could, however, be utilized in future for logging purposes.
	- For convience, users may find their API Key by heading to the documentaion page and selecting 'Get API Key'.

4. Setting up the program.
   - Users may run the 'Setup.py' script which can be found in the 'Scripts' folder.
   - In the requested fields, users should paste in the respecive keys and those being their: 'Client ID', 'Client Secret', 'Authorization Code', 'Real-Debrid API Key' and 'TMDB API Key'. 

   - Retrieving the 'Authorization Code':
	- Users may retrieve their 'Trakt Authorization Code' by clicking the 'Authorize' button under the 'Redirect URI:' field.
   - Lastly, users may then run the 'Run.py' script to run the script once or the 'Start.py' script to begin continous running.

Note: The default values will ensure that the script is ran in the early morning, afternoon and evening: 08:00, 12:00 and 18:00, respectively before running off and starting back up the following day. Any changes that the user hopes to make may be made to the 'Schedule.py' file before either the 'Run.py' or 'Start.py' scripts are ran, although it's highly suggested that the former script is ran to create the necessary file with the default values, whereafter users may feel free to edit the times in said file. The 'Stop.py' should be ran before any changes may be made to the file, and of course, this being if the user has opted to run the latter script; this being done to avoid any issues with the script reading or utilizing the wrong times. Lastly, it should be noted that the last available time should have no comma after the qoutations: (""), for example:
"17:00", 
"18:00", 
"20:00"
would be correct, however:

"17:00", 
"18:00", 
"20:00",
would be incorrect and would instead result in there being issues when the data is read.

5. Making Donations.
   - Donations may be made by running the 'Donations.py' script and then selcting your prefered donation method/service.

6. Getting Help.
   - For more information, visit the FAQ section or check out the repository's documentation for additional guidance.
"""

# URLs
REPO_URL = 'https://github.com/H1ddenShadow/Real-Debrid-Media-Manager.git'
FOLDER_URL = 'https://github.com/H1ddenShadow/Real-Debrid-Media-Manager/raw/main/'

def scroll_up(event, canvas):
    canvas.yview_scroll(-1, "units")

def scroll_down(event, canvas):
    canvas.yview_scroll(1, "units")

def scroll_to_top(event, canvas):
    canvas.yview_moveto(0)

def scroll_to_bottom(event, canvas):
    canvas.yview_moveto(1)

def bind_keys(window, canvas):
    window.bind_all('<Up>', lambda event: scroll_up(event, canvas))
    window.bind_all('<Down>', lambda event: scroll_down(event, canvas))
    window.bind_all('<w>', lambda event: scroll_up(event, canvas))
    window.bind_all('<s>', lambda event: scroll_down(event, canvas))
    window.bind_all('<Left>', lambda event: scroll_to_top(event, canvas))
    window.bind_all('<Right>', lambda event: scroll_to_bottom(event, canvas))
    window.bind_all('<a>', lambda event: scroll_to_top(event, canvas))
    window.bind_all('<d>', lambda event: scroll_to_bottom(event, canvas))

def show_faq():
    faq_window = tb.Toplevel(root)
    faq_window.title("FAQ")
    faq_window.attributes('-fullscreen', True)  # Open in full-screen

    # Create a canvas and styled scrollbar
    canvas = tk.Canvas(faq_window)
    scrollbar = ttk.Scrollbar(faq_window, orient="vertical", command=canvas.yview)
    
    # Create a frame to contain the FAQ content
    faq_frame = tk.Frame(canvas)
    
    # Add the FAQ content to the frame
    faq_label = tb.Label(faq_frame, text=FAQ_CONTENT, wraplength=750, justify=tk.LEFT)
    faq_label.pack(padx=10, pady=10)
    
    # Add the frame to the canvas
    canvas.create_window((0, 0), window=faq_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack the canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Update the scroll region of the canvas
    faq_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    
    # Create a frame for buttons in the top-right corner
    button_frame = tb.Frame(faq_window)
    button_frame.pack(side=tk.TOP, anchor='ne', pady=30, padx=30)
    
    back_button = tb.Button(button_frame, text="Back", command=faq_window.destroy)
    back_button.pack(side=tk.LEFT, padx=5)
    
    exit_button = tb.Button(button_frame, text="Exit", command=root.quit)
    exit_button.pack(side=tk.LEFT, padx=5)

    # Bind the keys for scrolling
    bind_keys(faq_window, canvas)

def show_tutorial():
    tutorial_window = tb.Toplevel(root)
    tutorial_window.title("Tutorial")
    tutorial_window.attributes('-fullscreen', True)  # Open in full-screen

    # Create a canvas and styled scrollbar
    canvas = tk.Canvas(tutorial_window)
    scrollbar = ttk.Scrollbar(tutorial_window, orient="vertical", command=canvas.yview)
    
    # Create a frame to contain the tutorial content
    tutorial_frame = tk.Frame(canvas)
    
    # Add the tutorial content to the frame
    tutorial_label = tb.Label(tutorial_frame, text=TUTORIAL_CONTENT, wraplength=750, justify=tk.LEFT)
    tutorial_label.pack(padx=10, pady=10)
    
    # Add the frame to the canvas
    canvas.create_window((0, 0), window=tutorial_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack the canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Update the scroll region of the canvas
    tutorial_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    
    # Create a frame for buttons in the top-right corner
    button_frame = tb.Frame(tutorial_window)
    button_frame.pack(side=tk.TOP, anchor='ne', pady=30, padx=30)
    
    back_button = tb.Button(button_frame, text="Back", command=tutorial_window.destroy)
    back_button.pack(side=tk.LEFT, padx=5)
    
    exit_button = tb.Button(button_frame, text="Exit", command=root.quit)
    exit_button.pack(side=tk.LEFT, padx=5)

    # Bind the keys for scrolling
    bind_keys(tutorial_window, canvas)

def clone_repository(progress_var):
    repo_path = filedialog.askdirectory()
    if repo_path:
        # Determine the final clone path
        final_clone_path = os.path.join(repo_path, "Real Debrid Media Manager")
        
        # Check if the selected path is empty
        if not os.listdir(repo_path):  # Check if the directory is empty
            clone_path = repo_path
        else:
            clone_path = final_clone_path
            # Create the directory if it does not exist
            if not os.path.exists(clone_path):
                os.makedirs(clone_path)
        
        try:
            # Initialize the progress bar
            progress_var.set(0)
            progress_bar.pack(pady=10)  # Show the progress bar
            root.update_idletasks()

            # Clone the repository
            repo = git.Repo.clone_from(REPO_URL, clone_path, progress=progress_callback(progress_var))
            
            # Rename the directory if cloning into an empty directory
            if clone_path != repo_path:
                repo_dir_name = os.path.basename(REPO_URL).replace(".git", "")
                repo_dir_path = os.path.join(clone_path, repo_dir_name)
                if os.path.exists(repo_dir_path):
                    shutil.move(repo_dir_path, final_clone_path)

            # Delete the Initialize.py file if it exists
            initialize_file_path = os.path.join(final_clone_path, 'Initialize.py')
            if os.path.exists(initialize_file_path):
                os.remove(initialize_file_path)

            messagebox.showinfo("Success", "Repository cloned and Initialize.py deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clone repository or delete file: {e}")
        finally:
            progress_bar.pack_forget()  # Hide the progress bar after completion

def progress_callback(progress_var):
    def update(op_code, cur_count, max_count=None, message=''):
        if max_count:
            progress = (cur_count / max_count) * 100
            progress_var.set(progress)
            root.update_idletasks()
    return update

def clone_repository_thread():
    threading.Thread(target=clone_repository, args=(progress_var,)).start()

def main_menu():
    for widget in root.winfo_children():
        widget.destroy()
    
    label = tb.Label(root, text="Choose an option:", font=("Helvetica", 16))
    label.pack(pady=10)
    
    button_frame = tb.Frame(root)
    button_frame.pack(pady=10)

    options = [
        ("1. FAQ", show_faq),
        ("2. Clone Repository", clone_repository_thread),
        ("3. Tutorial", show_tutorial),
        ("4. Exit", root.quit)
    ]

    for text, command in options:
        button = tb.Button(button_frame, text=text, command=command)
        button.pack(pady=5, padx=10, fill=tk.X, anchor='w')  # Add anchor='w' to align left and add padding

    global progress_var
    progress_var = tk.DoubleVar()
    global progress_bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progress_var)
    progress_bar.pack_forget()  # Initially hide the progress bar

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    root.title("GitHub Repository Manager")
    root.geometry("400x300")
    
    main_menu()
    root.mainloop()