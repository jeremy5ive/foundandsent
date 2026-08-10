#!/usr/bin/env python3
"""
Found & Sent — one-time (re-runnable) thumbnail backfill.
Walks images/ and generates a thumbnail for any file that doesn't already
have one in images/thumbs/. Safe to run more than once — already-thumbnailed
files are skipped, so this can also just be re-run after adding cards by hand.
"""

import os
from thumbs import make_thumbnail, THUMBS_SUBDIR

IMAGES_DIR = "images"


def main():
    thumbs_dir = os.path.join(IMAGES_DIR, THUMBS_SUBDIR)
    existing = set(os.listdir(thumbs_dir)) if os.path.isdir(thumbs_dir) else set()

    created = 0
    skipped = 0
    failed = []

    for fname in sorted(os.listdir(IMAGES_DIR)):
        full_path = os.path.join(IMAGES_DIR, fname)
        if not os.path.isfile(full_path):
            continue  # skips the thumbs/ subdirectory itself
        if fname in existing:
            skipped += 1
            continue
        try:
            result = make_thumbnail(IMAGES_DIR, fname)
        except Exception as e:
            failed.append((fname, str(e)))
            continue
        if result:
            created += 1
            print(f"Thumbnailed: {fname}")

    print(f"\nDone. {created} thumbnail(s) created, {skipped} already existed.")
    if failed:
        print(f"\n{len(failed)} file(s) failed (not valid images, or unreadable):")
        for fname, err in failed:
            print(f"  - {fname}: {err}")


if __name__ == "__main__":
    main()
