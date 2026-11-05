# Operations reference

This reference covers the parts of the series that are not editorial: backlog control, queue order, artifact checks, optional scheduling, and failure recovery. Read it when bootstrapping a new series or when publication is being automated.

## Repository shape

A series root contains:

    YYYY-MM-DD-topic/
      meta.json
      research.md
      article.md
      文章.epub
      文章.pdf
      .sent                 only after confirmed delivery
    assets/
      topics.example.json
    index.md
    scripts/
    references/

meta.json is machine-readable queue state. index.md is the human-readable registry. A directory without article.md is not part of the catalog. A directory with article.md and no .sent marker is pending. Never infer pending status from a filename alone; scan the filesystem.

The recommended meta.json shape is:

    {
      "id": "topic-id",
      "domain": "密码与情报",
      "title": "文章标题",
      "created_at": "2026-11-06T10:00:00+08:00",
      "queued_at": "2026-11-06T10:00:00+08:00"
    }

queued_at is the delivery priority. Use scripts/new_article.py to create it. The inventory script falls back to file creation time only for older directories that predate meta.json.

## Backlog policy

The default target is four pending articles. When inventory is below four, write up to three, then stop. This prevents a single run from consuming an entire day's budget while still giving the delivery scheduler headroom.

Preferred order:

1. Domains not represented in the last seven published pieces.
2. Topics whose research pages are available and specific enough for a 4,000-character treatment.
3. Topics that have not appeared in index.md or any article directory.

Do not use volume as a substitute for evidence. A shorter, well-sourced article is safer than a padded one full of repeated conclusions.

## Writing-to-delivery handoff

Writing and delivery are separate operations:

1. Writing creates article.md and both artifacts. It must not create .sent.
2. A delivery job checks only pending directories, sorted by meta.json queued_at.
3. After the mail transport reports success, it writes .sent with a timestamp and records the result in the delivery log.
4. If sending fails, leave the article pending. A retry must reuse the same selected directory; do not skip ahead to a newer article.
5. Never send a fallback article when the intended queue is empty. Alert the operator instead.

The delivery job should hold a short-lived lock so overlapping scheduler ticks cannot send the same article twice. A lock older than the expected run window may be removed only after checking that no send process is still alive.

## Optional delivery setup

Delivery is environment-specific and is intentionally not bundled with credentials. A private implementation may provide:

- A launcher that runs an inventory query, selects the first pending article, and calls a mail or notification transport.
- Two named slots per day, for example 07:00 and 19:00, protected by a state record that marks each slot complete.
- A push notification when inventory is empty or a send fails.
- A manual dry-run mode that prints the selected directory and title without sending.

Keep SMTP passwords, OAuth tokens, webhook secrets, and recipient addresses outside the published repository. Read them from the operating system's credential store or an untracked environment file.

## Artifact checks

EPUB:

    python -c "import zipfile; z=zipfile.ZipFile('文章.epub'); print(z.testzip()); print(z.namelist())"

PDF:

    python -c "from pypdf import PdfReader; r=PdfReader('文章.pdf'); print(len(r.pages)); print(len((r.pages[0].extract_text() or '')))"

A file that exists but is zero bytes is not an artifact. Check size and at least one readable content block. If PDF rendering fails, verify CHROME_PATH before changing the article.

## Failure recovery

- Research fetch fails: retry once with a different language/title; record the failure in research.md rather than filling the gap from memory.
- Character count is short: add evidence, a concrete scene, or a mechanism explanation. Do not repeat the conclusion.
- One section is too long: split at a real change of scene or argument. Do not insert arbitrary headings.
- A validator failure is not a formatting nuisance. Fix the underlying mismatch before publishing.
- A delivery error is not permission to remove .sent or replay old content. Keep the article pending and alert the operator.
- A duplicate send means the .sent write and the transport result were not committed together. Stop the scheduler and reconcile the log before resuming.

## Publishing a reusable copy

When publishing this reference implementation:

- Remove local roots, email addresses, push topics, account identifiers, and SMTP stores.
- Keep the editorial reference and generic scripts.
- Add a license and a README that states the tested platform and known limits.
- Tag a release only after running the validator and artifact checks on a clean example.
- Never publish a sample article's private research traffic or a real subscriber list.
