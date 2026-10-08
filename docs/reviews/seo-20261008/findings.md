# SEO optimization — 2026-10-08

## Baseline

- Astro builds 52 site pages, representing 51 unique canonical URLs. `/fondfont/` duplicates `/fondfont/en/` intentionally.
- Titles, descriptions, canonical tags and social metadata already existed. There was no sitemap or robots.txt.
- Chinese roots for CHMate, KeyHop and YiYan redirected based on browser/storage language; FondFont's English alias also redirected. English homepage entries depended on those redirects.
- Most language switchers exposed only JavaScript-driven select options. Four public FondFont experiment pages were also indexable.

## Implemented

- Generate `/sitemap.xml` from the final HTML after privacy URLs are flattened. Include 51 self-canonical pages; exclude the FondFont alias and copied HTML assets. No invented modification dates or priorities.
- Add `/robots.txt` declaring the sitemap and permitting crawling of content and rendering resources.
- Keep every existing localized URL and its reciprocal hreflang cluster. Remove automatic language redirects; the three Chinese roots remain Chinese, while `/fondfont/` is a stable English alias with canonical `/fondfont/en/`.
- Link English homepage entries to English canonical product URLs and correct the product-card heading level from H3 to H2.
- Add a compact native language disclosure with real links on each localized product page, usable with JavaScript disabled.
- Add WebSite/Organization JSON-LD on the home page and basic SoftwareApplication JSON-LD to six product families using existing page facts. No ratings, reviews, prices, or rich-result eligibility claims.
- Clarify search titles on the home page, World Book, English KeyHop, and English/simplified/traditional Chinese YiYan. Condense YiYan descriptions in those three languages; update its source copy and regenerate locale data, preserving visible brand headlines and social copy.
- Mark four legacy FondFont HTML experiments `noindex`; retain the files and public media.
- Add `npm run check:seo` and run it automatically during builds. Declare the already-installed HTML parser `parse5` as a direct development dependency in the npm lockfile used by CI.

## Verification

- `npm run build`: passed, 52 pages and 51 sitemap URLs; existing FondFont asset checks also passed.
- SEO validation: final canonical targets, privacy `.html` URLs, descriptions, H1s, reciprocal hreflang and self references, crawlable language links, social assets, JSON-LD, internal link destinations and exact sitemap membership passed.
- Sitemap XML parsed successfully with an independent XML parser: 51 URLs, both privacy pages included, FondFont alias and media paths excluded.
- Deliberately inserting a sitemap alias, breaking a hreflang target, or reverting a privacy canonical to its pre-flattened URL causes validation failure. Built files restored; see `validator-checks.json`.
- Headless Chrome: all four product roots remain stable with English browser preferences and stored English choices. Explicit dropdown switching works and preserves query strings/fragments. Mobile Arabic and all four language-link menus with JavaScript disabled show no horizontal overflow. See `browser-checks.json` and mobile captures.

## Advisor decisions

The Astra/xhigh approach review recommended making FondFont alias behavior deterministic before implementation. Adopted: no automatic alias redirect, canonical stays `/fondfont/en/`, English internal entries use `/en/`, sitemap excludes `/fondfont/`. The validator explicitly allows only that known alias and resolves all canonical/hreflang targets against final build output. Review: `approach-advisor.md`.

The independent Astra/xhigh completion review passed with no material SEO or navigation blockers. It checked the source diff, final build output and browser evidence, including the unobstructed Arabic menu capture. Accepted the completion decision because it agrees with the build, mutation checks and browser observations. Review: `completion-advisor.md`.

## Scope and follow-up

Changes are local; this work does not deploy or submit anything to Search Console. After publishing, submit `https://lazyapps.com/sitemap.xml` and inspect representative English/Chinese URLs. Indexing, ranking and traffic effects have not been measured. Basic app markup does not establish Google software rich-result eligibility without its additional required fields.

Existing unrelated `.gitignore` changes were preserved.

## Primary references

- [Google: multilingual sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites) — stable locale URLs and user-controlled language switching.
- [Google: localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions) — reciprocal hreflang, including self. HTML annotations are sufficient; duplicating them in the sitemap is unnecessary.
- [Google: build a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) — list preferred canonical URLs.
- [Google: software application data](https://developers.google.com/search/docs/appearance/structured-data/software-app) — distinguish basic app semantics from rich-result requirements.
