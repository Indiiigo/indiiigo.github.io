"""Fetch publications from a Google Scholar profile into _data/publications.yml.

Usage: python scripts/fetch_scholar.py [SCHOLAR_USER_ID]

The Research page (_pages/research.md) renders from the generated YAML file.
Run locally or via the GitHub Action in .github/workflows/update-publications.yml.
"""

import sys
import time
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

USER_ID = sys.argv[1] if len(sys.argv) > 1 else "qXzr-p8AAAAJ"
BASE = "https://scholar.google.com"
OUT = Path(__file__).resolve().parent.parent / "_data" / "publications.yml"
PAGE_SIZE = 100
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_page(start):
    params = {
        "user": USER_ID,
        "hl": "en",
        "cstart": start,
        "pagesize": PAGE_SIZE,
        "sortby": "pubdate",
    }
    resp = requests.get(f"{BASE}/citations", params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    if "gsc_a_tr" not in resp.text and "gsc_a_e" not in resp.text:
        raise RuntimeError("Unexpected response from Google Scholar (possibly blocked by a captcha).")
    return BeautifulSoup(resp.text, "html.parser")


def parse_rows(soup):
    pubs = []
    for row in soup.select("tr.gsc_a_tr"):
        title_el = row.select_one("a.gsc_a_at")
        if title_el is None:
            continue
        gray = row.select("div.gs_gray")
        # The venue line repeats the year in a hidden span; drop it.
        for span in row.select("span.gs_oph"):
            span.decompose()
        year = row.select_one("span.gsc_a_h")
        cites = row.select_one("a.gsc_a_ac")
        year_text = year.get_text(strip=True) if year else ""
        cites_text = cites.get_text(strip=True) if cites else ""
        pubs.append({
            "title": title_el.get_text(strip=True),
            "url": BASE + title_el["href"].replace(f"&pagesize={PAGE_SIZE}&sortby=pubdate", ""),
            "authors": gray[0].get_text(strip=True) if len(gray) > 0 else "",
            "venue": gray[1].get_text(" ", strip=True) if len(gray) > 1 else "",
            "year": int(year_text) if year_text.isdigit() else None,
            "citations": int(cites_text) if cites_text.isdigit() else 0,
        })
    return pubs


def main():
    pubs, start = [], 0
    while True:
        rows = parse_rows(fetch_page(start))
        pubs.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        start += PAGE_SIZE
        time.sleep(2)

    if not pubs:
        sys.exit("No publications found; leaving existing data untouched.")

    pubs.sort(key=lambda p: (p["year"] or 0), reverse=True)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        yaml.safe_dump(pubs, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"Wrote {len(pubs)} publications to {OUT}")


if __name__ == "__main__":
    main()
