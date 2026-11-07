# Yilo hero

Current v21: 1280 × 608, 14 seconds, 24 fps. Original pelican line art is
animated by local MiniMax H3, with a small thought bubble and a full-width
hatched road. No background polygon, dotted connector, footer icon or title
inside the movie. Reference: https://x.com/pmamtraveller/status/2118294851431092442
(style study only; no reference artwork is copied).

Real native RecordCardView screenshots use the app's extraLarge text setting,
short inputs and more advanced natural output. Chinese input: “先别大改，留点余地。”
English output: “Hold off on a sweeping rewrite; leave us some wiggle room.”
English UI uses English input with Pinyin-marked Simplified Chinese and Japanese
with Romaji. Twelve complete native PNGs are preserved under `public/records/`,
with independent source receipts. They are scaled to fit, never rebuilt or cropped.
The final illustration shows people reusing the learned expression.

The large title is on the website: “Pick up a language while you’re vibe coding” The learned
material is natural rewrites or translations, and the outcome is conversation
with people. Shared phrases: `src/i18n/yilo-examples.json`.

Music: “Fluffing a Duck” by Kevin MacLeod (incompetech.com), CC BY 4.0, 122 BPM.
The 14-second excerpt has background loudness and brief fades. Keep credits from
`public/v/yilo/music-credits.txt` when sharing. Rebuild audio with
`python3 scripts/prepare-yilo-hero-music.py` from the repository root.

Install: `pnpm install --frozen-lockfile`. Preview: `pnpm dev`.
Render: `python3 ../../scripts/render-yilo-line-hero.py`.
Capture native records: `python3 ../../scripts/capture-yilo-hero-screenshots.py --app-source /path/to/yilo-src`.
Current asset receipts are in `scripts/assets/yilo/hero-video-source.json`.
Production builds use only the checked exports and do not need the private app,
H3 or Remotion. `YiloPedalingAnchor` exports the original uncropped 1280 × 720
SVG reference; local H3 inference uses a 1280 × 704 image.

For an English HTML heading-only revision, `python3 scripts/render-yilo-line-hero.py --retitle-only` updates all movie title metadata and receipts without re-encoding picture or audio.

v20 removes the two diagonal supports beneath the wheels. The shared cleanup
in `scripts/lib/yilo_wheel_supports.py` preserves the round rims and uses nearby
pixels from the same road row to retain horizontal hatching. Original H3 assets
stay intact. `--remove-wheel-supports-only` upgrades reviewed v19 exports with
unchanged audio and timing; normal renders apply the same cleanup. The two HTML
headings omit final sentence marks; in-video example punctuation is unchanged.

v21 holds the complete ending composition for the final 1.5 seconds (frames
300–335), without fading the illustration or learning outcome to blank paper.
The shared `src/timing.json` drives a Remotion Freeze for all 12 languages.
The movie remains 14 seconds long; the existing audio fade is unchanged.
