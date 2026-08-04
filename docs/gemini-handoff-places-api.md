# Gemini Handoff — Google Cloud Places API Key

Paste the block below into **Gemini Cloud Assist** (the ✦ icon in the Google Cloud Console
toolbar) or the Gemini app. It is written to be self-contained: it states the end state,
the non-obvious constraints, and what to report back.

Reusable across clients — only the Place ID in the verification step changes.

---

```
You are helping me set up a Google Cloud API key. I run a web development agency
(Thryve Operations). I need a server-side key that reads public Google reviews for
my clients' businesses so their websites can display their newest reviews
automatically.

Walk me through this in the Google Cloud Console one step at a time. Wait for me to
confirm each step is done before moving to the next. If a menu or button has moved
from where you expect, tell me what to search for instead.

TARGET END STATE
1. A Google Cloud project named "thryve-ops-places"
2. Billing enabled on it
3. The "Places API (New)" enabled
4. An API key named "thryve-places-server", restricted to that one API
5. A $5/month budget alert with email notifications

CONSTRAINTS — these are deliberate, please do not suggest otherwise:

- It must be "Places API (New)", NOT the legacy "Places API". They are separate
  products with different request formats and different response field names. My
  code targets the new one. If you are unsure which is which, tell me the exact
  name shown on each so I can confirm before enabling.

- Under "Application restrictions" on the key, set NONE. Do not set HTTP referrer
  restrictions and do not set IP restrictions. This key is used server-side from
  GitHub Actions, whose runners have dynamic IP addresses, so an IP allowlist
  breaks the job at random. Referrer restrictions do not apply to server-side
  calls at all. The key is protected by the API restriction plus being stored in
  GitHub encrypted Secrets. It is never sent to a browser.

- Under "API restrictions", DO restrict to "Places API (New)" only.

CONTEXT ON COST
Usage is roughly 4 API calls per month per client site (one weekly scheduled
refresh). Please confirm what the current free tier covers for Places API (New)
Place Details requests including the "reviews" field, and flag if that field sits
in a higher-priced SKU than the basic fields. I want to know the real number, not
a reassurance.

VERIFICATION
Once the key exists, give me a curl command I can run in a terminal to confirm it
works. It should call Places API (New) Place Details for this Place ID:

  ChIJBfkPVNXE6AURgcKLg98SKTw

and request exactly these fields:

  displayName, rating, userRatingCount, reviews

Show me the correct header names for the new API (I believe it uses X-Goog-Api-Key
and X-Goog-FieldMask rather than a key query parameter — confirm this).

THEN TELL ME
1. Does the response include a "reviews" array, and how many reviews does it
   contain? I expect a maximum of 5.
2. Does each review object include "publishTime" and
   "relativePublishTimeDescription"? I need both — one to sort by, one to display.
3. Is there any parameter that makes Place Details return reviews sorted newest
   first, or does it always return Google's "most relevant" selection? I need to
   know whether to sort them myself.

IMPORTANT
Do not ask me to paste the API key into this conversation, and do not echo it back
if I paste one by mistake. I will move it directly into GitHub Secrets myself.
```

---

## After Gemini finishes

1. Run the verification curl. Send me the output **with the key stripped out** — I'll
   build against the real response shape instead of guessing field names.
2. Add the key to `thryveops/410-odd-jobs-website` →
   **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `GOOGLE_PLACES_API_KEY`
   - Do not paste it into chat.

## Answers worth double-checking

Gemini is generally reliable on console navigation but can be confidently wrong on
pricing and on the legacy-vs-new distinction. Two things to sanity check against the
docs it cites:

- **Legacy vs New.** If it ever tells you to use a `key=` query parameter instead of
  the `X-Goog-Api-Key` header, it has drifted to the legacy API. Stop and redirect it.
- **Pricing.** Place Details requests that include `reviews` may be billed at a higher
  tier than ID-only or basic-field requests. Ask it to cite the pricing page.

## Reusing this for other clients

Only the Place ID changes. Pull a client's Place ID from their
`search.google.com/local/writereview?placeid=...` link — the same place it came from
for 410 Odd Jobs. One key covers every client site; you do not repeat this setup.
