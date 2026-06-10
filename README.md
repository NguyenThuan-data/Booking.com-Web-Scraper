# Booking.com Web Scraper

> A small tool I built for a real user — the secretary of a Vietnamese university club (VAUSA) who spent hours comparing accommodation options for club retreats.

---

## The challenge

- **User pain:** Manual copy-paste from Booking.com search results for every retreat planning cycle.
- **Technical:** Booking.com HTML changes often; scraping requires maintenance and respectful use.
- **Scope:** Export structured hotel data (name, location, price, rating, link) to CSV for side-by-side comparison.

## What I learned

- Building for a **named user with a named workflow** beats generic "scraper tutorials."
- A simple Flask UI helps non-technical friends more than a CLI alone.
- Scrapers are **liability projects** — document breakage honestly and don't oversell reliability.

## How this leveled me up

| | |
|---|---|
| **Before** | I consumed web data in notebooks only |
| **After** | I shipped a small product someone else actually used |
| **Unlocked next** | Plugin-based crawlers (see [Global Job Intelligence System](https://github.com/NguyenThuan-data/Global-Job-Intelligence-System)) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/NguyenThuan-data/Booking.com-Web-Scraper.git
cd Booking.com-Web-Scraper
pip install -r requirements.txt
```

Optional virtual environment (Windows PowerShell):

```powershell
py -m venv .venv; .venv\Scripts\Activate.ps1
```

---

## Usage

### 1) Web UI (Flask)

```bash
python app.py
```

Open `http://localhost:3000`, paste a Booking.com **search results** URL, enter a filename, and download CSV.

### 2) Command line (interactive)

```bash
python web_scrape.py
```

Follow prompts for URL and output filename.

### 3) Python module

```python
from web_scrape import web_scraper

row_count = web_scraper(
    "https://www.booking.com/searchresults.html?ss=auckland",
    "my-hotels",
)
print(f"Exported {row_count} rows.")
```

---

## Output

CSV columns: **Hotel Name**, **Location**, **Price**, **Rating**, **Score**, **Review**, **Link**.

---

## Honest notes

- **May break without warning** when Booking.com changes page structure — this is expected for scrapers.
- Review Booking.com's terms of service; use responsibly and for legitimate personal/club planning only.
- Not recommended as a primary portfolio pin unless you add a fresh demo recording; better as a "real user story" supporting project.

---

## Tech stack

Python · Flask · requests · BeautifulSoup · lxml
