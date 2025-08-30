from io import StringIO
import csv
from datetime import datetime
from urllib.parse import urlencode

from flask import Flask, request, Response, render_template_string
from web_scrape import fetch_html, parse_hotels

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Booking.com Scraper</title>
    <style>
      :root { --bg: #0b1b2b; --card: #10273d; --text: #e6f1ff; --muted: #a8c0d6; --accent: #3ea8ff; }
      body { margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; background: var(--bg); color: var(--text); }
      .page { min-height: 100vh; display: grid; place-items: center; padding: 24px; }
      .card { width: 100%; max-width: 720px; background: var(--card); border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); }
      .title { margin: 0 0 8px; font-weight: 700; font-size: 22px; }
      .subtitle { margin: 0 0 24px; color: var(--muted); font-size: 14px; }
      .field { display: grid; gap: 8px; margin: 0 0 16px; }
      .label { font-size: 14px; color: var(--muted); }
      .input { width: 100%; border: 1px solid #214462; background: #0d2236; color: var(--text); border-radius: 10px; padding: 12px 14px; font-size: 14px; }
      .actions { display: flex; gap: 12px; align-items: center; justify-content: flex-start; margin-top: 8px; }
      .button { background: var(--accent); color: #071421; border: none; border-radius: 999px; padding: 10px 16px; font-weight: 600; cursor: pointer; }
      .hint { color: var(--muted); font-size: 12px; }
      .footer { margin-top: 20px; font-size: 12px; color: var(--muted); }
      .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
      @media (max-width: 640px) { .row { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <main class=\"page\">
      <section class=\"card\">
        <h1 class=\"title\">Booking.com Scraper</h1>
        <p class=\"subtitle\">Enter your search details. We'll build the Booking.com URL for you to review before scraping.</p>
        <form method=\"post\" action=\"/build\">
          <div class=\"field\">
            <label for=\"destination\" class=\"label\">Destination</label>
            <input id=\"destination\" name=\"destination\" type=\"text\" class=\"input\" placeholder=\"Auckland\" required />
          </div>
          <div class=\"row\">
            <div class=\"field\">
              <label for=\"checkin\" class=\"label\">Check-in</label>
              <input id=\"checkin\" name=\"checkin\" type=\"date\" class=\"input\" required />
            </div>
            <div class=\"field\">
              <label for=\"checkout\" class=\"label\">Check-out</label>
              <input id=\"checkout\" name=\"checkout\" type=\"date\" class=\"input\" required />
            </div>
          </div>
          <div class=\"row\">
            <div class=\"field\">
              <label for=\"adults\" class=\"label\">Adults</label>
              <input id=\"adults\" name=\"adults\" type=\"number\" min=\"1\" step=\"1\" value=\"2\" class=\"input\" />
            </div>
            <div class=\"field\">
              <label for=\"rooms\" class=\"label\">Rooms</label>
              <input id=\"rooms\" name=\"rooms\" type=\"number\" min=\"1\" step=\"1\" value=\"1\" class=\"input\" />
            </div>
          </div>
          <div class=\"field\">
            <label for=\"sort\" class=\"label\">Sort by</label>
            <select id=\"sort\" name=\"sort\" class=\"input\">
              <option value=\"popularity\">Most popular</option>
              <option value=\"price\">Lowest price</option>
              <option value=\"bayesian_review_score\">Top reviewed</option>
            </select>
          </div>
          <div class=\"field\">
            <label for=\"filename\" class=\"label\">File name (without .csv)</label>
            <input id=\"filename\" name=\"filename\" type=\"text\" class=\"input\" placeholder=\"my-hotels\" required />
          </div>
          <div class=\"actions\">
            <button class=\"button\" type=\"submit\">Build Search</button>
            <span class=\"hint\">You'll confirm before scraping.</span>
          </div>
        </form>
        <p class=\"footer\">This tool performs best-effort parsing and may miss data if Booking.com markup changes.</p>
      </section>
    </main>
  </body>
</html>
"""


def build_booking_url(destination: str, checkin: str, checkout: str, adults: int, rooms: int, sort: str) -> str:
    def ymd(d: str):
        dt = datetime.strptime(d, "%Y-%m-%d")
        return dt.year, dt.month, dt.day

    ci_y, ci_m, ci_d = ymd(checkin)
    co_y, co_m, co_d = ymd(checkout)

    params = {
        "ss": destination,
        "checkin_year": ci_y,
        "checkin_month": ci_m,
        "checkin_monthday": ci_d,
        "checkout_year": co_y,
        "checkout_month": co_m,
        "checkout_monthday": co_d,
        "group_adults": adults,
        "no_rooms": rooms,
        "order": sort or "popularity",
    }
    return "https://www.booking.com/searchresults.html?" + urlencode(params)


PREVIEW_HTML = """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Confirm Search</title>
    <style>
      :root { --bg: #0b1b2b; --card: #10273d; --text: #e6f1ff; --muted: #a8c0d6; --accent: #3ea8ff; }
      body { margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; background: var(--bg); color: var(--text); }
      .page { min-height: 100vh; display: grid; place-items: center; padding: 24px; }
      .card { width: 100%; max-width: 720px; background: var(--card); border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); }
      .title { margin: 0 0 8px; font-weight: 700; font-size: 22px; }
      .subtitle { margin: 0 0 24px; color: var(--muted); font-size: 14px; }
      .field { display: grid; gap: 8px; margin: 0 0 16px; }
      .label { font-size: 14px; color: var(--muted); }
      .input { width: 100%; border: 1px solid #214462; background: #0d2236; color: var(--text); border-radius: 10px; padding: 12px 14px; font-size: 14px; }
      .actions { display: flex; gap: 12px; align-items: center; justify-content: flex-start; margin-top: 8px; }
      .button { background: var(--accent); color: #071421; border: none; border-radius: 999px; padding: 10px 16px; font-weight: 600; cursor: pointer; }
      .hint { color: var(--muted); font-size: 12px; }
      .footer { margin-top: 20px; font-size: 12px; color: var(--muted); }
      .url { word-break: break-all; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background:#0d2236; border:1px solid #214462; border-radius:10px; padding:10px 12px; }
      .row { display:flex; gap:10px; flex-wrap:wrap; }
      .link { color: inherit; text-decoration: none; }
    </style>
  </head>
  <body>
    <main class=\"page\">
      <section class=\"card\">
        <h1 class=\"title\">Confirm your search</h1>
        <p class=\"subtitle\">We built this Booking.com URL from your inputs. You can open it to review, then proceed to scrape.</p>
        <div class=\"field\">
          <div class=\"label\">Search URL</div>
          <div class=\"url\">{{ url }}</div>
        </div>
        <div class=\"row\">
          <a class=\"link button\" href=\"{{ url }}\" target=\"_blank\" rel=\"noopener noreferrer\">Open on Booking.com</a>
          <form method=\"post\" action=\"/scrape\">
            <input type=\"hidden\" name=\"url\" value=\"{{ url }}\" />
            <input type=\"hidden\" name=\"filename\" value=\"{{ filename }}\" />
            <button class=\"button\" type=\"submit\">Scrape & Download CSV</button>
          </form>
          <form method=\"get\" action=\"/\"><button class=\"button\" type=\"submit\">Back</button></form>
        </div>
        <p class=\"footer\">This tool performs best-effort parsing and may miss data if Booking.com markup changes.</p>
      </section>
    </main>
  </body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(INDEX_HTML)


@app.post("/build")
def build():
    destination = (request.form.get("destination") or "").strip()
    checkin = (request.form.get("checkin") or "").strip()
    checkout = (request.form.get("checkout") or "").strip()
    adults = int(request.form.get("adults") or 2)
    rooms = int(request.form.get("rooms") or 1)
    sort = (request.form.get("sort") or "popularity").strip()
    filename = (request.form.get("filename") or "results").strip()

    if not destination or not checkin or not checkout or not filename:
        return ("Missing required fields", 400)

    try:
        url = build_booking_url(destination, checkin, checkout, adults, rooms, sort)
    except Exception as e:
        return (f"Invalid input: {e}", 400)

    return render_template_string(PREVIEW_HTML, url=url, filename=filename)


@app.post("/scrape")
def scrape():
    url = (request.form.get("url") or "").strip()
    filename = (request.form.get("filename") or "results").strip()
    if not url or not filename:
        return ("Missing url or filename", 400)

    html = fetch_html(url)
    rows = parse_hotels(html)

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

    csv_text = buf.getvalue()
    headers = {"Content-Disposition": f"attachment; filename={filename}.csv"}
    return Response(csv_text, mimetype="text/csv", headers=headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
