#!/usr/bin/env python3
"""Render an article Markdown file to PDF through a local Chromium browser."""

from __future__ import annotations

import argparse
import base64
import html
import os
import sys
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

def _configure_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

_configure_stdout()



IMG_RE = re.compile(r"^!\[(.*?)\]\((.+?)\)\s*$")
CSS = """
body { font-family: "Microsoft YaHei", "Noto Sans CJK SC", "SimSun", sans-serif; line-height: 1.85; margin: 0 auto; max-width: 760px; padding: 40px 24px; color: #222; }
h1 { font-size: 26px; line-height: 1.4; margin: 0 0 28px; }
h2 { font-size: 19px; margin: 34px 0 12px; padding-bottom: 6px; border-bottom: 1px solid #ddd; }
p { text-indent: 2em; margin: 12px 0; text-align: justify; }
li { margin: 6px 0; }
ul { padding-left: 1.6em; }
figure { margin: 26px 0; text-align: center; page-break-inside: avoid; }
img { max-width: 100%; }
figcaption { font-size: 13px; color: #555; margin-top: 8px; text-indent: 0; }
"""


def inline(text: str) -> str:
    output = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", output)


def convert(md_path: Path) -> str:
    markdown = md_path.read_text(encoding="utf-8-sig")
    output = []
    in_list = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if in_list:
                output.append("</ul>")
                in_list = False
            continue
        image = IMG_RE.match(line)
        if image:
            if in_list:
                output.append("</ul>")
                in_list = False
            caption, path_text = image.group(1).strip(), image.group(2).strip()
            source = Path(path_text)
            if not source.is_absolute():
                source = md_path.parent / source
            data = ""
            if source.exists():
                mime = source.suffix.lower().lstrip(".") or "png"
                data = "data:image/%s;base64,%s" % (
                    mime,
                    base64.b64encode(source.read_bytes()).decode("ascii"),
                )
            output.append('<figure><img src="%s" alt="%s"/>' % (data, html.escape(caption)))
            if caption:
                output.append("<figcaption>%s</figcaption>" % html.escape(caption))
            output.append("</figure>")
            continue
        if line.startswith("# "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append("<h1>%s</h1>" % html.escape(line[2:].strip()))
        elif line.startswith("## "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append("<h2>%s</h2>" % html.escape(line[3:].strip()))
        elif line.startswith("- "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append("<li>%s</li>" % inline(line[2:].strip()))
        else:
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append("<p>%s</p>" % inline(line))
    if in_list:
        output.append("</ul>")
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (
        CSS,
        "\n".join(output),
    )


def find_browser() -> str:
    configured = os.environ.get("CHROME_PATH")
    if configured and Path(configured).exists():
        return configured
    candidates = [
        Path(r"C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path(r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path(r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path(r"C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    for name in ("google-chrome", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("No Chromium browser found. Set CHROME_PATH to Chrome, Edge, or Chromium.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Markdown article to PDF.")
    parser.add_argument("article")
    parser.add_argument("pdf")
    args = parser.parse_args()

    article = Path(args.article).resolve()
    pdf = Path(args.pdf).resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    html_doc = convert(article)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as handle:
        handle.write(html_doc)
        temp_html = Path(handle.name)
    try:
        subprocess.run(
            [
                find_browser(),
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                "--print-to-pdf=" + str(pdf),
                temp_html.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        temp_html.unlink(missing_ok=True)
    print(f"pdf: {pdf} ({pdf.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
