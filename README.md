# bloom-web

Web presence for **Bloom: Your Baby's Story** — the couple-first pregnancy companion for iOS (bundle ID `com.wpluiss.bloom`). Static site, no build step.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | Landing page (waitlist CTA, positioning, SEO + JSON-LD) |
| `styles.css` | Shared design system (ivory / terracotta / sage / charcoal) |
| `privacy.html` | Privacy policy (effective 2026-07-24) |
| `support.html` | Support page + FAQ |
| `404.html` | Branded not-found page (self-contained styles) |
| `CNAME` | Custom domain: `conduitai.io` |
| `bloom/index.html` | Redirect so `conduitai.io/bloom` resolves to the landing page |

## Enabling GitHub Pages

1. Repo **Settings → Pages**.
2. Source: **Deploy from a branch** → branch `main`, folder `/ (root)` → Save.
3. The site goes live at `https://wpbluiss.github.io/bloom-web/` within a minute or two.

## DNS (Porkbun) for conduitai.io

Once the `CNAME` file is in the repo, Pages expects the domain to resolve to GitHub:

- **Preferred (apex):** Porkbun supports an **ALIAS** record. Create `ALIAS conduitai.io → wpbluiss.github.io`. GitHub's docs caution that plain CNAME at the apex is non-standard — ALIAS (CNAME flattening) is the correct way at Porkbun.
- **Alternative:** point the `www` subdomain instead — `CNAME www → wpbluiss.github.io`, then change the `CNAME` file to `www.conduitai.io` and redirect the apex to `www` in Porkbun.
- Optional A-record fallback for apex (if not using ALIAS): `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
- After DNS propagates, tick **Enforce HTTPS** in Settings → Pages.

With a custom domain on a project site, GitHub serves this repo at the domain **root** (`conduitai.io/` = the landing page), not at `/bloom-web/`.

## How the /bloom path works

`bloom/index.html` is a tiny redirect page (meta refresh + `location.replace`) pointing at `../index.html`. So both of these work:

- `conduitai.io/` → landing page
- `conduitai.io/bloom` → redirects to the landing page

All internal links and the stylesheet are referenced relatively, so the site works identically at `wpbluiss.github.io/bloom-web/` and at the custom domain.

## Placeholders / future assets

- `assets/og.png` — Open Graph share image (1200×630) referenced in `index.html` meta tags. **Does not exist yet**; create it and commit it under `assets/`.
- The waitlist CTA is a `mailto:hello@conduitai.io?subject=Bloom%20waitlist` link. When a real list provider is chosen, swap the `href`s (they appear in the header, hero, and waitlist section of `index.html`).
