import csv
import os
from collections import Counter
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ============================================================
# Configuration constants
# ============================================================

CSV_FILE_NAME = "rymsponsoredwithnames.csv"

DATE_FORMAT = "%B {day_with_ordinal} %Y"

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900

CARD_COLUMNS = 3
OUTER_PADDING = 64
CARD_INNER_PADDING = 25

HIGHLIGHT_BG = "#b6d7ff"

# ============================================================
# Path setup
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

CSV_PATH = os.path.join(SCRIPT_DIR, CSV_FILE_NAME)

# ============================================================
# Data / domain logic
# ============================================================

def count_album_occurrences(csv_file: str) -> Counter:
    counter = Counter()
    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    counter[row[1]] += 1
    except FileNotFoundError:
        pass
    return counter


def save_album_counts_to_csv(csv_file: str, album_counter: Counter, entries: list[str]) -> None:
    with open(csv_file, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for line in reversed(entries):
            try:
                username, album = line.split(": ", 1)
            except ValueError:
                continue
            writer.writerow([username, album, album_counter[album]])


def process_new_entries(entries: list[str], album_counter: Counter) -> None:
    for line in entries:
        try:
            _, album = line.split(": ", 1)
        except ValueError:
            continue
        album_counter[album] += 1


def ordinal(n: int) -> str:
    words = {
        1: "First", 2: "Second", 3: "Third",
        4: "Fourth", 5: "Fifth", 6: "Sixth",
        7: "Seventh", 8: "Eighth", 9: "Ninth"
    }
    if n in words:
        return words[n]
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1:'st', 2:'nd', 3:'rd'}.get(n % 10, 'th') }"


def build_date_string(day_offset: int) -> str:
    today = datetime.now() - timedelta(days=day_offset)
    day = today.day
    suffix = "th" if 10 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return today.strftime(DATE_FORMAT.format(day_with_ordinal=f"{day}{suffix}"))


def process_input(entries: list[str]) -> list[dict]:
    process_new_entries(entries, album_counter)

    date_str = build_date_string(day_offset)

    cards = []
    for line in entries:
        try:
            username, album = line.split(": ", 1)
        except ValueError:
            continue

        count = album_counter[album]

        card_text = (
            f"{username}\n\n"
            f"{date_str}\n\n"
            f"{ordinal(count)} time sponsored"
        )

        cards.append({
            "album": album,
            "username": username,
            "count": count,
            "text": card_text
        })

    return cards[::-1]


def apply_day_offset(cards: list[dict]) -> list[dict]:
    date_str = build_date_string(day_offset)
    new_cards = []
    for item in cards:
        new_text = (
            f"{item['username']}\n\n"
            f"{date_str}\n\n"
            f"{ordinal(item['count'])} time sponsored"
        )
        new_cards.append({
            "album": item["album"],
            "username": item["username"],
            "count": item["count"],
            "text": new_text
        })
    return new_cards

# ============================================================
# Clipboard helper
# ============================================================

def copy_to_clipboard(text: str) -> None:
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

# ============================================================
# UI rendering
# ============================================================

def show_processed_view(items: list[dict]) -> None:
    input_frame.pack_forget()

    output_container.pack(fill=tk.BOTH, expand=True)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    for widget in output_frame.winfo_children():
        widget.destroy()

    # ============================================================
    # Buttons: -1 Day and +1 Day
    # ============================================================

    btn_frame = tk.Frame(output_frame)
    btn_frame.grid(row=0, column=0, columnspan=CARD_COLUMNS, pady=10)

    def subtract_one_day():
        global day_offset
        day_offset += 1
        updated = apply_day_offset(items)
        show_processed_view(updated)

    def add_one_day():
        global day_offset
        day_offset -= 1
        updated = apply_day_offset(items)
        show_processed_view(updated)

    minus_button = tk.Button(btn_frame, text="-1 Day", command=subtract_one_day)
    minus_button.pack(side=tk.LEFT, padx=10)

    plus_button = tk.Button(btn_frame, text="+1 Day", command=add_one_day)
    plus_button.pack(side=tk.LEFT, padx=10)

    # ============================================================
    # Layout math
    # ============================================================

    usable_width = WINDOW_WIDTH - OUTER_PADDING
    base_width = usable_width / CARD_COLUMNS
    wrap_length = int(base_width - CARD_INNER_PADDING)

    for col in range(CARD_COLUMNS):
        output_frame.columnconfigure(
            col,
            minsize=int(base_width),
            weight=1,
            uniform="cards"
        )

    selected = {"card": None, "labels": []}

    def clear_selection():
        if not selected["card"]:
            return
        selected["card"].config(bg=root.cget("bg"))
        for lbl in selected["labels"]:
            lbl.config(bg=root.cget("bg"))
        selected["card"] = None
        selected["labels"] = []

    def select_card(card, labels):
        clear_selection()
        card.config(bg=HIGHLIGHT_BG)
        for lbl in labels:
            lbl.config(bg=HIGHLIGHT_BG)
        selected["card"] = card
        selected["labels"] = labels

    start_row = 1

    for index, item in enumerate(items):
        row, col = divmod(index, CARD_COLUMNS)
        row += start_row

        card = tk.Frame(output_frame, bd=1, relief=tk.SOLID, padx=10, pady=6)
        card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

        album_label = tk.Label(
            card,
            text=item["album"],
            font=("TkDefaultFont", 10, "bold"),
            anchor="w",
            justify="left",
            wraplength=wrap_length
        )
        album_label.pack(anchor="w", fill=tk.X, pady=(0, 4))

        text_label = tk.Label(
            card,
            text=item["text"],
            anchor="w",
            justify="left",
            wraplength=wrap_length
        )
        text_label.pack(anchor="w", fill=tk.X)

        def on_click(event, t=item["text"], crd=card, lbls=(album_label, text_label)):
            copy_to_clipboard(t)
            select_card(crd, list(lbls))

        for widget in (card, album_label, text_label):
            widget.bind("<Button-1>", on_click)

    output_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# ============================================================
# Event handlers
# ============================================================

def on_submit():
    raw_text = text_area.get("1.0", tk.END).strip()
    if not raw_text:
        messagebox.showerror("Error", "No entries provided")
        return

    entries = raw_text.split("\n")

    items = process_input(entries)
    save_album_counts_to_csv(CSV_PATH, album_counter, entries)
    show_processed_view(items)

# ============================================================
# Application bootstrap
# ============================================================

album_counter = count_album_occurrences(CSV_PATH)
day_offset = 0

root = tk.Tk()
root.title("RYM Sponsorship Tool")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+3440+380")
root.minsize(1000, 400)
root.maxsize(1800, 1000)

input_frame = tk.Frame(root)
input_frame.pack(fill=tk.BOTH, expand=True)

output_container = tk.Frame(root)

canvas = tk.Canvas(output_container, highlightthickness=0)
scrollbar = tk.Scrollbar(output_container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

output_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=output_frame, anchor="nw")

input_label = tk.Label(input_frame, text="Enter New Entries:")
input_label.pack(anchor="nw", padx=10, pady=(10, 0))

text_area = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD)
text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

submit_button = tk.Button(input_frame, text="Submit", command=on_submit)
submit_button.pack(pady=10)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-event.delta / 120), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

root.mainloop()
