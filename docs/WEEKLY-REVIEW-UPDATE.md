# Weekly Review Update — 410 Odd Jobs

Takes about five minutes. Everything here is public data, so you never need
Ahmad's login or a Google Cloud account.

## 1. Open the review list, sorted by newest

https://search.google.com/local/reviews?placeid=ChIJBfkPVNXE6AURgcKLg98SKTw

Set the sort control to **Newest**. Note two things:

- The **total review count**
- The **top three reviews** — text and reviewer name. Note roughly when each
  was left, but record it as a month ("August 2026"), not as Google's relative
  wording ("2 weeks ago") — see step 3.

## 2. Update the count

From the repo root:

```bash
python3 scripts/update-review-count.py 59
```

That updates all eight places the number appears across `index.html`,
`reviews.html`, and `quote/index.html` — including a meta description and the
JSON-LD `aggregateRating`, neither of which anything else would catch. Use
`--dry-run` first if you want to see what it would touch.

The homepage ticker label ("…and 56 more") is derived automatically as
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
| Date | `<p class="reviewer-date">` — the current month and year, e.g. `August 2026` |
| Avatar letter | `<div class="reviewer-avatar">` — first initial |

**Short reviews:** if one is under roughly 15 words, change its class to
`class="review-text is-short"`. That switches the card to display type so it
reads as punchy rather than half empty. Remove `is-short` when a long review
takes that slot again.

**Use the month and year, not Google's relative wording.** Write `August 2026`,
not `2 days ago`. Relative dates are only true on the day you paste them, and
this update does not reliably happen weekly — on 2026-08-25 the live site was
still claiming "1 day ago" for reviews committed on 2026-08-17, overstating
recency by more than a week. A month label cannot go stale between updates.

**Never invent a date.** Only claim a month you actually saw on the listing. If
you can't tell when a review was left, drop the `<p class="reviewer-date">`
line rather than guessing — a wrong date is a false claim to a customer.

## 4. Check it

```bash
python3 scripts/verify-content.py
```

Then open the homepage and confirm the reviews section: trust bar reads
`5.0` and the new count, three cards show the new reviews, the ticker scrolls
and pauses when you hover it.

## 5. Commit

```bash
git add -A && git commit -m "Update reviews: 3 newest featured, count now 59" && git push
```

GitHub Pages redeploys automatically. Give it a minute, then check
410oddjobs.com.

---

## Things that are easy to get wrong

**The rating is 5.0, not 4.9.** Every review on the listing is five stars. If
that ever changes, the `5.0` in the trust bar is hardcoded in `index.html` —
search for `class="num"`.

**`reviews.html` must hold one card per review Google reports.** As of
2026-08-25 the two are in sync at 59, and `verify-content.py` now enforces it —
the count in the copy is checked against the number of `.review-card` divs, so
a mismatch fails the commit rather than shipping. When you add reviews, add the
cards *and* run the count script; don't bump the number alone.

**The homepage schema states the count too.** `index.html` carries a
`LocalBusiness` block with an `aggregateRating`, and the count script keeps its
`reviewCount` in sync automatically — `verify-content.py` fails the commit if it
ever disagrees with the real card count. You don't edit it by hand. Note that
this markup will *not* produce star ratings in Google Search: a business that
marks up reviews about itself is ineligible for review rich results under
Google's self-serving review policy. It's there as an entity signal, and it's
true. Don't promise the client stars on the strength of it.

**The ticker quotes rarely need touching.** They're short verbatim reviews in
the `PULL_QUOTES` array near the bottom of `index.html`. A one-line quote
doesn't go stale the way "our three most recent" does. Refresh them a couple
of times a year, not weekly.

**If the weekly cadence slips**, nothing silently becomes false — that is the
point of month-and-year dates. What does drift is the count, since new reviews
land whether or not you update. Run the count script every time you touch this,
even if you're not swapping the featured three.

**Normalize two things, never the wording.** Google shows some reviewer names in
full caps ("MEGAN ARTHUR") — title-case those so they don't read as shouting
next to every other name. And collapse any hard line break inside a review body
to a single space; no card in the archive uses `<br>`. The review text itself
stays verbatim, typos and emoji included.

## Automating this later

The Google Places API can supply the rating, the true count, and Google's own
`relativePublishTimeDescription` strings — but it returns a maximum of five
reviews chosen by relevance rather than recency, so it cannot by itself
guarantee "the three most recent." The Google Business Profile API can, but it
needs OAuth against Ahmad's account rather than a plain API key. Revisit when
there's appetite for it; this manual routine is not blocking anything.
