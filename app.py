from io import StringIO
import csv
from typing import List, Dict

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, PlainTextResponse

from web_scrape import fetch_html, parse_hotels

app = FastAPI(title="Booking.com Scraper")


def rows_to_csv(rows: List[Dict[str, str]]) -> str:
    buf = StringIO()
    writer = csv.DictWriter(
        buf,
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
    return buf.getvalue()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (
        """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Booking.com Scraper</title>
            <style>
              :root { --bg: #0b1b2b; --card: #10273d; --text: #e6f1ff; --muted: #a8c0d6; --accent: #3ea8ff; }
              body { margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; background: var(--bg); color: var(--text); }
              .page-wrap { min-height: 100vh; display: grid; place-items: center; padding: 24px; }
              .panel { width: 100%; max-width: 720px; background: var(--card); border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); }
              .heading { margin: 0 0 8px; font-weight: 700; font-size: 22px; }
              .subtle { margin: 0 0 24px; color: var(--muted); font-size: 14px; }
              .field { display: grid; gap: 8px; margin: 0 0 16px; }
              .label { font-size: 14px; color: var(--muted); }
              .input { width: 100%; border: 1px solid #214462; background: #0d2236; color: var(--text); border-radius: 10px; padding: 12px 14px; font-size: 14px; }
              .actions { display: flex; gap: 12px; align-items: center; justify-content: flex-start; margin-top: 8px; }
              .button { background: var(--accent); color: #071421; border: none; border-radius: 999px; padding: 10px 16px; font-weight: 600; cursor: pointer; }
              .hint { color: var(--muted); font-size: 12px; }
              .footer { margin-top: 20px; font-size: 12px; color: var(--muted); }
            </style>
          </head>
          <body>
            <main class="page-wrap">
              <section class="panel">
                <h1 class="heading">Booking.com Scraper</h1>
                <p class="subtle">Enter a Booking.com search URL. You'll get a CSV download of the parsed results.</p>
                <form method="post" action="/scrape">
                  <div class="field">
                    <label for="url" class="label">Search URL</label>
                    <input id="url" name="url" type="url" class="input" placeholder="https://www.booking.com/searchresults.html?..." required />
                  </div>
                  <div class="field">
                    <label for="filename" class="label">File name (without .csv)</label>
                    <input id="filename" name="filename" type="text" class="input" placeholder="my-hotels" required />
                  </div>
                  <div class="actions">
                    <button class="button" type="submit">Scrape & Download CSV</button>
                    <span class="hint">Scrape may take a few seconds.</span>
                  </div>
                </form>
                <p class="footer">This tool performs best-effort parsing and may miss data if Booking.com markup changes.</p>
              </section>
            </main>
          </body>
        </html>
        """
    )


@app.post("/scrape")
async def scrape(url: str = Form(...), filename: str = Form(...)):
    html = fetch_html(url)
    rows = parse_hotels(html)

    csv_text = rows_to_csv(rows)

    headers = {
        "Content-Disposition": f"attachment; filename={filename}.csv"
    }
    return PlainTextResponse(content=csv_text, media_type="text/csv", headers=headers)
