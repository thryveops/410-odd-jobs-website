#!/usr/bin/env python3
"""Update the Google review count everywhere it appears on the site.

The count lives in several places across three pages — including a meta
description and a JSON-LD aggregateRating, neither of which JavaScript could
reach. Rather than injecting it at runtime — which would hide the number from
crawlers on a site whose whole point is local SEO — the number stays hardcoded
in the HTML and this script keeps the copies in sync.

    python3 scripts/update-review-count.py 52
    python3 scripts/update-review-count.py 52 --dry-run

Run it from the repo root. See docs/WEEKLY-REVIEW-UPDATE.md.
"""

import argparse
import pathlib
import re
import sys

# Elements carrying data-review-count hold the number as their entire text,
# so one pattern covers every tagged occurrence on every page.
# The (?![-\w]) guard stops this from also matching data-review-count-rest,
# which holds a different number and is handled separately below.
TAGGED = re.compile(r'(<([a-z]+)[^>]*\bdata-review-count(?![-\w])[^>]*>)(\s*)(\d+)(\s*)(</\2>)')

# The ticker label says "...and N more", where N excludes the three reviews
# already featured above it. Derived here so the weekly update stays a
# single number.
FEATURED_ON_HOMEPAGE = 3
TAGGED_REST = re.compile(r'(<([a-z]+)[^>]*\bdata-review-count-rest\b[^>]*>)(\s*)(\d+)(\s*)(</\2>)')

# The meta description is prose and can't carry an attribute, so it gets an
# explicit pattern. If the wording is ever rewritten, update this too.
UNTAGGED = [
    (pathlib.Path("reviews.html"), re.compile(r'(Read )(\d+)( verified 5-star reviews)')),
    # The LocalBusiness aggregateRating in index.html. JSON-LD can't carry an
    # HTML attribute, so the schema count needs an explicit pattern the same
    # way the meta description does. verify-content.py cross-checks it against
    # the real card count, so a miss here fails the commit rather than
    # shipping a schema that contradicts the page.
    (pathlib.Path("index.html"), re.compile(r'("reviewCount":\s*)(\d+)(,)')),
]

FILES = ["index.html", "reviews.html", "quote/index.html"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("count", type=int, help="current total review count from Google")
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    args = ap.parse_args()

    if not pathlib.Path("index.html").exists():
        sys.exit("Run this from the repo root (where index.html lives).")

    new = str(args.count)
    total = 0

    for name in FILES:
        path = pathlib.Path(name)
        if not path.exists():
            print(f"  skip {name} (not found)")
            continue

        src = path.read_text()
        rest = str(max(0, args.count - FEATURED_ON_HOMEPAGE))

        # (old, new) per marker, so a marker that already holds the right
        # value is not reported as a change. The "rest" marker carries a
        # different number than the rest of them, hence the pairing.
        seen = []

        def tag_swap(target_value):
            def inner(m):
                seen.append((m.group(4), target_value))
                return f"{m.group(1)}{m.group(3)}{target_value}{m.group(5)}{m.group(6)}"
            return inner

        out = TAGGED.sub(tag_swap(new), src)
        out = TAGGED_REST.sub(tag_swap(rest), out)

        for target, pattern in UNTAGGED:
            if target == path:
                def swap_prose(m):
                    seen.append((m.group(2), new))
                    return f"{m.group(1)}{new}{m.group(3)}"
                out = pattern.sub(swap_prose, out)

        if not seen:
            print(f"  ---- {name}: no count markers found")
            continue

        changed = [(o, n) for o, n in seen if o != n]
        total += len(changed)
        verb = "would update" if args.dry_run else "updated"
        detail = (
            "  (" + ", ".join(sorted({f"{o}->{n}" for o, n in changed})) + ")"
            if changed else "  (already current)"
        )
        print(f"  {name}: {len(seen)} marker(s), {verb} {len(changed)}{detail}")

        if out != src and not args.dry_run:
            path.write_text(out)

    print(f"\n{'Would change' if args.dry_run else 'Changed'} {total} value(s).")
    if total and not args.dry_run:
        print("Review with `git diff`, then commit.")


if __name__ == "__main__":
    main()
