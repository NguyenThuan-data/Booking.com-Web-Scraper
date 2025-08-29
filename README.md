# Booking.com Web Scraper

Scrape hotel search results from Booking.com and export them to CSV for easy comparison. Built with Python and BeautifulSoup.
I build this app for my friend, a secretary of VAUSA, who cost a lot of time to check for accomodation for the club retreat

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip
- Git (optional, for cloning)

### Installation
1. Clone the repository
   ```sh
   git clone https://github.com/NguyenThuan-data/Booking.com-Web-Scraper.git
   ```
2. Change into the project directory
   ```sh
   cd "Booking.com-Web-Scraper"
   ```
3. (Optional) Create and activate a virtual environment
   - macOS/Linux:
     ```sh
     python3 -m venv .venv && source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     py -m venv .venv; .venv\Scripts\Activate.ps1
     ```
4. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```

---

## 🔧 Usage
You can use this project in three ways: Web UI, CLI, or as a Python module.

### 1) Web UI (Flask)
Run the web app and use a browser to download a CSV.
```sh
python app.py
```
Then open http://localhost:3000 and:
- Paste a Booking.com search URL (e.g., a page listing hotels for a destination/date range)
- Enter a filename (without .csv)
- Click “Scrape & Download CSV”

### 2) Command Line (interactive)
Run the script and follow the prompts.
```sh
python web_scrape.py
```
You will be asked for:
- URL: a Booking.com search results page URL
- File name: base name for the CSV

The CSV (e.g., my-hotels.csv) will be saved in the current directory.

### 3) As a Python module
Use functions directly in your own code.
```python
from web_scrape import web_scraper, fetch_html, parse_hotels

# High-level: fetch, parse, and write CSV. Returns number of rows.
row_count = web_scraper(
    "https://www.booking.com/searchresults.html?ss=auckland",
    "my-hotels",
)
print(f"Exported {row_count} rows.")

# Lower-level: fetch and parse without writing a file
html = fetch_html("https://www.booking.com/searchresults.html?ss=auckland")
rows = parse_hotels(html)
# rows is a list of dicts with keys: Hotel Name, Location, Price, Rating, Score, Review, Link
```

---

## 🗂️ Output
- A CSV file is created with columns: Hotel Name, Location, Price, Rating, Score, Review, Link.
- File is saved as <filename>.csv in the current directory.

---

## ❗ Notes & Troubleshooting
- Booking.com may change its HTML structure; scraping may need maintenance.
- If requests fail with HTTP errors, try again later or adjust headers/network. Basic browser-like headers are already included.
- Ensure lxml is installed (installed via requirements.txt) for faster/more reliable parsing.
- Use responsibly and review the website’s terms of service before scraping.

---

## 📦 Tech Stack
- Python, Flask, requests, BeautifulSoup, lxml
