# Content checklist

Run before committing any change to images or reviews.

`scripts/verify-content.py` runs automatically on commit and catches
duplicates, broken references, wrong counts, and platform badges that
contradict their location line.

**It cannot tell you who is in a photograph.** Everything below is the part
a machine cannot check.

## Why this file exists

Every wrong caption on this site came from the same mistake: a filename was
treated as evidence. A photo named `team-ahmad-mattress.jpeg` was captioned
"Ahmad removing a mattress." Nobody opened it. It is not Ahmad.

Filenames are a guess someone made once. They are not evidence.

## Before captioning any image

1. **Open the image and look at it.** Not the filename, not the old caption,
   not what the client said it was. The pixels.
2. **Count the people.** "Crew" and "team" mean two or more. Three photos on
   this site said "crew" and showed one person.
3. **Name someone only if you can verify it.** Compare against
   `assets/images/ahmad-alamad-headshot.jpeg`. If you are not certain, write
   "410 Odd Jobs team member." A generic caption is never wrong; a wrong name
   is a false statement about a person.
4. **Check a before-and-after really is one.** Both panels must show the same
   room or space. `warehouse-cleanout-ba.jpg` paired a basement with a garage
   and sat in the gallery for months labeled "Basement Cleanout."
5. **Open the compressed output, not just the source.** Converting HEIC to
   JPEG can drop or double-apply the EXIF rotation flag. An image can be
   correct in Finder and sideways on the site.

## Before adding or editing a review

1. **Work from the source.** A screenshot of the Google Business Profile or
   the Facebook page. Not memory, not the existing HTML.
2. **Quote verbatim.** Including the reviewer's typos. Do not silently correct
   them.
3. **The location line must match the platform badge.** A Nextdoor review is
   not a Facebook recommendation. Two of them shipped that way.
4. **A repeat reviewer is allowed, a duplicated review is not.** Wade Kerns
   wrote two genuinely different recommendations. If a name repeats, confirm
   the text differs and add the name to `allowed_repeats` in the checker.
5. **Update every count.** There are four: the meta description, the page
   subtitle, the count badge, and the homepage CTA. The checker enforces this.

## Counting

Never count reviews with a loose grep. Count `<div class="review-card">`
elements and cross-check against `<p class="reviewer-name">` tags. They must
agree. `scripts/verify-content.py` does this correctly — use it.

## Setup

The pre-commit hook lives in `.githooks/` so it survives a clone:

```sh
git config core.hooksPath .githooks
```

Run the checks manually any time:

```sh
python3 scripts/verify-content.py
```
