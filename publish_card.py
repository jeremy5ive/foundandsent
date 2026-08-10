#!/usr/bin/env python3
"""
Found & Sent — Daily Card Publisher
Pops the next card from queue.json and injects it into cards.json, index.html
(map pins only — card data now lives in cards.json), and feed.xml. Also
generates a grid thumbnail for the card's front/back images.
Run by GitHub Actions at 8am CST daily.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

from thumbs import make_thumbnail

QUEUE_FILE = "queue.json"
CARDS_FILE = "cards.json"
INDEX_FILE = "index.html"
FEED_FILE  = "feed.xml"
IMAGES_DIR = "images"
BASE_IMG   = "https://raw.githubusercontent.com/jeremy5ive/foundandsent/main/images/"
SITE_URL   = "https://foundandsent.net"

# ── Load queue ──────────────────────────────────────────────────────────────
with open(QUEUE_FILE, "r", encoding="utf-8") as f:
    queue = json.load(f)

if not queue:
    print("Queue is empty — nothing to publish today.")
    sys.exit(0)

card = queue[0]
print(f"Checking card #{card['id']}: {card['location']} ({card['year']})")

# ── Verify image files actually exist before publishing anything ────────────
missing = []
for key in ("front", "back"):
    fname = card.get(key)
    if not fname:
        missing.append(f"{key} (no filename set)")
        continue
    full_path = os.path.join(IMAGES_DIR, fname)
    if not os.path.isfile(full_path):
        missing.append(f"{key}: \"{fname}\"")

if missing:
    print(f"ERROR: Card #{card['id']} is missing image file(s) in {IMAGES_DIR}/:")
    for m in missing:
        print(f"  - {m}")
    print("Not publishing. Fix the filename(s) in queue.json (or add the missing "
          "file(s) to images/) so they match exactly, then re-run.")
    sys.exit(1)

queue.pop(0)
print(f"Publishing card #{card['id']}: {card['location']} ({card['year']})")

# ── Save updated queue ───────────────────────────────────────────────────────
with open(QUEUE_FILE, "w", encoding="utf-8") as f:
    json.dump(queue, f, indent=2, ensure_ascii=False)
print(f"Queue updated — {len(queue)} card(s) remaining.")

# ── Generate grid thumbnails for front/back ──────────────────────────────────
for key in ("front", "back"):
    thumb_rel = make_thumbnail(IMAGES_DIR, card[key])
    if thumb_rel is None:
        print(f"WARNING: could not generate thumbnail for {card[key]} — "
              f"grid will fall back to the full-size image for this card.")
    else:
        print(f"Thumbnail ready: {thumb_rel}")

# ── Append into cards.json ───────────────────────────────────────────────────
with open(CARDS_FILE, "r", encoding="utf-8") as f:
    cards = json.load(f)

new_card = {
    "id": card["id"],
    "location": card["location"],
    "address": card["address"],
    "year": card["year"],
    "sender": card["sender"],
    "recipient": card["recipient"],
    "notes": card["notes"],
    "front": BASE_IMG + card["front"],
    "back": BASE_IMG + card["back"],
}
if card.get("link"):
    new_card["link"] = card["link"]

cards.append(new_card)

with open(CARDS_FILE, "w", encoding="utf-8") as f:
    json.dump(cards, f, indent=2, ensure_ascii=False)
print(f"cards.json updated ✓ ({len(cards)} cards total)")

# ── Inject map entries into index.html ───────────────────────────────────────
# (Map pin data still lives inline in index.html — untouched by the cards.json
# migration. This logic is unchanged from before.)
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    html = f.read()

def esc(s):
    """Escape a string for use inside a JS double-quoted string."""
    return s.replace("\\", "\\\\").replace('"', '\\"')

map_entries = card.get("map", [])
if map_entries:
    MAP_MARKER = "\n];\n\nlet map="
    map_pos = html.rfind(MAP_MARKER)
    if map_pos != -1:
        map_js_parts = []
        for pin in map_entries:
            name = esc(pin["name"])
            lat  = pin["lat"]
            lng  = pin["lng"]
            map_js_parts.append(
                f'  {{name:"{name}",lat:{lat},lng:{lng},ids:[{card["id"]}]}}'
            )
        map_js = ",\n" + ",\n".join(map_js_parts)
        html = html[:map_pos] + map_js + html[map_pos:]
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(html)
        print("index.html map pins updated ✓")
    else:
        print("WARNING: Could not find map array marker in index.html — map pins not added.")
else:
    print("No map entries for this card — index.html left untouched.")

# ── Inject into feed.xml ─────────────────────────────────────────────────────
with open(FEED_FILE, "r", encoding="utf-8") as f:
    feed = f.read()

# Update lastBuildDate
cst = timezone(timedelta(hours=-6))
now_cst = datetime.now(cst)
rss_date = now_cst.strftime("%a, %d %b %Y %H:%M:%S %z")
feed = re.sub(
    r"<lastBuildDate>.*?</lastBuildDate>",
    f"<lastBuildDate>{rss_date}</lastBuildDate>",
    feed
)

# Build feed item
thumb_url = BASE_IMG + card["front"]
desc = card.get("feed_description", card["notes"][:300])
desc_escaped = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

new_item = f"""    <item>
      <title>Card #{card['id']}: {card['location']} ({card['year']})</title>
      <link>{SITE_URL}/#card-{card['id']}</link>
      <guid isPermaLink="true">{SITE_URL}/#card-{card['id']}</guid>
      <description>{desc_escaped}</description>
      <media:thumbnail url="{thumb_url}"/>
    </item>
"""

# Insert as newest item (top of list)
insert_feed_pos = feed.find("    <item>")
if insert_feed_pos == -1:
    print("ERROR: Could not find item insertion point in feed.xml")
    sys.exit(1)

feed = feed[:insert_feed_pos] + new_item + feed[insert_feed_pos:]

with open(FEED_FILE, "w", encoding="utf-8") as f:
    f.write(feed)
print("feed.xml updated ✓")

print(f"\nDone! Card #{card['id']} is now live.")
