# This app scrapes data from booking.com

import csv
import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

# Use lxml parser if available via BeautifulSoup

# Default headers to mimic a common browser to reduce basic bot blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}


def fetch_html(web_url: str, timeout: int = 20) -> str:
    """Fetch page HTML with a desktop-like user agent.

    Raises requests.HTTPError on bad responses.
    """
    res = requests.get(web_url, headers=HEADERS, timeout=timeout)
    res.raise_for_status()
    return res.text


def parse_hotels(html: str) -> List[Dict[str, str]]:
    """Parse hotel cards from Booking search HTML into a list of dict rows.

    This is best-effort: it tolerates missing elements.
    """
    soup = BeautifulSoup(html, "lxml")

    rows: List[Dict[str, str]] = []

    # Booking uses role=listitem for result cards currently
    hotel_divs = soup.find_all("div", role="listitem")

    for hotel in hotel_divs:
        def safe_text(find_result, default: str = "") -> str:
            try:
                if not find_result:
                    return default
                text = getattr(find_result, "text", None)
                if text is None:
                    return default
                return text.strip()
            except Exception:
                return default

        # These classnames are brittle and may change; we handle "not found" gracefully.
        name_el = hotel.find("div", class_="b87c397a13 a3e0b4ffd1")
        location_el = hotel.find("span", class_="d823fbbeed f9b3563dd4")
        price_el = hotel.find("span", class_="b87c397a13 f2f358d1de ab607752a2")
        review_container = hotel.find("div", class_="fff1944c52 fb14de7f14 eaa8455879")
        rating_el = hotel.find("div", class_="f63b14ab7a f546354b44 becbee2f63")
        score_el = hotel.find("div", class_="f63b14ab7a dff2e52086")
        link_el = hotel.find("a", href=True)

        hotel_name = safe_text(name_el)
        hotel_location = safe_text(location_el)
        price_raw = safe_text(price_el)
        price = price_raw.replace("NZD ", "") if price_raw else ""

        review = safe_text(review_container, default="No reviews yet")
        rating = safe_text(rating_el, default="New to Booking.com")
        score = safe_text(score_el, default="New to Booking.com")
        link = link_el.get("href") if link_el and link_el.has_attr("href") else ""

        # Skip completely empty rows
        if not any([hotel_name, hotel_location, price, rating, score, review, link]):
            continue

        rows.append(
            {
                "Hotel Name": hotel_name,
                "Location": hotel_location,
                "Price": price,
                "Rating": rating,
                "Score": score,
                "Review": review,
                "Link": link,
            }
        )

    return rows


def save_to_csv(rows: List[Dict[str, str]], file_name: str) -> None:
    """Save parsed rows into a CSV file with the given base file name (no extension)."""
    with open(f"{file_name}.csv", "w", newline="", encoding="utf-8") as file_csv:
        writer = csv.DictWriter(
            file_csv,
            fieldnames=[
                "Hotel Name",
                "Location",
                "Price",
                "Rating",
                "Score",
                "Review",
                "Link",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def web_scraper(web_url: str, file_name: str) -> int:
    """High-level scraper: fetch, parse, and write to CSV. Returns row count."""
    print("Hi welcome to the show!\nStart now!")
    time.sleep(1)

    html = fetch_html(web_url)
    rows = parse_hotels(html)
    save_to_csv(rows, file_name)

    print(f"Saved {len(rows)} rows to {file_name}.csv")
    return len(rows)


if __name__ == "__main__":
    web_url = input("Please enter URL: ")
    file_name = input("please enter the stored file's name: ")
    try:
        count = web_scraper(web_url, file_name)
        print(f"Completed. {count} records exported.")
    except requests.HTTPError as http_err:
        print(f"Connection failed! HTTP error: {http_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
