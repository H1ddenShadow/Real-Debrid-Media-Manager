import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import ttkbootstrap as tb

# URLs for donation platforms
DONATION_URLS = {
    "Ko-Fi": "https://ko-fi.com/H1ddenShadow",
    "BuyMeACoffee": "https://www.buymeacoffee.com/H1ddenShadow",
    "Patreon": "https://www.patreon.com/H1ddenShadow",
}

def open_donation_page(platform):
    url = DONATION_URLS.get(platform)
    if url:
        webbrowser.open(url)
        root.focus_set()  # Set focus back to the root window
    else:
        messagebox.showerror("Error", "URL for selected platform is not configured.")

def show_donation_ui():
    for widget in root.winfo_children():
        widget.destroy()
    
    label = tb.Label(root, text="Choose a donation platform:", font=("Helvetica", 20, 'bold'), anchor='center', background='lightgrey')
    label.pack(pady=30)
    
    button_frame = tb.Frame(root, style="Custom.TFrame")
    button_frame.pack(pady=30)

    for platform in DONATION_URLS:
        button = tb.Button(button_frame, text=f"Donate via {platform}", command=lambda p=platform: open_donation_page(p), bootstyle="info-outline")
        button.pack(pady=15, padx=30, fill=tk.X)

def main_menu():
    for widget in root.winfo_children():
        widget.destroy()
    
    label = tb.Label(root, text="Support Our Cause", font=("Helvetica", 20, 'bold'), anchor='center', background='lightgrey')
    label.pack(pady=30)
    
    button_frame = tb.Frame(root, style="Custom.TFrame")
    button_frame.pack(pady=30)

    options = [
        ("1. Ko-Fi", "Ko-Fi"),
        ("2. BuyMeACoffee", "BuyMeACoffee"),
        ("3. Patreon", "Patreon"),
        ("4. Exit", "Exit")
    ]

    for text, platform in options:
        button = tb.Button(button_frame, text=text, command=lambda p=platform: open_donation_page(p) if p != "Exit" else root.quit(), bootstyle="success-outline" if platform != "Exit" else "danger-outline")
        button.pack(pady=15, padx=30, fill=tk.X)

if __name__ == "__main__":
    root = tb.Window(themename="flatly")  # Changed theme for a modern look
    root.title("Donation Application")
    root.geometry("500x500")
    root.configure(background='lightgrey')  # Set background color to light grey
    
    # Define a style for the ttk.Frame with the desired background color
    style = ttk.Style()
    style.configure("Custom.TFrame", background='lightgrey')
    
    main_menu()
    root.mainloop()
