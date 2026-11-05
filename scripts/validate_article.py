#!/usr/bin/env python3
"""Validate a Tongshi Series article against the editorial delivery gates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

def _configure_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

_configure_stdout()

CJK = re.compile(r"[\u4e00-\u9fff]")
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TITLE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
TAIL_NAMES = ("术语表", "延伸阅读")


def cjk_count(text: str) -> int:
    return len(CJK.findall(text))


def section_spans(text: str):
    matches = list(HEADING.finditer(text))
    spans = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end]
        spans.append({"name": match.group(1).strip(), "body": body, "chars": cjk_count(body)})
    return spans


def first_paragraph(body: str) -> str:
    for block in re.split(r"\n\s*\n", body.strip()):
        block = block.strip()
        if block and not block.startswith("#"):
            return block
    return ""


def validate(path: Path, args) -> dict:
    problems = []
    warnings = []
    text = path.read_text(encoding="utf-8-sig")
    title_match = TITLE.search(text)
    if not title_match:
        problems.append("missing top-level '# title' heading")

    total = cjk_count(text)
    if not (args.min_chars <= total <= args.max_chars):
        problems.append(f"total CJK characters {total} outside {args.min_chars}-{args.max_chars}")

    spans = section_spans(text)
    tail = [item for item in spans if item["name"] in TAIL_NAMES]
    content = [item for item in spans if item["name"] not in TAIL_NAMES]
    tail_chars = sum(item["chars"] for item in tail)
    body_chars = total - tail_chars

    if body_chars < args.min_body:
        problems.append(f"body CJK characters {body_chars} below {args.min_body}")
    if tail_chars > args.max_tail:
        problems.append(f"glossary/reading CJK characters {tail_chars} above {args.max_tail}")
    if not (args.min_sections <= len(content) <= args.max_sections):
        problems.append(f"content section count {len(content)} outside {args.min_sections}-{args.max_sections}")

    if not any(item["name"] == "术语表" for item in tail):
        problems.append("missing '## 术语表' section")
    if not any(item["name"] == "延伸阅读" for item in tail):
        problems.append("missing '## 延伸阅读' section")

    for index, item in enumerate(content, start=1):
        if not (args.min_section_chars <= item["chars"] <= args.max_section_chars):
            problems.append(
                f"section {index} '{item['name']}' has {item['chars']} CJK characters; "
                f"expected {args.min_section_chars}-{args.max_section_chars}"
            )

    if content:
        opening = first_paragraph(content[0]["body"])
        opening_chars = cjk_count(opening)
        if opening_chars > args.max_opening:
            problems.append(f"opening paragraph has {opening_chars} CJK characters; max {args.max_opening}")

    certainty = next((item for item in content if "确定性说明" in item["name"]), None)
    if not certainty:
        problems.append("missing a section whose heading contains '确定性说明'")
    else:
        body = certainty["body"]
        for label in ("可以确认", "有共识", "属于推测"):
            if label not in body:
                problems.append(f"certainty section missing label: {label}")

    if re.search(r"\bTODO\b|待补|占位|PLACEHOLDER", text, re.IGNORECASE):
        problems.append("placeholder text found")

    research = path.parent / "research.md"
    if not research.exists() and not args.allow_missing_research:
        problems.append("research.md is missing; run the research step or pass --allow-missing-research")

    return {
        "ok": not problems,
        "path": str(path),
        "title": title_match.group(1) if title_match else None,
        "total_cjk": total,
        "body_cjk": body_chars,
        "tail_cjk": tail_chars,
        "content_sections": len(content),
        "section_sizes": [item["chars"] for item in content],
        "target": args.target,
        "problems": problems,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Tongshi Series article.")
    parser.add_argument("article", nargs="?", default="article.md")
    parser.add_argument("--min-chars", type=int, default=4000)
    parser.add_argument("--max-chars", type=int, default=4500)
    parser.add_argument("--min-body", type=int, default=4000)
    parser.add_argument("--target", type=int, default=4200)
    parser.add_argument("--max-tail", type=int, default=300)
    parser.add_argument("--min-sections", type=int, default=10)
    parser.add_argument("--max-sections", type=int, default=15)
    parser.add_argument("--min-section-chars", type=int, default=170)
    parser.add_argument("--max-section-chars", type=int, default=450)
    parser.add_argument("--max-opening", type=int, default=120)
    parser.add_argument("--allow-missing-research", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.article)
    if not path.exists():
        print(f"article not found: {path}", file=sys.stderr)
        return 2
    result = validate(path, args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"{status}: {result['path']}")
        print(
            f"total={result['total_cjk']} body={result['body_cjk']} "
            f"tail={result['tail_cjk']} sections={result['content_sections']}"
        )
        for problem in result["problems"]:
            print(f"- {problem}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
