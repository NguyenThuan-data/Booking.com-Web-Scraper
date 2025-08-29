import express from 'express';
import cheerio from 'cheerio';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.urlencoded({ extended: true }));

const INDEX_HTML = `<!doctype html>
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
</html>`;

app.get('/', (req, res) => {
  res.type('html').send(INDEX_HTML);
});

function escapeCsv(value) {
  if (value == null) return '';
  const str = String(value);
  if (/[",\n]/.test(str)) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}

function rowsToCsv(rows, headers) {
  const lines = [];
  lines.push(headers.join(','));
  for (const row of rows) {
    lines.push(headers.map(h => escapeCsv(row[h])).join(','));
  }
  return lines.join('\n');
}

app.post('/scrape', async (req, res) => {
  const { url, filename } = req.body || {};
  if (!url || !filename) {
    return res.status(400).send('Missing url or filename');
  }

  try {
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    };
    const response = await fetch(url, { headers });
    if (!response.ok) {
      return res.status(response.status).send(`Failed to fetch page: ${response.status}`);
    }
    const html = await response.text();

    const $ = cheerio.load(html);
    const cards = $('div[role="listitem"]');

    const rows = [];
    cards.each((_, el) => {
      const $el = $(el);

      const hotelName = $el.find('div.b87c397a13.a3e0b4ffd1').text().trim();
      const location = $el.find('span.d823fbbeed.f9b3563dd4').text().trim();
      const priceRaw = $el.find('span.b87c397a13.f2f358d1de.ab607752a2').text().trim();
      const price = priceRaw.replace('NZD ', '');

      const review = $el.find('div.fff1944c52.fb14de7f14.eaa8455879').text().trim() || 'No reviews yet';
      const rating = $el.find('div.f63b14ab7a.f546354b44.becbee2f63').text().trim() || 'New to Booking.com';
      const score = $el.find('div.f63b14ab7a.dff2e52086').text().trim() || 'New to Booking.com';
      const link = $el.find('a[href]').attr('href') || '';

      if (!hotelName && !location && !price && !rating && !score && !review && !link) {
        return; // skip empty
      }

      rows.push({
        'Hotel Name': hotelName,
        'Location': location,
        'Price': price,
        'Rating': rating,
        'Score': score,
        'Review': review,
        'Link': link,
      });
    });

    const headerOrder = ['Hotel Name', 'Location', 'Price', 'Rating', 'Score', 'Review', 'Link'];
    const csv = rowsToCsv(rows, headerOrder);

    res.setHeader('Content-Disposition', `attachment; filename=${filename}.csv`);
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.send(csv);
  } catch (err) {
    res.status(500).send(`Unexpected error: ${err instanceof Error ? err.message : String(err)}`);
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
