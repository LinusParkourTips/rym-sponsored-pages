import csv
import re
from collections import Counter
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
from screeninfo import get_monitors

# Regular expression pattern to match the lines
pattern = re.compile(r'^(.*?):\s*(.*?)\s*(\d+)$')

# Function to process each line and extract the required components
def process_line(line):
    match = pattern.match(line)
    if match:
        username = match.group(1)
        album = match.group(2)
        number = match.group(3)
        return username, album, number
    else:
        return None

# Function to read the CSV file and count occurrences of artist and album titles
def count_album_occurrences(csv_file):
    counter = Counter()
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:  # Ensure row has at least two values
                album = row[1]
                counter[album] += 1
    return counter

# Function to process new entries and add the correct number
def process_new_entries(new_entries, album_counter):
    processed_entries = []
    for line in new_entries:
        username, album = line.split(': ', 1)  # Split only on the first ': '
        count = album_counter[album] + 1
        album_counter[album] = count  # Update the counter correctly
        processed_entries.append(f'{username}: {album} {count}')
    return processed_entries

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

# Paths to the input files
csv_file = 'rymsponsoredwithnames.csv'
output_txt_file = 'rymsponsoredwithnames.txt'
script_file = 'script.py' 

# Count occurrences of artist and album titles in the existing CSV file
album_counter = count_album_occurrences(csv_file)

# Function to process the input from the GUI
def process_input(new_entries):
    # Process the new entries and prepare output for the text file
    processed_entries = process_new_entries(new_entries, album_counter)
    with open(output_txt_file, 'a', encoding='utf-8') as outfile:
        # Ensure the first new entry starts on a new line if the file is not empty
        if outfile.tell() > 0:
            outfile.write('\n')
        for i, entry in enumerate(reversed(processed_entries)):
            # Check if it's the last entry
            if i == len(processed_entries) - 1:
                outfile.write(entry)
            else:
                outfile.write(f'{entry}\n')

    # Get today's date with ordinal suffix and year
    today_date = datetime.now()
    day = today_date.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    day_with_ordinal = f"{day}{suffix}"
    formatted_date = today_date.strftime(f"%B {day_with_ordinal} %Y")

    # Print the formatted output to the console
    output_messages = []
    for entry in new_entries:
        username = entry.split(':', 1)[0]
        album = entry.split(': ', 1)[1]
        count = album_counter[album]
        ordinal_count = ordinal(count)
        output_messages.append(f"{username}\n\n{formatted_date}\n\n{ordinal_count} time sponsored\n")

    return output_messages[::-1]  # Reverse the order of output messages

# Function to display the processed entries in the same window
def display_processed_entries(output_messages):
    output_text = "\n\n".join(output_messages)
    
    # Insert the processed entries into the output text area
    output_text_area.config(state=tk.NORMAL)
    output_text_area.delete(1.0, tk.END)
    output_text_area.insert(tk.END, output_text)
    output_text_area.config(state=tk.DISABLED)  # Make the text area read-only

# Function to handle button click
def on_submit():
    new_entries = text_area.get("1.0", tk.END).strip().split('\n')
    if not new_entries or new_entries == ['']:
        messagebox.showerror("Error", "No entries provided")
        return

    output_messages = process_input(new_entries)
    display_processed_entries(output_messages)

    # Close the output text file
    with open(output_txt_file, 'a', encoding='utf-8') as outfile:
        pass  # Just opening and closing the file to release the lock

    # Run the script after writing to the output file
    print("Running the script...")
    subprocess.run(['python', script_file])
    print("Script executed successfully.")

# Create the GUI application
root = tk.Tk()
root.title("Enter New Entries")

# Create a frame for the input and output areas
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create and place input text area
input_label = tk.Label(frame, text="Enter New Entries:")
input_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='nw')

text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=20)
text_area.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

# Create and place output text area
output_label = tk.Label(frame, text="Processed Entries:")
output_label.grid(row=0, column=1, padx=10, pady=(10, 0), sticky='nw')

output_text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)
output_text_area.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')

# Configure the grid to make the text areas expand with the window
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)

# Create and place submit button
submit_button = tk.Button(root, text="Submit", command=on_submit)
submit_button.pack(pady=5)

# Get monitor information and set the position of the window
monitors = get_monitors()
if len(monitors) > 1:
    right_monitor = max(monitors, key=lambda m: m.x)
    root.geometry(f"+{right_monitor.x}+{right_monitor.y}")

# Run the GUI application
root.mainloop()
