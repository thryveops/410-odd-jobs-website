#!/usr/bin/env python3
"""
Content integrity checks for the 410 Odd Jobs site.

Catches the mechanical class of error: duplicates, broken references,
counts that disagree with reality, platform labels that contradict the
badge they sit under.

It CANNOT verify that a photo shows the person its caption names. Only a
human opening the image can do that. See docs/CONTENT-CHECKLIST.md.

Usage:  python3 scripts/verify-content.py
Exit:   0 = clean, 1 = problems found
"""

import hashlib
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
REVIEWS = os.path.join(ROOT, "reviews.html")
QUOTE = os.path.join(ROOT, "quote", "index.html")
IMAGES = os.path.join(ROOT, "assets", "images")

PLATFORM_LOCATION = {
    "google": "Google Review",
    "facebook": "Facebook Recommendation",
}

failures = []
notes = []


def fail(msg):
    failures.append(msg)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def review_cards(html):
    """Every <div class="review-card"> with its platform, name and location."""
    cards = []
    for chunk in html.split('<div class="review-card">')[1:]:
        platform = re.search(r"review-platform platform-(\w+)", chunk)
        name = re.search(r'<p class="reviewer-name">([^<]*)</p>', chunk)
        location = re.search(r'<p class="reviewer-location">([^<]*)</p>', chunk)
        cards.append(
            {
                "platform": platform.group(1) if platform else None,
                "name": name.group(1).strip() if name else None,
                "location": location.group(1).strip() if location else None,
            }
        )
    return cards


def gallery_items(html, panel_id, stop_at):
    block = html.split(f'id="{panel_id}"')[1].split(stop_at)[0]
    imgs = re.findall(r'<img src="assets/images/([^"]+)"[^>]*alt="([^"]*)"', block)
    labels = re.findall(r'<div class="gallery-label">([^<]*)</div>', block)
    return imgs, labels


def check_reviews(index_html, reviews_html):
    cards = review_cards(reviews_html)
    total = len(cards)

    for card in cards:
        if not all((card["platform"], card["name"], card["location"])):
            fail(f"review card missing platform/name/location: {card}")

    # A card's location line must match the platform badge above it. This is
    # how two Nextdoor reviews once shipped wearing Facebook badges.
    for card in cards:
        expected = PLATFORM_LOCATION.get(card["platform"])
        if expected and card["location"] != expected:
            fail(
                f"{card['name']}: badge says {card['platform']} but location reads "
                f"{card['location']!r} (expected {expected!r})"
            )

    if re.search(r"Valleymede|Gray Rock Farm|[Nn]extdoor", reviews_html):
        fail("Nextdoor residue found in reviews.html")

    # Duplicate reviewers are allowed only on an explicit allowlist, because a
    # repeat customer is legitimate but an accidental copy-paste is not.
    allowed_repeats = {"Wade Kerns"}
    repeats = {n for n, c in Counter(c["name"] for c in cards).items() if c > 1}
    for name in sorted(repeats - allowed_repeats):
        fail(f"duplicate reviewer {name!r} not on the allowlist")
    for name in sorted(allowed_repeats & repeats):
        notes.append(f"{name} appears twice (allowlisted: two distinct reviews)")

    # Identical review text under different names means something was pasted twice.
    texts = re.findall(r'<p class="review-text">(.*?)</p>', reviews_html, re.S)
    for text, count in Counter(t.strip() for t in texts).items():
        if count > 1:
            fail(f"identical review text appears {count}x: {text[:60]!r}...")

    # Every stated count must equal the number of cards actually rendered.
    claims = [
        (REVIEWS, rf"Read {total} verified", "meta description"),
        (REVIEWS, rf"{total} verified reviews", "page subtitle"),
        (REVIEWS, rf"<strong>{total}</strong>", "count badge"),
        (INDEX, rf"See All {total} Reviews", "homepage CTA"),
        # The Google Ads landing page repeats the count in its trust bar, so it
        # drifts out of sync the same way the others do.
        (QUOTE, rf"data-review-count>{total}<", "ads landing page trust bar"),
    ]
    for path, pattern, where in claims:
        if not os.path.exists(path):
            continue
        if not re.search(pattern, read(path)):
            fail(f"{where}: does not state the real review count ({total})")

    stale = re.findall(r"\b(\d{2})\+? (?:verified )?[Rr]eviews\b", reviews_html)
    for n in set(stale):
        if int(n) != total:
            fail(f"reviews.html claims {n} reviews but {total} cards exist")

    platforms = Counter(c["platform"] for c in cards)
    notes.append(f"{total} reviews: " + ", ".join(f"{v} {k}" for k, v in platforms.items()))


