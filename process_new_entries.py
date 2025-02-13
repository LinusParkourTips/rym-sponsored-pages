import csv
import re
import os
from collections import Counter
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
from screeninfo import get_monitors


# Get the script's directory and change the working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Regular expression pattern to match the lines (if needed for processing)
pattern = re.compile(r'^(.*?):\s*(.*?)\s*$')

# Function to read the CSV file and count occurrences of artist and album titles
def count_album_occurrences(csv_file):
    counter = Counter()
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:  # Ensure row has at least two values
                    album = row[1]
                    counter[album] += 1
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' does not exist.")
    return counter

# Function to save the updated album counts to the CSV file in reversed order
def save_album_counts_to_csv(csv_file, album_counter, input_entries):
    # Write directly to the CSV file without using csv.writer
    with open(csv_file, 'a', encoding='utf-8') as file:
        # Process the input entries in reverse order
        for line in reversed(input_entries):
            # Each input line is expected to be in the format: username: album
            try:
                username, album = line.split(': ', 1)
            except ValueError:
                continue  # Skip lines that do not match the expected format
            count = album_counter[album]
            # Build the CSV line exactly as you want it:
            # username,"album",count
            file.write(f'{username},"{album}",{count}\n')

# Function to process new entries and update the album counter
def process_new_entries(new_entries, album_counter):
    for line in new_entries:
        try:
            username, album = line.split(': ', 1)
        except ValueError:
            continue  # Skip lines that do not match the expected format
        # Increment the count for this album
        album_counter[album] += 1

# Function to convert a number to its ordinal representation
def ordinal(n):
    ordinal_words = {
        1: 'First', 2: 'Second', 3: 'Third', 4: 'Fourth', 
        5: 'Fifth', 6: 'Sixth', 7: 'Seventh', 8: 'Eighth', 9: 'Ninth'
    }
    if 1 <= n <= 9:
        return ordinal_words[n]
    else:
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f'{n}{suffix}'

# Define the correct file path
csv_file = os.path.join(script_dir, "rymsponsoredwithnames.csv")

# Count occurrences of artist and album titles in the existing CSV file
album_counter = count_album_occurrences(csv_file)

# Function to process the input from the GUI and return output messages for display
def process_input(new_entries):
    # Update album counts with the new entries
    process_new_entries(new_entries, album_counter)
    
    # Get today's date with ordinal suffix and year
    today_date = datetime.now()
    day = today_date.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    day_with_ordinal = f"{day}{suffix}"
    formatted_date = today_date.strftime(f"%B {day_with_ordinal} %Y")

    # Build output messages for each input line
    output_messages = []
    for line in new_entries:
        try:
            username, album = line.split(': ', 1)
        except ValueError:
            continue
        count = album_counter[album]
        ordinal_count = ordinal(count)
        output_messages.append(f"{username}\n\n{formatted_date}\n\n{ordinal_count} time sponsored\n")
    
    # Reverse the order of output messages for display
    return output_messages[::-1]

# Function to display the processed entries in the GUI
def display_processed_entries(output_messages):
    output_text = "\n\n".join(output_messages)
    output_text_area.config(state=tk.NORMAL)
    output_text_area.delete(1.0, tk.END)
    output_text_area.insert(tk.END, output_text)
    output_text_area.config(state=tk.DISABLED)

# Function to handle the Submit button click in the GUI
def on_submit():
    new_entries = text_area.get("1.0", tk.END).strip().split('\n')
    if not new_entries or new_entries == ['']:
        messagebox.showerror("Error", "No entries provided")
        return

    # Process the input and display the output messages
    output_messages = process_input(new_entries)
    display_processed_entries(output_messages)

    # Save the updated entries to the CSV file in reversed order using our custom formatting
    save_album_counts_to_csv(csv_file, album_counter, new_entries)
    messagebox.showinfo("Success", "Entries processed and saved successfully!")

# Create the GUI application
root = tk.Tk()
root.title("Enter New Entries")

# Create a frame for the input and output areas
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Input text area for new entries
input_label = tk.Label(frame, text="Enter New Entries:")
input_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='nw')

text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=20)
text_area.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

# Output text area to display processed entries
output_label = tk.Label(frame, text="Processed Entries:")
output_label.grid(row=0, column=1, padx=10, pady=(10, 0), sticky='nw')

output_text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
output_text_area.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')

# Configure grid resizing behavior
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)

# Submit button
submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.pack(pady=5)

# Get screen dimensions using screeninfo
monitors = get_monitors()
if len(monitors) >= 3:
    # Assuming the third monitor is the right monitor
    right_monitor = monitors[2]
    right_monitor_width = right_monitor.width
    right_monitor_height = right_monitor.height

    # Set the window position to the right monitor
    x_position = right_monitor.x + 50  # 50 pixels from the left edge of the right monitor
    y_position = 50  # 50 pixels from the top of the right monitor

    # Set window geometry
    window_width = 1000
    window_height = 500
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
else:
    messagebox.showerror("Error", "Less than 3 monitors detected. Cannot position on the right monitor.")
    root.quit()

root.mainloop()
