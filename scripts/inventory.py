#!/usr/bin/env python3
"""List pending and sent Tongshi Series articles in queue order."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
import sys
from pathlib import Path

def _configure_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

_configure_stdout()

CJK = re.compile(r"[\u4e00-\u9fff]")
SKIP = {"_tools", "_dist", "_research", "_scratch"}


def first_title(article: Path) -> str:
    for line in article.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return article.parent.name


def queued_at(directory: Path, article: Path) -> str:
    meta = directory / "meta.json"
    if meta.exists():
        try:
            value = json.loads(meta.read_text(encoding="utf-8"))["queued_at"]
            return str(value)
        except (KeyError, ValueError, OSError, TypeError):
            pass
    stamp = article.stat().st_ctime
    return datetime.fromtimestamp(stamp, timezone.utc).isoformat()


def collect(root: Path):
    rows = []
    for directory in sorted(root.iterdir()):
        if not directory.is_dir() or directory.name in SKIP or directory.name.startswith("."):
            continue
        article = directory / "article.md"
        if not article.exists():
            continue
        text = article.read_text(encoding="utf-8-sig")
        rows.append(
            {
                "directory": directory.name,
                "title": first_title(article),
                "chars": len(CJK.findall(text)),
                "status": "sent" if (directory / ".sent").exists() else "pending",
                "queued_at": queued_at(directory, article),
                "research": (directory / "research.md").exists(),
                "epub": (directory / "文章.epub").exists(),
                "pdf": (directory / "文章.pdf").exists(),
            }
        )
    return sorted(rows, key=lambda row: (row["queued_at"], row["directory"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the Tongshi Series backlog.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--pending-only", action="store_true")
    args = parser.parse_args()

    rows = collect(Path(args.root).resolve())
    if args.pending_only:
        rows = [row for row in rows if row["status"] == "pending"]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    pending = sum(row["status"] == "pending" for row in rows)
    print(f"pending={pending} total={len(rows)}")
    for row in rows:
        print(
            f"{row['status']:7} {row['queued_at']} {row['chars']:4} "
            f"{row['directory']} | {row['title']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
