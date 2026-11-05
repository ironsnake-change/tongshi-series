---
name: tongshi-series
description: Build and maintain a research-first Chinese general-knowledge essay series with a backlog, editorial QA, EPUB/PDF artifacts, and optional scheduled delivery.
---

# Tongshi Series

Use this skill when the user wants to create, continue, or operate a recurring Chinese general-knowledge essay series. It is for a managed series with research files, editorial standards, queued publication, and durable artifacts. Do not use it for a one-off article, casual rewriting, or a generic content calendar.

## Operating rules

- Research before drafting. Save the source extracts in the article directory and mark unverified claims as uncertain.
- Keep writing and delivery separate. Drafting may fill the backlog; sending requires an explicit delivery step and must never be inferred from "write an article."
- Treat the article directory as the source of truth. A pending article has article.md and no .sent marker. Use meta.json for queue order.
- Preserve the user's topic, domain, language, and publication constraints. If they are absent, use the defaults in the editorial reference.
- Do not invent quotations, scenes, dates, numbers, or sources to make a story smoother.

## Workflow

1. Read [references/editorial-style.md](references/editorial-style.md) completely before drafting. Read [references/operations.md](references/operations.md) when setting up a backlog, queue, schedule, or delivery job.
2. Inspect the root with scripts/inventory.py. The default backlog target is 4 pending articles; when below target, draft at most 3 in one run. Prefer domains that have not appeared recently.
3. Choose an unused topic from assets/topics.example.json or the project's topics file. Avoid topics already present in index.md or article directories.
4. Create the article directory with scripts/new_article.py. This writes meta.json with an ISO queued_at value, so queue order does not depend on a folder name.
5. Run scripts/research.py for the chosen terms, then inspect research.md. If extraction is incomplete, retry with a better title or record the gap; do not silently replace it with memory.
6. Write article.md to the editorial reference. The default gate is 4000-4500 total CJK characters, at least 4000 body characters, 10-15 content sections, an opening paragraph under 120 characters, and a three-level certainty section.
7. Run scripts/validate_article.py. Fix every failure before building artifacts.
8. Build 文章.epub and 文章.pdf with the scripts below. Verify that both files exist and open.
9. Update index.md with the title, domain, character count, directory, artifact status, and sent/pending state. Keep the machine queue in meta.json aligned with the displayed backlog.
10. Stop after the requested batch. Do not send, mark .sent, or advance a scheduled slot unless the user explicitly asked for delivery.

## Commands

Run these from the series root. Paths are examples; keep the user's actual root.

    python scripts/new_article.py --root . --id enigma --domain "密码与情报" --title "恩尼格玛：机器与人的双重破绽"
    python scripts/research.py "Enigma machine" "恩尼格玛密码机" --out 2026-11-06-enigma/research.md
    python scripts/validate_article.py 2026-11-06-enigma/article.md
    python scripts/build_epub.py 2026-11-06-enigma/article.md 2026-11-06-enigma/文章.epub "恩尼格玛：机器与人的双重破绽" "Tongshi Series"
    python scripts/md_to_pdf.py 2026-11-06-enigma/article.md 2026-11-06-enigma/文章.pdf

Set CHROME_PATH when Chrome, Edge, or Chromium is not in a standard location. The PDF renderer uses only the local browser and does not upload the article.

## Defaults and boundaries

- Default language: Chinese; default article length: 4000-4500 CJK characters, target 4200.
- Eight-domain rotation: secret societies and esoteric traditions; codes and intelligence; body and death; technologies of violence; mind and cognition; belief and ritual; philosophy and evil; the unknown and frontiers.
- The validator checks structure and length, not historical truth. Source review remains the writer's responsibility.
- Do not commit credentials, email addresses, SMTP secrets, or private logs to a published skill. Delivery configuration belongs in the user's private environment; see the operations reference.
- If the user asks only to evaluate whether the workflow is ready, read [references/release-review.md](references/release-review.md), then report the quality gates, remaining operational gaps, and unverified assumptions before proposing publication.
