# YiYan — Sounds like a win-win

User's requested new creative: personified supported agents; any input language yields idiomatic English feedback; use the learned phrase with Trump; finish with both giving thumbs-up and “赢麻了”. The website's original style/layout must stay unchanged.

## Fourteen-second story

| Time | Action | Product meaning |
| --- | --- | --- |
| 0–4s | Fictional learner casually chats with five distinct logo-inspired robots. Chinese, Japanese, Spanish and rough English speech bubbles appear. | Continue using your agent in whichever language you write. |
| 4–7s | Original-language input remains beside a genuine YiYan-branded English feedback card: **Sounds like a win-win.** Brief note: win-win = 双赢. | Idiomatic English feedback, rather than an agent answering the conversation. |
| 7–10s | The same exact card moves into the learner's speech while she chats with a cartoon Trump. | Reuse what you learned. |
| 10–14s | Both share a cheerful thumbs-up. Same English stays visible; Chinese punchline **赢麻了**, current YiYan icon and concise localized brand line appear. | The comedic payoff stays connected to the learned expression. |

The adviser recommended carrying one identical sentence card through feedback, use and punchline. Accepted. The lead selected “Sounds like a win-win.” instead of the earlier working phrase because it motivates the mutual thumbs-up and Chinese meme. All source examples express mutual benefit. The product's `TranslationPromptBuilder.swift` detects original/mixed languages and translates retained prose into idiomatic English, supporting this message.

## Characters and references

Unmistakable original 3D clay/vinyl comedy. The adult learner is fictional, not a depiction of the user. Trump is a stylized public-figure caricature in a generic studio, with no real footage, voice, political messaging, official setting or endorsement. A persistent localized AI-fiction knockout watermark and accessible media description make this explicit.

All five supported source agents are included, in this left-to-right order:

- Pi: current three-color pixel mark, sourced from https://pi.dev/logo-auto.svg via the official https://pi.dev/ download.
- Claude Code: irregular coral starburst. Exact Claude mark from the product's `Distribution/Assets.xcassets/AgentClaude.imageset/claude.svg`.
- Codex: black/ivory knot head, OpenAI blossom from the product's `AgentChatGPT.imageset/openai-blossom.svg`, named Codex explicitly.
- OpenCode: black pixel-square robot, actual official mark from https://opencode.ai/favicon-96x96-v3.png; verified against https://opencode.ai/brand and its preview image.
- Antigravity: rainbow arch body, official press icon https://antigravity.google/assets/image/brand/antigravity-icon__full-color.svg via https://antigravity.google/press.

The robot silhouettes/colors embody these marks. Actual unmodified marks and native-rendered names are composited separately, preserving identification if generated animation moves slightly.

## Production and provenance

Built-in imagegen created three original first-frame stills: robots, conversation and double thumbs-up. The latter two use prior frames for identity/style continuity. Anchors, reference brand board and original outputs are retained in the ignored `scripts/assets/yiyan/marketing-v5/` cache; exact character specifications are reflected in generator prompts and this brief.

**Local MiniMax H3** animates all three character scenes, using the installed MiniMaxAI model with twenty steps, all fifty layers, reuse2 and SSD streaming. Renderer: 640×352 internal, 1280×704 output, 73 frames per generated clip. `scripts/generate-yiyan-marketing-v5.py` records exact prompts, commands, seeds and anchor checksums. Native-shaped typography and true YiYan branding are composited by `scripts/compose-yiyan-marketing-v5.py`. No generated glyphs or invented UI screenshots.

Localized copy: `src/i18n/yiyan-agent-film-copy.json`, all twelve existing languages. Every version demonstrates the same four source languages and identical idiomatic English; surrounding labels, lesson, brand line and punchline are localized.

Music remains Scott Buckley's **A Kind Of Hope**, CC BY4.0, explicitly free for commercial projects with attribution: https://www.scottbuckley.com.au/library/a-kind-of-hope/ . v5 uses original seconds6–20 at a quiet -24 LUFS target with 0.5s entrance /1.4s exit fades. Credit and modification notice remain in the existing page footer, all MP4 metadata and public music-credits.txt. Source hash and measured audio properties are recorded in validation.json: final audio measures **-23.8 LUFS**, **-6.9 dBFS true peak**. The full master stays local/ignored.

