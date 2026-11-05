#!/usr/bin/env python3
"""Fetch Wikipedia extracts for research-first essay drafting."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "TongshiSeries/0.1 (research helper)"
DEFAULT_LIMIT = 12000

def _configure_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

_configure_stdout()




def make_opener(proxy: str | None):
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    opener = urllib.request.build_opener(*handlers)
    opener.addheaders = [("User-Agent", USER_AGENT)]
    return opener


def fetch(opener, lang: str, term: str, limit: int):
    url = (
        f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts"
        "&explaintext=1&format=json&redirects=1&titles="
        + urllib.parse.quote(term)
    )
    with opener.open(url, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    for page in data.get("query", {}).get("pages", {}).values():
        text = page.get("extract", "") or ""
        if text:
            title = page.get("title", term)
            page_url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            return title, page_url, text[:limit]
    return None, None, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Wikipedia text for citations and fact checking.")
    parser.add_argument("terms", nargs="+", help="Article titles or search terms")
    parser.add_argument("--out", required=True, help="Output research.md path")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Characters per language extract")
    parser.add_argument("--langs", default="zh,en", help="Comma-separated Wikipedia languages")
    parser.add_argument("--proxy", default=os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY"))
    args = parser.parse_args()

    opener = make_opener(args.proxy)
    chunks = []
    for term in args.terms:
        for lang in [item.strip() for item in args.langs.split(",") if item.strip()]:
            try:
                title, page_url, text = fetch(opener, lang, term, args.limit)
            except Exception as exc:
                chunks.append(f"## {term} ({lang})\n\n[fetch failed: {type(exc).__name__}: {exc}]")
                continue
            if text:
                chunks.append(f"## {title} ({lang})\nSource: {page_url}\n\n{text}\n")
            else:
                chunks.append(f"## {term} ({lang})\n\n[no extract returned]")

    header = (
        "# Research dossier\n\n"
        "The extracts below are working sources from Wikipedia. Treat claims not covered here "
        "as unverified; use a primary source before presenting them as fact.\n\n"
    )
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(header + "\n\n".join(chunks), encoding="utf-8")
    print(f"research saved: {output} ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
