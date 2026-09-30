# Found & Sent — Claude Code guide

Found & Sent (foundandsent.net) is Jeremy's vintage postcard archive. Cards are scanned,
transcribed, researched, and queued; GitHub Actions publishes them automatically.
Repo: `jeremy5ive/foundandsent` (public, all rights reserved — custom LICENSE). Hosting: GitHub Pages + Cloudflare.

## How the pipeline works (read the code if in doubt — it wins over this file)
- `queue.json` — cards waiting to publish. `publish_card.py` pops `queue[0]`.
- `publish_card.py` verifies both image files exist in `images/`, then writes the card into
  `cards.json` (card data), injects map pins into `index.html` (map data still lives inline there),
  updates `feed.xml`, and makes thumbnails in `images/thumbs/` via `thumbs.py`.
- `.github/workflows/daily-publish.yml` runs the publisher on its cron schedule (check the file for
  the current cadence) and commits as "Found & Sent Bot". It also supports manual `workflow_dispatch`.
- A SessionStart hook in `.claude/settings.json` runs `git pull --ff-only` automatically when a
  session opens; if it printed a WARNING, sort that out before editing.
- The bot commits to `main` on its own, so **always `git pull` before editing** and never overwrite
  `index.html`, `cards.json`, or `feed.xml` with a stale copy — you'd erase published cards.

## Card schema (queue.json entries)
`id`, `location`, `address`, `year`, `sender`, `recipient`, `notes`, `front`, `back`,
`feed_description`, `map` (array of `{name, lat, lng}`), optional `link`.
- `notes`: front description, publisher/stamp/postmark details, historical context, then the
  verbatim message as `Message: "..."`. Never mix card notes into the message text.
- `id`s continue sequentially from the highest id in `cards.json` + `queue.json`.

## Weekly batch workflow
1. Jeremy scans 7 cards (front + back = 14 images) and saves them straight into `images/` in this
   local clone (no more GitHub web uploader — it was corrupting images).
2. Claude transcribes handwriting, translates non-English text (German comes up often),
   researches context, and writes the `queue.json` entries.
3. Validate, show Jeremy the new entries, then on his OK commit the new images + `queue.json`
   together and push.

## Transcription standards — the most important part of the project
- Try hard on handwritten messages; do multiple passes.
- Flag uncertain readings with `[?]`. Flag genuinely illegible text honestly — never invent it.
- Handwriting technique (Pillow): rotate to correct orientation, crop the message region, split into
  overlapping horizontal strips, upscale ~1.8–2× with `LANCZOS`, use quadrant crops for
  signatures/postmarks. Put scratch crops outside the repo (e.g. `/tmp`), never in `images/`.

## Filenames — strict
- Jeremy names his image files while scanning; **those names are final**. Match `front`/`back`
  in `queue.json` to his filenames exactly. Don't rename files or re-argue year/location wording
  he chose.
- Convention: natural spaced names with dashes, e.g. `1921 - Pana Township High School, ILL - front.jpeg`.
- Underscores in filenames are always a bug, never the convention.
- Verify every `front`/`back` exists: `ls "images/<name>"` locally (publish fails if missing).

## Validation before handing off
- Write JSON with `json.dump(..., indent=2, ensure_ascii=False)` so umlauts, em-dashes and curly
  quotes stay literal UTF-8.
- Re-load `queue.json` with Python to confirm it parses; check no duplicate ids vs `cards.json`.
- If `index.html` JS changes, extract the array and syntax-check it with `node`.
- Card presence check: `grep -o "id:N," index.html` (pipeline writes `id:182,` with no spaces).

## Git
- Commit only when Jeremy asks; **never push without explicit OK** (the settings prompt for it).
- Don't touch the workflow file or `publish_card.py` unless asked; for code changes, show the diff.

## Roadmap context (not active work unless raised)
- Future: move to Cloudflare D1 (two-tier summary/detail data, server-side search/pagination).
- Idea: 3D globe of sent-from → destination arcs (would need destination coords).
- Nonprofit formation + grants (NHPRC, IMLS Inspire, Texas history funders).
