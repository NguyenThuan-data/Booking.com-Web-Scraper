from io import StringIO
import csv
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
    </style>
  </head>
  <body>
    <main class=\"page\">
      <section class=\"card\">
        <h1 class=\"title\">Booking.com Scraper</h1>
        <p class=\"subtitle\">Enter a Booking.com search URL. You'll get a CSV download of the parsed results.</p>
        <form method=\"post\" action=\"/scrape\">
          <div class=\"field\">
            <label for=\"url\" class=\"label\">Search URL</label>
            <input id=\"url\" name=\"url\" type=\"url\" class=\"input\" placeholder=\"https://www.booking.com/searchresults.html?...\" required />
          </div>
          <div class=\"field\">
            <label for=\"filename\" class=\"label\">File name (without .csv)</label>
            <input id=\"filename\" name=\"filename\" type=\"text\" class=\"input\" placeholder=\"my-hotels\" required />
          </div>
          <div class=\"actions\">
            <button class=\"button\" type=\"submit\">Scrape & Download CSV</button>
            <span class=\"hint\">Scrape may take a few seconds.</span>
          </div>
        </form>
        <p class=\"footer\">This tool performs best-effort parsing and may miss data if Booking.com markup changes.</p>
      </section>
    </main>
  </body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(INDEX_HTML)


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
