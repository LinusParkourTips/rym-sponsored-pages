Script to automate data entry of this list: https://rateyourmusic.com/list/LinusParkourTips/every-sponsored-page-on-rym/

Copy the new rows from this page: https://rateyourmusic.com/subscribe/supported_pages

Run process_new_entries.py, paste the data and it checks the csv database for information regarding how many times an entry is already there, then it adds the new data properly formatted to both the txt file and csv file.

The txt file isn't really needed, however I started with it and I'm keeping it for now in case the script has some fatal flaws I haven't noticed or any other reasons I can't think of.
