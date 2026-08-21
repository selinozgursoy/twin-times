# Twin News

A local-first Chrome extension that builds a personalized morning intelligence dashboard for AI, science, neuroscience, startups, hardware, computer science, math and venture capital. Twin runs as a Manifest V3 Chrome extension and stores its working state in `chrome.storage.local`.

### Features

- Today: top 10 personalized headlines
- Expandable category briefing
- Go Deeper research / paper section
- Inside / Outside Your Bubble discovery view
- Newsmarks saved from Twin or any webpage
- Right-click → **★ Newsmark this page**
- Information Diet based only on Twin interactions
- Automatic background news refresh every 4 hours
- Toolbar popup with today's top stories
- Full-screen extension dashboard
- No LLM/API credits required
- No browsing-history permission

## Install locally

1. Download or clone this repository.
2. Open Chrome and visit `chrome://extensions`.
3. Turn on **Developer mode**.
4. Click **Load unpacked**.
5. Select this `twin-news-v0.3` folder.
6. Pin **Twin News** to the toolbar.
7. Click **Refresh news** on first launch if the initial background refresh has not completed yet.

The extension popup shows the top five stories. Click **Open morning briefing →** for the full dashboard.

## Newsmark

You can Newsmark in three ways:

- Click `☆` on a Today headline.
- Click `☆ Newsmark` on an expanded Twin story.
- On any normal webpage, right-click and choose **★ Newsmark this page**.

Newsmarks remain in Chrome local extension storage until removed or the extension's data is cleared.

## Information Diet

The Information Diet records interactions originating in Twin: story unfolds, article opens and Newsmark actions. It does **not** request Chrome browsing-history permission and does not attempt to record every site you visit.

## Built-in sources

The starter source registry includes TechCrunch, Nature, selected arXiv categories, and topic searches from Google News RSS. Source configuration lives in `data/sources.js`; personalization lives in `data/profile.js`.

## Permissions

- `storage`: local Twin state
- `alarms`: scheduled refresh
- `contextMenus`: right-click Newsmark
- `activeTab`: Newsmark the currently active page from the popup
- Host access is limited to the built-in feed hosts in `manifest.json`

## Open source

MIT licensed. To publish:

```bash
git init
git add .
git commit -m "Twin News v0.3 standalone Chrome extension"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/twin-news.git
git push -u origin main
```

## Architecture

```text
Chrome Extension
├── background.js      scheduled ingestion + context menu
├── lib/feeds.js       RSS / Atom parsing
├── lib/rank.js        deterministic personalization
├── lib/store.js       chrome.storage.local state
├── popup.*            toolbar briefing
└── dashboard.*        full morning intelligence UI
```

## Notes

This is intentionally RSS/API-first and zero-credit. Some publishers can change or restrict their feeds, so individual sources may occasionally fail while the rest continue refreshing. The dashboard reports the last successful refresh time.
