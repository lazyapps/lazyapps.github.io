# YiYan — your own words, used in life

The user rejected the feature-list treatment: “视屏不要做成了说明书，换个方向”. The replacement is a 12-second lifestyle brand film, with no product demonstration, feature lists, cards or instructional captions.

## Story

| Time | Picture | Copy |
| --- | --- | --- |
| 0–4.25s | A woman writes at her laptop in afternoon light | Yesterday; “我们明天接着聊。” |
| 4.25–9s | The same woman prepares to say goodbye to a friend at a café | Today; “Let’s pick this up tomorrow.” |
| 9–12s | Genuine YiYan icon and brand | “把说过的话，变成自己的英语。” |

This fictional campaign dialogue illustrates using one's own everyday words as learning material. It is not a captured app record, a testimonial, a claim of automatic speech or a guarantee of fluency. For other languages the first phrase and day markers are localized; the English phrase remains the payoff. The concise website retains the full current feature information.

Accepted advisor recommendation: the second shot is an identifiable goodbye, including a bag, parting gesture and the friend's acknowledgement. An unspecified café chat would have made the connection between the phrase and its use weaker.

## Production

- Two original photoreal reference stills generated with built-in imagegen. The second uses the first as a character/wardrobe/style reference. These are fictional adults.
- All live footage animated with **local MiniMax H3** at `/Users/realazy/tmp/h3.c/h3`, using the installed MiniMaxAI snapshot. Twenty denoising steps, all fifty layers, reuse 2, SSD streaming, 640×352 internal rendering and 1280×704 output.
- Anchors: ignored `scripts/assets/yiyan/marketing-v4/{work,cafe}-anchor.png`.
- Built-in originals retained at `/Users/realazy/.codex/generated_images/01a11b96-a4d8-7671-8f80-4f45e5841c67/exec-568ebc79-d523-440f-99fb-8cce26622d4c.png` and `exec-7a048eba-a6f0-4547-a42e-a2d5bd933ae7.png`.
- Exact local video prompts and commands: `scripts/generate-yiyan-marketing-v4.py`; each source has `.prompt.txt`, `.generation.json` and local log.
- Moderate slow motion and frame interpolation create two 4.25/4.75-second shots. All subtitles and brand text use native font shaping; they are composited separately from generated images. No generated UI or text.
- Composer: `scripts/compose-yiyan-marketing-v4.py`; localized copy: `src/i18n/yiyan-story-copy.json`.
- Final files: `public/v/yiyan/hero-<locale>-v4.mp4` and matching JPG. Prior edits remain available.

## Additional page correction

The user requested left alignment in the expanded “支持与连接” content. Disclosure heading and body now share the same text edge, without bullet indentation. Native details semantics and logical alignment for RTL remain intact. CUA measured heading x=50.75 + inset 19.8px and paragraph x=70.55px, confirming the shared edge.

## Current app icon

The user also requested the updated icon. The current app's `AppIcon.icon` is copied into `scripts/assets/yiyan/AppIcon.icon`, including the newer gradient, native glass and sun glow. `scripts/prepare-yiyan-brand-web.py` exports native pixels to the shared website icon and extracts the exact authored silhouettes for the homepage symbol. No AI redraw.

`python3 scripts/render-yiyan-opengraph.py` updates the three share images with the current genuine symbol, website grain and typography. The floating sun is excluded from title-height alignment; the full group fits the center-square safe area. Website header, favicon, privacy pages and homepage all consume the shared refreshed assets. The film's end card uses the same current icon. Previous web brand files remain in the ignored generation archive.

## Validation

`validation.json` records checksums and media properties of the completed encoded outputs. Review frames are extracted from those encoded files, alongside the original H3 motion contact sheets. Existing site build, SEO and artifact checks are used; no native-app changes or deployment.

## Music

Scott Buckley's **A Kind Of Hope**, a gentle piano piece with strings and ambient synth. The exact track page explicitly permits free commercial use with attribution under CC BY 4.0:
https://www.scottbuckley.com.au/library/a-kind-of-hope/
https://creativecommons.org/licenses/by/4.0/

The final film uses seconds 6–18 of the original, adjusted to a quiet -24 LUFS target, with a 0.5-second entrance and 1.4-second closing fade. The first six seconds were excluded because they are mostly the source's ambient fade-in. No vocals or narration were added. Measured final loudness is retained in `audio-loudness.txt`.

`scripts/finish-yiyan-marketing-v4.py` preserves the silent H3 composites under the ignored generation folder and adds the same music to all twelve localized versions without re-encoding video. `validation.json` checks identical video packet hashes and records the original track hash, audio processing and output properties.

Credit with linked source, author, license and editing notice is visible in the landing-page footer, embedded in every MP4's comment/copyright metadata, and retained in `public/v/yiyan/music-credits.txt`. For a repost on a video platform, copy that credit into the video description. The complete music master stays in the ignored local generation cache.

Final checks: `npm run build` passed with all existing SEO/social/link/artifact checks (63 pages); its pre-existing unrelated large-JS-chunk warning remains. CUA verified Chinese playback uses v4, duration 12s, 1280px decoded width, readyState 4, muted autoplay and controls. Desktop and 375px mobile have no horizontal overflow. Chinese disclosure body x=133.80px matches heading x=114px + 19.8px inset. Arabic mobile uses its own v4 file, correct RTL and no overflow. All twelve final encoded contact rows were visually inspected; current icon, native shaping, captions and end lines fit. Local preview retained at http://127.0.0.1:4324/yiyan/ .

## Completion review

Independent read-only Astra/xhigh review (`completion-advice.md`) found no material delivery blocker. It confirmed story clarity, current branding, all twelve final hashes and the author's explicit free-commercial license with implemented attribution. Accepted the recommendation to deliver; no further changes were requested.