def check_gallery(index_html):
    panels = [
        ("Team", "panel-team", 'id="panel-ba"'),
        ("Before & After", "panel-ba", "gallery-footer"),
    ]
    for title, panel_id, stop in panels:
        imgs, labels = gallery_items(index_html, panel_id, stop)
        files = [f for f, _ in imgs]
        alts = [a for _, a in imgs]

        if len(files) != 12:
            fail(f"{title} panel has {len(files)} items, expected 12")

        for kind, values in (("file", files), ("label", labels), ("alt text", alts)):
            for value, count in Counter(values).items():
                if count > 1:
                    fail(f"{title} panel: duplicate {kind} {value!r} ({count}x)")

        # Two different filenames holding identical bytes render as a visible
        # duplicate even though every string in the markup is unique.
        by_hash = defaultdict(list)
        for name in files:
            path = os.path.join(IMAGES, name)
            if os.path.exists(path):
                with open(path, "rb") as fh:
                    by_hash[hashlib.sha256(fh.read()).hexdigest()].append(name)
        for group in by_hash.values():
            if len(group) > 1:
                fail(f"{title} panel: identical image content in {group}")

        notes.append(f"{title} panel: {len(files)} items, all labels and alts unique")


def check_references(index_html, reviews_html):
    refs = set(re.findall(r"assets/images/[A-Za-z0-9._-]+", index_html + reviews_html))
    for ref in sorted(refs):
        if not os.path.exists(os.path.join(ROOT, ref)):
            fail(f"broken image reference: {ref}")


def exif_orientation(path):
    """Return the EXIF orientation value, or None if absent/unparseable."""
    with open(path, "rb") as fh:
        data = fh.read(131072)
    marker = data.find(b"Exif\x00\x00")
    if marker == -1:
        return None
    tiff = marker + 6
    if len(data) < tiff + 8:
        return None
    endian = "<" if data[tiff : tiff + 2] == b"II" else ">"
    import struct

    try:
        (ifd_off,) = struct.unpack(endian + "I", data[tiff + 4 : tiff + 8])
        ifd = tiff + ifd_off
        (count,) = struct.unpack(endian + "H", data[ifd : ifd + 2])
        for i in range(count):
            entry = ifd + 2 + i * 12
            (tag,) = struct.unpack(endian + "H", data[entry : entry + 2])
            if tag == 0x0112:
                (value,) = struct.unpack(endian + "H", data[entry + 8 : entry + 10])
                return value
    except (struct.error, IndexError):
        return None
    return None


def check_orientation(index_html):
    """A rotation flag makes an otherwise-correct photo render sideways in some
    contexts. Only images the site actually renders matter."""
    used = set(re.findall(r"assets/images/([A-Za-z0-9._-]+)", index_html))
    for name in sorted(used):
        if not name.lower().endswith((".jpg", ".jpeg")):
            continue
        path = os.path.join(IMAGES, name)
        if not os.path.exists(path):
            continue
        value = exif_orientation(path)
        if value not in (None, 1):
            fail(f"{name}: EXIF orientation={value} (will render rotated; bake it in)")


def main():
    index_html = read(INDEX)
    reviews_html = read(REVIEWS)

    check_reviews(index_html, reviews_html)
    check_gallery(index_html)
    check_references(index_html, reviews_html)
    check_orientation(index_html)

    for note in notes:
        print(f"  ok  {note}")

    if failures:
        print("\nCONTENT CHECK FAILED\n")
        for f in failures:
            print(f"  ✗ {f}")
        print(
            "\nA passing run does not mean captions name the right person. "
            "Open every image you touched."
        )
        return 1

    print("\nAll content checks passed.")
    print("Reminder: this cannot verify who is in a photo. Open every image you touched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