Final web exports: `public/v/yiyan/hero-<locale>-v5.mp4` with matching posters. Earlier versions stay intact. Page integration changes only media URLs and the appropriate accessible description; original CSS/layout/content from the last user-approved restoration remain intact. No deployment or native product edits.

## Final validation

- All twelve final encodes: 14 seconds, 336 frames, 1280×720 H.264/yuv420p, stereo AAC 48kHz. File sizes and exact hashes are recorded in validation.json. Video packet hashes match their silent sources exactly after audio muxing.
- Inspected actual H3 motion contacts for all three scenes and all twelve localized final encoded contacts. Character identities, single thumbs-up hands, source phrases, English feedback, punchlines and typography remain legible and stable.
- `final-contact-0.jpg` / `final-contact-1.jpg` contain actual final encoded frames at 2.2s, 5s, 8.5s and 12s. Individual frames remain in ignored `final-frames/`.
- Page CSS is byte-identical to HEAD. Against `page-before-video-integration.astro`, only the hero-copy import, MP4/JPEG URLs and accessible media description changed.
- `npm run build` passed, including SEO and existing artifact checks. All twelve built pages reference v5; built media SHA-256 hashes match the validated exports. Existing unrelated large-JS-chunk warning remains.
- Browser verification: Chinese desktop and 375×812 mobile, plus Arabic mobile. Correct localized v5 source, 14-second duration, readyState 4, no media error, muted playback and controls retained; no horizontal overflow. Viewport restored and Chinese preview retained.
- Independent completion adviser reviewed the durable encoded artifacts and returned **“No material blocker. Deliver this version.”** Accepted: the repeated sentence card makes multilingual input → feedback → reuse clear, and the clay caricature plus fiction label makes the imagined encounter explicit. Full review: `completion-advice.md`.

## Requested typography refinement

Applied `make-interfaces-feel-better` and its typography reference to the video overlays. Website typography/CSS remain unchanged.

| Before | After |
| --- | --- |
| Centered multilingual phrases and feedback body; English and explanations compete | Source phrases, English and explanations share left edges; Arabic labels/explanations retain natural RTL alignment and the header icon moves to the right |
| Smaller English with tight vertical space and coral secondary label | Larger English in a taller card, consistent 28px inset, quieter secondary color and clear vertical spacing |
| Agent names in pills with logos below | True logos and names on one baseline, consistent spacing, subtle backdrop for contrast |
| Closing punchline offset right; brand and closing line crowded together below | Punchline and tagline share the center axis; compact brand sits separately at top left |
| Fiction label in rounded white panel | Plain knockout watermark with a restrained shadow; no panel, border or button |

Revisions preserve the same local H3 character animation, story, phrase, duration and licensed soundtrack. Previous exports are retained in the ignored revision archive.

The refreshed twelve final encoded contacts, source manifests and built media hashes were rechecked after this refinement; the build passed again. The independent typography completion review returned **“No material blockers. Deliver this revision.”** Accepted: clear hierarchy and alignment, no visible clipping/overlap, natural Arabic direction, and a plain knockout fiction watermark without a panel/border/button. Full addendum: `typography-completion-advice.md`.

## Optical alignment and integrated speech tails

Subsequent direct user corrections refine the same film, after the above review:

| Before | After |
| --- | --- |
| Watermark positioned by its 300px transparent text plate, leaving excessive space on the right | Crop to actual visible lettering/shadow; right and bottom margins are both 20px in every locale |
| Native font padding biases text upward inside source bubbles | Center actual glyph bounds vertically, preserving left alignment and natural script shaping |
| Feedback-card rows positioned using transparent text plate boxes | Center the complete visible header/English/explanation group, with equal 20px gaps and header icon/text optically aligned |
| Detached triangle drawn above the bubble, always pointing upward | Union the rounded body and tail in one antialiased silhouette with one continuous border; point toward the learner (up during conversation, down in the final shot); omit the tail while the card moves |

All twelve languages are regenerated from the same local H3 plates. This is a routine visual correction checked directly against full-size frames and final encoded contact sheets; the earlier independent review remains preserved for its corresponding revision. Website CSS/layout and the licensed music remain unchanged.
