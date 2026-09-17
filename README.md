# TwinTimes

A local-first personal news intelligence dashboard. TwinTimes ingests RSS/Atom and arXiv feeds, normalizes them into SQLite, scores each story against a transparent personal profile, deduplicates near-identical headlines, and builds a calm daily briefing.

## Why this exists

Most news apps optimize for engagement. Twin optimizes for *relevance to one person* while preserving a discovery budget so the feed does not collapse into a filter bubble.

## Features

- Zero third-party Python dependencies (Python 3.11+ recommended)
- Local SQLite database
- RSS + Atom + arXiv ingestion
- Transparent weighted ranking
- Topic/entity/geography scoring
- Basic headline deduplication
- Three focused dashboards: top news, interactive interest sections, and deeper research reads
- Strict editorial source lanes: Nature/arXiv appear only in Deeper Reads; general news comes from journalistic publishers and Google News feeds
- Feedback: More / Less / Important / Surprised me
- **Newsmarks**: a dedicated local reading-queue page, with Today filtering and email delivery
- **Information Diet**: local daily engagement graphs by topic and source
- Curated podcast recommendations
- Editable `profile.json` and `sources.json`
- Background refresh every 30 minutes while the app is running (configurable)
- Localhost only by default (`127.0.0.1`)
- Manifest V3 Chrome extension with narrowly scoped localhost access

## Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8787
```

Click **Refresh** once. The app also refreshes automatically every 30 minutes while running. Set `TWIN_REFRESH_MINUTES` to change the interval.

## Chrome extension

TwinTimes now includes a Manifest V3 extension in `extension/`. The extension is
the browser interface; the local Python service continues to handle RSS,
ranking, SQLite, and email so personal data and SMTP credentials stay outside
Chrome.

Build and load it locally:

```bash
python scripts/build_extension.py
./run.sh
```

Then open `chrome://extensions`, enable **Developer mode**, choose **Load
unpacked**, and select the repository's `extension` directory. Pin TwinTimes and
click its toolbar icon to open the dashboard.

Whenever the web UI changes, rerun `python scripts/build_extension.py` before
committing. The extension requests access only to the TwinTimes service on
`127.0.0.1:8787` and `localhost:8787`.

## Email today's Newsmarks

The Newsmarks page can preview an email without any setup. Sending is manual: open Newsmarks and click **Email today's Newsmarks**. No Python or JavaScript edits are required.

The easiest setup is to copy `.env.example` to `.env`, fill in your SMTP details, and start with `./run.sh`. Alternatively, export the same values in your shell:

```bash
export TWIN_SMTP_HOST="smtp.example.com"
export TWIN_SMTP_PORT="587"
export TWIN_SMTP_USER="you@example.com"
export TWIN_SMTP_PASSWORD="your-app-password"
export TWIN_SMTP_FROM="you@example.com"
python app.py
```

For Gmail, use an app password rather than your normal account password. These values stay in the local process and are never sent to the browser.

## Configure your twin

Edit `profile.json` to change topic weights, aliases, regions, tracked entities, preferred sources, and noise terms.

Edit `sources.json` to add any RSS or Atom feed:

```json
{"name":"Example","type":"rss","url":"https://example.com/feed.xml","enabled":true}
```

Or an arXiv query:

```json
{"name":"arXiv AI","type":"arxiv","query":"cat:cs.AI","max_results":40,"enabled":true}
```

## API

- `GET /api/digest`
- `GET /api/stories?limit=100`
- `GET /api/status`
- `GET /api/profile`
- `POST /api/profile`
- `GET /api/sources`
- `POST /api/sources`
- `POST /api/refresh`
- `POST /api/feedback`
- `GET /api/bookmarks`
- `POST /api/bookmark`
- `POST /api/newsmarks/email`
- `GET /api/podcasts`

## Data and privacy

All profile, story and feedback data is local. Runtime data is stored in `data/twin.db` and ignored by git. Twin does not read browser history.

The default source list contains public RSS/Atom endpoints, arXiv API queries, and Google News RSS searches. Publication links always open at the original source. Respect each source's terms of use and do not use Twin to bypass paywalls.

## Architecture

```text
RSS / Atom / arXiv
       │
       ▼
   ingestion
       │
       ▼
 SQLite story store
       │
       ▼
 transparent ranking ← profile.json
       │
       ▼
 dedupe + category editor
       │
       ▼
 localhost service ← Chrome extension
       │
       ▼
 feedback → SQLite
```

## Roadmap

1. Semantic clustering with embeddings
2. Optional LLM analysis for “why it matters” and “watch next”
3. Learned weights from feedback
4. OPML import/export
5. Paper citation graph
6. Daily snapshot/history
7. Optional native host/desktop launcher so the service can start with Chrome

## Push an update

```bash
python scripts/build_extension.py
python -m unittest -v
git status
git add -A
git commit -m "Add TwinTimes Chrome extension"
git push origin main
```

Do not commit `.env` or `data/twin.db`; both are ignored because they can contain
credentials and personal reading history.

MIT licensed.
