# Weekly Review Update — 410 Odd Jobs

Takes about five minutes. Everything here is public data, so you never need
Ahmad's login or a Google Cloud account.

## 1. Open the review list, sorted by newest

https://search.google.com/local/reviews?placeid=ChIJBfkPVNXE6AURgcKLg98SKTw

Set the sort control to **Newest**. Note two things:

- The **total review count**
- The **top three reviews** — text, reviewer name, and the relative date
  Google shows ("2 weeks ago")

## 2. Update the count

From the repo root:

```bash
python3 scripts/update-review-count.py 52
```

That updates all seven places the number appears across `index.html`,
`reviews.html`, and `quote/index.html` — including a meta description that
nothing else would catch. Use `--dry-run` first if you want to see what it
would touch.

The homepage ticker label ("…and 47 more") is derived automatically as
total minus the three featured. You don't set it separately.

## 3. Swap the three featured reviews

In `index.html`, find:

```
<!-- ══ WEEKLY UPDATE — FEATURED REVIEWS ══ -->
```

Three `.review-card` blocks follow, ending at
`<!-- ═══ END WEEKLY UPDATE — FEATURED REVIEWS ═══ -->`. For each card, replace:

| Field | Where |
|---|---|
| Review text | inside `<p class="review-text">` |
| Reviewer name | `<p class="reviewer-name">` |
| Relative date | `<p class="reviewer-date">` — copy Google's wording verbatim |
| Avatar letter | `<div class="reviewer-avatar">` — first initial |

**Short reviews:** if one is under roughly 15 words, change its class to
`class="review-text is-short"`. That switches the card to display type so it
reads as punchy rather than half empty. Remove `is-short` when a long review
takes that slot again.

**Never invent a date.** Copy exactly what Google shows. If the wording isn't
available, leave the previous date out rather than guessing — a wrong date is
a false claim to a customer.

## 4. Check it

```bash
python3 scripts/verify-content.py
```

Then open the homepage and confirm the reviews section: trust bar reads
`5.0` and the new count, three cards show the new reviews, the ticker scrolls
and pauses when you hover it.

## 5. Commit

```bash
git add -A && git commit -m "Update reviews: 3 newest featured, count now 52" && git push
```

GitHub Pages redeploys automatically. Give it a minute, then check
410oddjobs.com.

---

## Things that are easy to get wrong

**The rating is 5.0, not 4.9.** Every review on the listing is five stars. If
that ever changes, the `5.0` in the trust bar is hardcoded in `index.html` —
search for `class="num"`.

**`reviews.html` is a curated archive, not a live mirror.** It currently holds
46 review cards while Google reports more. The homepage trust bar quotes
Google's real number, which is correct, but "See All 52 Reviews" pointing at a
page with 46 is a discrepancy worth closing when you have time — paste the
missing ones into `reviews.html` following the existing card markup.

**The ticker quotes rarely need touching.** They're short verbatim reviews in
the `PULL_QUOTES` array near the bottom of `index.html`. A one-line quote
doesn't go stale the way "our three most recent" does. Refresh them a couple
of times a year, not weekly.

**If the weekly cadence slips**, the relative dates ("2 weeks ago") become
wrong before anything else does. If you know you'll be away, either update the
dates to something that stays true ("June 2026") or drop the
`<p class="reviewer-date">` lines until you're back.

## Automating this later

The Google Places API can supply the rating, the true count, and Google's own
`relativePublishTimeDescription` strings — but it returns a maximum of five
reviews chosen by relevance rather than recency, so it cannot by itself
guarantee "the three most recent." The Google Business Profile API can, but it
needs OAuth against Ahmad's account rather than a plain API key. Revisit when
there's appetite for it; this manual routine is not blocking anything.
