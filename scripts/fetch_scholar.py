"""Fetch publications from a Google Scholar profile into _data/publications.yml.

Usage: python scripts/fetch_scholar.py [SCHOLAR_USER_ID] [--reprocess]

--reprocess skips scraping and only re-applies venue cleanup and
scripts/publication_overrides.yml to the existing data file.

The Research page (_pages/research.md) renders from the generated YAML file.
Run locally or via the GitHub Action in .github/workflows/update-publications.yml.
"""

import random
import re
import sys
import time
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
USER_ID = ARGS[0] if ARGS else "qXzr-p8AAAAJ"
BASE = "https://scholar.google.com"
OUT = Path(__file__).resolve().parent.parent / "_data" / "publications.yml"
PAGE_SIZE = 100
VENUE_FIELDS = ("Journal", "Conference", "Book", "Source", "Publisher")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)


def get_soup(url, params=None):
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    if "gs_captcha" in resp.text or "unusual traffic" in resp.text:
        raise RuntimeError("Blocked by Google Scholar captcha.")
    return BeautifulSoup(resp.text, "html.parser")


def list_papers():
    """Return (detail_url, year) for every paper on the profile."""
    papers, start = [], 0
    while True:
        soup = get_soup(f"{BASE}/citations", {
            "user": USER_ID, "hl": "en", "cstart": start,
            "pagesize": PAGE_SIZE, "sortby": "pubdate",
        })
        rows = soup.select("tr.gsc_a_tr")
        for row in rows:
            link = row.select_one("a.gsc_a_at")
            year = row.select_one("span.gsc_a_h")
            if link is None:
                continue
            href = link["href"].replace(f"&pagesize={PAGE_SIZE}&sortby=pubdate", "")
            year_text = year.get_text(strip=True) if year else ""
            papers.append((BASE + href, int(year_text) if year_text.isdigit() else None))
        if len(rows) < PAGE_SIZE:
            return papers
        start += PAGE_SIZE
        time.sleep(2)


# (pattern, display name): first match wins, so put more specific patterns first.
VENUE_NAMES = [
    (r"arXiv", "arXiv preprint"),
    (r"Findings of the Association for Computational Linguistics: (\w+)", r"Findings of \1"),
    (r"EMNLP \(Findings\)", "Findings of EMNLP"),
    (r"ACL \d{4}, Student Research Workshop", "ACL Student Research Workshop"),
    (r"Annual Meeting of the Association for Computational Linguistics|^ACL$", "ACL"),
    (r"Empirical Methods in Natural Language Processing|^EMNLP$", "EMNLP"),
    (r"North American Chapter of the Association for Computational Linguistics", "NAACL"),
    (r"European Chapter of the Association for Computational Linguistics", "EACL"),
    (r"AAAI Conference on Web and Social Media", "ICWSM"),
    (r"Fairness, Accountability, and Transparency", "ACM FAccT"),
    (r"Computer Supported Cooperative Work", "CSCW Companion"),
    (r"ACM on Human-Computer Interaction", "Proceedings of the ACM on Human-Computer Interaction (CSCW)"),
    (r"Symposium on Human-Computer Interaction for Work", "CHIWORK"),
    (r"Advances in Social Networks Analysis and Mining", "ASONAM"),
    (r"ACM conference on web science", "ACM Web Science"),
    (r"IEEE International Conference on Cognitive Computing", "IEEE ICCC"),
    (r"workshop on natural language processing for social media", "SocialNLP Workshop"),
    (r"Workshop on Online Abuse and Harms", "WOAH Workshop"),
    (r"HCI\+NLP Workshop", "HCI+NLP Workshop (non-archival)"),
    (r"Handbook of Computational Social Science", "Handbook of Computational Social Science"),
    (r"GESIS.*Data File", "GESIS Data Archive"),
    (r"^npj (.*)", r"npj \1"),
]


def clean_venue(venue):
    venue = re.sub(r"\s+", " ", venue).strip()
    for pattern, name in VENUE_NAMES:
        match = re.search(pattern, venue, re.I)
        if match:
            return match.expand(name)
    venue = re.sub(r"^(In )?Proceedings of (the )?", "", venue)
    venue = re.sub(r"\s*\(pp\.[^)]*\)\.?", "", venue)
    venue = re.sub(r",?\s*\d{4}$", "", venue)
    return venue[:1].upper() + venue[1:]


def load_overrides():
    path = Path(__file__).resolve().parent / "publication_overrides.yml"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def apply_overrides(pub, overrides):
    for override in overrides:
        if override["match"].lower() in pub["title"].lower():
            pub.update({k: v for k, v in override.items() if k != "match"})
    return pub


def fetch_paper(url, year):
    soup = get_soup(url)
    title_link = soup.select_one("#gsc_oci_title a.gsc_oci_title_link")
    title_el = title_link or soup.select_one("#gsc_oci_title")
    pdf_el = soup.select_one("#gsc_oci_title_gg a")
    fields = {}
    for row in soup.select("#gsc_oci_table .gs_scl"):
        name, value = row.select_one(".gsc_oci_field"), row.select_one(".gsc_oci_value")
        if name and value:
            fields[name.get_text(strip=True)] = value.get_text(" ", strip=True)

    venue = next((fields[f] for f in VENUE_FIELDS if f in fields), "")
    link = title_link["href"] if title_link else None
    pdf = pdf_el["href"] if pdf_el else None
    if link and "scholar.google" in link:
        link = None
    return {
        "title": title_el.get_text(strip=True),
        "authors": fields.get("Authors", ""),
        "venue": clean_venue(venue),
        "year": year,
        "url": link or pdf,
        "pdf": pdf if pdf and pdf != link else None,
    }


def reprocess(overrides):
    """Re-apply venue cleanup and overrides to the existing data without scraping."""
    with OUT.open(encoding="utf-8") as f:
        pubs = yaml.safe_load(f)
    for pub in pubs:
        pub.pop("citations", None)
        pub["venue"] = clean_venue(pub.get("venue") or "")
        if pub.get("url") and "scholar.google" in pub["url"]:
            pub["url"] = None
        pub.setdefault("pdf", None)
        apply_overrides(pub, overrides)
    return pubs


def main():
    overrides = load_overrides()
    if "--reprocess" in sys.argv:
        pubs = reprocess(overrides)
    else:
        papers = list_papers()
        if not papers:
            sys.exit("No publications found; leaving existing data untouched.")
        pubs = []
        for i, (url, year) in enumerate(papers, 1):
            pubs.append(apply_overrides(fetch_paper(url, year), overrides))
            print(f"[{i}/{len(papers)}] {pubs[-1]['title']}")
            time.sleep(random.uniform(2, 4))

    pubs = [p for p in pubs if not p.pop("hide", False)]
    pubs.sort(key=lambda p: (p["year"] or 0), reverse=True)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        yaml.safe_dump(pubs, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"Wrote {len(pubs)} publications to {OUT}")


if __name__ == "__main__":
    main()
