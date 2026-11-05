# Release review and maturity record

Release: 0.1.0
Date: 2026-11-05
Decision: publish as public beta

## Scope

This package extracts the operating logic of a working Chinese general-knowledge essay pipeline: research capture, editorial rules, article scaffolding, quality checks, EPUB and PDF builds, machine-readable queue metadata, and a reference for separating writing from delivery.

## Evidence used for this release

- Three production articles passed validate_article.py after the gate was introduced.
- The article counts were 4219, 4141, and 4131 CJK characters, with body counts above 4000 and 14-15 content sections.
- The official skill-creator quick_validate.py reported: "Skill is valid!"
- All Python scripts compiled successfully.
- The scaffold created a date-topic directory and meta.json with queued_at.
- inventory.py found the four pending production articles in the intended order.
- build_epub.py produced a readable EPUB, and md_to_pdf.py produced a two-page PDF from the scaffold article.
- The package was scanned for personal email addresses, push topics, absolute user paths, and credentials. Only policy text mentions those words.

## Maturity matrix

| Area | Status | Assessment |
|---|---|---|
| Editorial process | Strong | Clear length, structure, source hierarchy, and certainty section. |
| Research capture | Usable | Deterministic Wikipedia extraction with failure records; not a complete fact-checking system. |
| Queue state | Improved | meta.json queued_at removes dependence on folder-name order. Older directories need backfill. |
| Artifact builds | Tested | EPUB is pure Python; PDF uses a local Chromium browser. |
| Quality gate | Tested | Structural validation catches length, section, opening, and certainty failures. |
| Delivery | Reference only | The public package intentionally excludes credentials and the private mail transport. |
| Portability | Good | Python standard library only; Chrome/Edge/Chromium is the external PDF dependency. |
| Automated CI | Missing | The scripts are tested manually in this release. CI can be added later. |
| Duplicate topic detection | Partial | Avoidance is an editorial step; no semantic similarity detector yet. |

## Known limitations

1. Wikipedia is a starting source, not a final authority. A writer must check primary material for contested claims.
2. The validator checks form, not truth. A structurally valid article can still contain a historical error.
3. The public repository does not include SMTP, API keys, push credentials, or a scheduler. Those belong to the operator's private environment.
4. The Windows scheduled-delivery design is documented as a pattern, not shipped as turnkey code.
5. Older article directories may not have meta.json; the inventory fallback is creation time and should be backfilled over time.
6. Google model routing was not accepted as a release dependency because the configured Google route was unhealthy during this audit.
7. No independent human editor has signed off on the public wording of every example.

## Security and privacy review

- No email address, account id, SMTP secret, ntfy topic, or private root path is included.
- research.py uses an optional proxy from an environment variable and does not persist credentials.
- md_to_pdf.py sends the article only to a local browser process.
- The repository should be treated as a workflow template; operators must configure their own credentials outside version control.

## Release position

This is not a claim that a model can independently produce publishable history. It is a claim that a careful operator can use the package to make research, writing, checking, packaging, and queue handoff repeatable.

Public beta is appropriate. Promote the workflow and its boundaries together. Move to 1.0 only after:

1. At least three external users complete a full series cycle.
2. A clean install works on Windows, macOS, and Linux.
3. A duplicate-topic check and an automated artifact test are in place.
4. The delivery reference has a tested, credential-free dry-run example.
