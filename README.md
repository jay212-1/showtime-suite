# Showtime Suite website

The website of the Showtime Suite (GitHub Pages, served from `main`).

- `site.json` – the apps: name, colour, tagline, features and the rules for their release files
  (the same as in the launcher's `apps.json`).
- `python3 build.py` – writes `index.html` and `<app>/index.html`. Commit the result.
- `img/<app>.png` – icons; `img/<app>-1.png`, `-2.png`, … – screenshots (demo data), shown in that order.
- `downloads.js` – the download buttons read the newest release of each app from GitHub in the
  browser, so a new release needs no change here.

Preview: `python3 -m http.server --directory .` and open http://localhost:8000.
