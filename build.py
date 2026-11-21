#!/usr/bin/env python3
"""Builds the Showtime Suite website from site.json.

    python3 build.py

Writes index.html and <app>/index.html. Screenshots are picked up from
img/<app>-1.png, img/<app>-2.png, ... (in that order). Downloads are not
written into the pages: downloads.js reads the newest release of each app
from GitHub in the browser, so a new release needs no new build.
"""

import glob
import html
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
E = html.escape


def shots(app_id):
    files = sorted(
        glob.glob(os.path.join(ROOT, "img", f"{app_id}-[0-9]*.png")),
        key=lambda p: int(p.rsplit("-", 1)[1].split(".")[0]),
    )
    return [os.path.basename(f) for f in files]


def platforms(app):
    """The download rules for downloads.js, as a data attribute."""
    rules = {}
    for os_name in ("macos", "windows", "linux"):
        if app.get(os_name):
            rules[os_name] = app[os_name]
    return E(json.dumps(rules), quote=True)


def page(title, description, body, depth, color):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(description, quote=True)}">
<meta name="color-scheme" content="dark light">
<link rel="icon" href="{up}img/showtime-suite.png">
<link rel="stylesheet" href="{up}style.css">
</head>
<body style="--accent: {color}">
<header class="top"><div class="wrap">
  <a class="brand" href="{up}index.html"><img src="{up}img/showtime-suite.png" alt="">Showtime Suite</a>
  <nav>{"".join(f'<a href="{up}{a["id"]}/index.html">{E(a["name"])}</a>' for a in SITE["apps"])}</nav>
</div></header>
{body}
<footer><div class="wrap">
  <p>Showtime Suite – free tools for live shows. After a new version, the Windows and Linux files follow the Mac shortly.</p>
  <p>NDI® is a registered trademark of Vizrt NDI AB. All other names belong to their owners.</p>
</div></footer>
<script src="{up}downloads.js" defer></script>
</body>
</html>
"""


def downloads(app, primary=True):
    extra = ""
    if app.get("extra"):
        extra = (
            f' data-extra="{E(json.dumps(app["extra"]), quote=True)}"'
        )
    return (
        f'<div class="downloads" data-releases="{E(app["releases"])}" data-rules="{platforms(app)}"{extra}'
        f' data-primary="{"1" if primary else ""}">'
        f'<a class="btn main" href="https://github.com/{E(app["releases"])}/releases/latest">Download</a>'
        f'<span class="ver">newest version on GitHub</span></div>'
    )


def index():
    s = SITE["suite"]
    cards = []
    for a in SITE["apps"]:
        shot = shots(a["id"])
        pic = f'<img class="peek" src="img/{shot[-1]}" alt="" loading="lazy">' if shot else ""
        cards.append(
            f'<a class="card" href="{a["id"]}/index.html" style="--accent: {a["color"]}">'
            f'<div class="card-head"><img class="icon" src="img/{a["id"]}.png" alt=""><h3>{E(a["name"])}</h3></div>'
            f'<p>{E(a["tagline"])}</p>{pic}<span class="more">More about {E(a["name"])} ›</span></a>'
        )
    suite_shots = shots(s["id"])
    suite_pic = (
        f'<img class="hero-shot" src="img/{suite_shots[0]}" alt="Showtime Suite with its app cards">'
        if suite_shots
        else ""
    )
    feats = "".join(f"<li>{E(f)}</li>" for f in s["features"])
    body = f"""<main>
<section class="hero"><div class="wrap hero-grid">
  <div>
    <img class="hero-icon" src="img/showtime-suite.png" alt="">
    <h1>Showtime Suite</h1>
    <p class="lead">{E(s["tagline"])}</p>
    {downloads(s)}
    <p class="small">For macOS, Windows and Linux. Install Showtime Suite once; it installs and updates the other apps.</p>
  </div>
  {suite_pic}
</div></section>
<section class="wrap"><h2>The apps</h2><div class="cards">{"".join(cards)}</div></section>
<section class="wrap launcher"><h2>The launcher</h2><ul class="ticks">{feats}</ul></section>
</main>"""
    return page("Showtime Suite – tools for live shows", s["tagline"], body, 0, s["color"])


def app_page(a):
    shot = shots(a["id"])
    gallery = ""
    if shot:
        gallery = '<section class="wrap gallery">' + "".join(
            f'<figure><img src="../img/{f}" alt="{E(a["name"])} screenshot" loading="lazy"></figure>'
            for f in shot
        ) + "</section>"
    feats = "".join(
        f'<div class="feat"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for t, d in a["features"]
    )
    extra = ""
    if a.get("extra"):
        extra = f'<p class="small">{E(a.get("extra_note", ""))}</p>'
    systems = "macOS, Windows and Linux" if a.get("linux") else "macOS and Windows"
    body = f"""<main>
<section class="hero app"><div class="wrap">
  <div class="title"><img class="hero-icon" src="../img/{a["id"]}.png" alt=""><h1>{E(a["name"])}</h1></div>
  <p class="lead">{E(a["intro"])}</p>
  {downloads(a)}
  {extra}
  <p class="small">For {systems}. Easiest with <a href="../index.html">Showtime Suite</a>, which also keeps it up to date.</p>
</div></section>
{gallery}
<section class="wrap"><h2>What it does</h2><div class="feats">{feats}</div></section>
</main>"""
    return page(f"{a['name']} – Showtime Suite", a["tagline"], body, 1, a["color"])


def main():
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index())
    for a in SITE["apps"]:
        os.makedirs(os.path.join(ROOT, a["id"]), exist_ok=True)
        with open(os.path.join(ROOT, a["id"], "index.html"), "w", encoding="utf-8") as f:
            f.write(app_page(a))
    print("built", 1 + len(SITE["apps"]), "pages")


if __name__ == "__main__":
    main()
