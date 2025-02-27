import csv
import re
import os
from collections import Counter
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
from screeninfo import get_monitors

# Constants
CSV_FILE_NAME = "rymsponsoredwithnames.csv"
DATE_FORMAT = "%B {day_with_ordinal} %Y"

# Get the script's directory and change the working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Regular expression pattern to match the lines (if needed for processing)
pattern = re.compile(r'^(.*?):\s*(.*?)\s*$')

def count_album_occurrences(csv_file):
    """Read the CSV file and count occurrences of artist and album titles."""
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

def save_album_counts_to_csv(csv_file, album_counter, input_entries):
    """Save the updated album counts to the CSV file in reversed order."""
    with open(csv_file, 'a', encoding='utf-8') as file:
        for line in reversed(input_entries):
            try:
                username, album = line.split(': ', 1)
            except ValueError:
                continue  # Skip lines that do not match the expected format
            count = album_counter[album]
            file.write(f'{username},"{album}",{count}\n')

def process_new_entries(new_entries, album_counter):
    """Process new entries and update the album counter."""
    for line in new_entries:
        try:
            username, album = line.split(': ', 1)
        except ValueError:
            continue  # Skip lines that do not match the expected format
        album_counter[album] += 1

def ordinal(n):
    """Convert a number to its ordinal representation."""
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

def process_input(new_entries):
    """Process the input from the GUI and return output messages for display."""
    process_new_entries(new_entries, album_counter)
    
    today_date = datetime.now()
    day = today_date.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    day_with_ordinal = f"{day}{suffix}"
    formatted_date = today_date.strftime(DATE_FORMAT.format(day_with_ordinal=day_with_ordinal))

    output_messages = []
    for line in new_entries:
        try:
            username, album = line.split(': ', 1)
        except ValueError:
            continue
        count = album_counter[album]
        ordinal_count = ordinal(count)
        output_messages.append(f"{username}\n\n{formatted_date}\n\n{ordinal_count} time sponsored\n")
    
    return output_messages[::-1]

def display_processed_entries(output_messages):
    """Display the processed entries in the GUI."""
    output_text = "\n\n".join(output_messages)
    output_text_area.config(state=tk.NORMAL)
    output_text_area.delete(1.0, tk.END)
    output_text_area.insert(tk.END, output_text)
    output_text_area.config(state=tk.DISABLED)

def on_submit():
    """Handle the Submit button click in the GUI."""
    new_entries = text_area.get("1.0", tk.END).strip().split('\n')
    if not new_entries or new_entries == ['']:
        messagebox.showerror("Error", "No entries provided")
        return

    output_messages = process_input(new_entries)
    display_processed_entries(output_messages)
    save_album_counts_to_csv(csv_file, album_counter, new_entries)
    print("Script has executed successfully")

# Define the correct file path
csv_file = os.path.join(script_dir, CSV_FILE_NAME)
album_counter = count_album_occurrences(csv_file)

# Create the GUI application
root = tk.Tk()
root.title("Enter New Entries")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

input_label = tk.Label(frame, text="Enter New Entries:")
input_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='nw')

text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=20)
text_area.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

output_label = tk.Label(frame, text="Processed Entries:")
output_label.grid(row=0, column=1, padx=10, pady=(10, 0), sticky='nw')

output_text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
output_text_area.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')

frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)

submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.pack(pady=5)

root.mainloop()
