import csv
import re
import os
from collections import Counter
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Constants
CSV_FILE_NAME = "rymsponsoredwithnames.csv"
DATE_FORMAT = "%B {day_with_ordinal} %Y"

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

pattern = re.compile(r'^(.*?):\s*(.*?)\s*$')


def count_album_occurrences(csv_file):
    counter = Counter()
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    counter[row[1]] += 1
    except FileNotFoundError:
        pass
    return counter


def save_album_counts_to_csv(csv_file, album_counter, input_entries):
    with open(csv_file, 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for line in reversed(input_entries):
            try:
                username, album = line.split(': ', 1)
            except ValueError:
                continue
            writer.writerow([username, album, album_counter[album]])


def process_new_entries(new_entries, album_counter):
    for line in new_entries:
        try:
            _, album = line.split(': ', 1)
        except ValueError:
            continue
        album_counter[album] += 1


def ordinal(n):
    words = {
        1: 'First', 2: 'Second', 3: 'Third', 4: 'Fourth',
        5: 'Fifth', 6: 'Sixth', 7: 'Seventh', 8: 'Eighth', 9: 'Ninth'
    }
    if n in words:
        return words[n]
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1:'st',2:'nd',3:'rd'}.get(n%10,'th') }"


def process_input(new_entries):
    process_new_entries(new_entries, album_counter)

    today = datetime.now()
    day = today.day
    suffix = 'th' if 10 <= day % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    date_str = today.strftime(DATE_FORMAT.format(day_with_ordinal=f"{day}{suffix}"))

    items = []
    for line in new_entries:
        try:
            username, album = line.split(': ', 1)
        except ValueError:
            continue
        count = album_counter[album]
        text = f"{username}\n\n{date_str}\n\n{ordinal(count)} time sponsored"
        items.append({"album": album, "text": text})
    return items[::-1]


def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()


def show_processed_view(items):
    input_frame.pack_forget()
    output_frame.pack(fill=tk.BOTH, expand=True)

    for w in output_frame.winfo_children():
        w.destroy()

    cols = 3
    HIGHLIGHT_BG = "#b6d7ff"

    selected = {"card": None, "labels": []}

    def clear_selection():
        if selected["card"] is None:
            return
        selected["card"].config(bg=root.cget('bg'))
        for lbl in selected["labels"]:
            lbl.config(bg=root.cget('bg'))
        selected["card"] = None
        selected["labels"] = []

    def select_card(card, labels):
        clear_selection()
        card.config(bg=HIGHLIGHT_BG)
        for lbl in labels:
            lbl.config(bg=HIGHLIGHT_BG)
        selected["card"] = card
        selected["labels"] = labels

    for i, item in enumerate(items):
        r, c = divmod(i, cols)

        card = tk.Frame(output_frame, bd=1, relief=tk.SOLID, padx=10, pady=4)
        card.grid(row=r, column=c, sticky='nsew', padx=8, pady=8)
        card.config(cursor='hand2')

        output_frame.columnconfigure(c, weight=1, uniform='cards')
        output_frame.rowconfigure(r, weight=1)

        album_label = tk.Label(
            card,
            text=item['album'],
            fg='black',
            font=('TkDefaultFont', 10, 'bold'),
            justify='left',
            anchor='w',
            cursor='hand2'
        )

        album_label.pack(anchor='w', fill=tk.X, pady=(0, 2))

        text_label = tk.Label(
            card,
            text=item['text'],
            justify='left',
            anchor='w',
            cursor='hand2'
        )
        text_label.pack(anchor='w', fill=tk.X)

        def on_click(event, t=item['text'], crd=card, lbls=(album_label, text_label)):
            copy_to_clipboard(t)
            select_card(crd, list(lbls))

        card.bind('<Button-1>', on_click)
        album_label.bind('<Button-1>', on_click)
        text_label.bind('<Button-1>', on_click)

        def resize(event, lbl=text_label, alb=album_label, container=card):
            wrap = container.winfo_width() - 20
            if wrap > 50:
                lbl.config(wraplength=wrap)
                alb.config(wraplength=wrap)

        card.bind('<Configure>', resize)


def on_submit():
    new_entries = text_area.get('1.0', tk.END).strip().split('\n')
    if not new_entries or new_entries == ['']:
        messagebox.showerror('Error', 'No entries provided')
        return

    items = process_input(new_entries)
    save_album_counts_to_csv(csv_file, album_counter, new_entries)
    show_processed_view(items)


# Init data
csv_file = os.path.join(script_dir, CSV_FILE_NAME)
album_counter = count_album_occurrences(csv_file)

# GUI
root = tk.Tk()
root.title('RYM Sponsorship Tool')
root.geometry('1000x900')

input_frame = tk.Frame(root)
input_frame.pack(fill=tk.BOTH, expand=True)

output_frame = tk.Frame(root)

input_label = tk.Label(input_frame, text='Enter New Entries:')
input_label.pack(anchor='nw', padx=10, pady=(10, 0))

text_area = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD)
text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

submit_button = tk.Button(input_frame, text='Submit', command=on_submit)
submit_button.pack(pady=10)

root.mainloop()
