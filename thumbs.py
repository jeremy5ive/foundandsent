#!/usr/bin/env python3
"""
Found & Sent — shared thumbnail helper.
Used by both publish_card.py (new cards, run daily) and backfill_thumbnails.py
(one-time pass over the existing archive). Keeping this in one place means the
two callers can never drift out of sync on size/quality.
"""

from PIL import Image
import os

THUMB_MAX_WIDTH = 640   # px — plenty sharp for the grid, a fraction of the original's weight
THUMB_QUALITY = 78      # JPEG quality — good balance of size vs. visible quality
THUMBS_SUBDIR = "thumbs"


def make_thumbnail(images_dir, filename, thumbs_subdir=THUMBS_SUBDIR):
    """
    Generate a compressed thumbnail for `filename` (relative to images_dir),
    saved at images_dir/thumbs_subdir/filename (same filename, so the site's
    JS can derive the thumb URL with a simple path swap).

    Returns the thumbnail's path relative to images_dir (e.g. "thumbs/foo.jpeg"),
    or None if the source file doesn't exist.
    """
    src_path = os.path.join(images_dir, filename)
    if not os.path.isfile(src_path):
        return None

    thumbs_dir = os.path.join(images_dir, thumbs_subdir)
    os.makedirs(thumbs_dir, exist_ok=True)
    thumb_path = os.path.join(thumbs_dir, filename)

    with Image.open(src_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        if w > THUMB_MAX_WIDTH:
            new_h = round(h * (THUMB_MAX_WIDTH / w))
            img = img.resize((THUMB_MAX_WIDTH, new_h), Image.LANCZOS)
        img.save(thumb_path, "JPEG", quality=THUMB_QUALITY, optimize=True)

    return os.path.join(thumbs_subdir, filename)
