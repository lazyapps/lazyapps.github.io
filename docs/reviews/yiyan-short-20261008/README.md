# YiYan concise update — 2026-10-08

The user asked for shorter video and web copy reflecting the current product.

- Video: 25 → 15 seconds, three chapters, no standalone introduction or outro. Twelve languages, silent 1280×720 H.264, 24 fps.
- Page: one-line introduction, download buttons before the film, six concise feature cards, three closed detail groups. Removed repeated examples, duplicate screenshot, repeated download section and blocking page loader.
- All video motion reuses the genuine **local MiniMax H3** generation from the preceding iteration. No new remote video generation. Native shaped text and an authentic learning record are composited separately.
- iPhone availability is visible in both formats: optional iCloud synchronization and TestFlight beta. Mac follow-up chat and iPhone AI-app handoff are distinct.

Current entry points:

- `src/components/YiYanPage.astro`
- `src/i18n/yiyan-short-copy.json` — the maintained copy for all 12 locales; existing generated locale data is preserved.
- `scripts/compose-yiyan-marketing-v3.py`
- `public/v/yiyan/hero-<locale>-v3.mp4` and matching JPG
- `validation.json` — final encoded-file checksums, dimensions, duration, frame count and visible-copy size.

Local source footage, text plates and manifests remain in ignored `scripts/assets/yiyan/marketing-v2/` and `marketing-v3/`. Previous exports are preserved. Recompose with `/opt/homebrew/bin/python3 scripts/compose-yiyan-marketing-v3.py` when output names are unused. The guard preserves existing exports; use another version for future edits.

## Feature coverage

Product source root: `/Users/realazy/Projects/_vibe/_yiyan`.

| Current capability | Website | 15-second film | Source evidence |
| --- | --- | --- | --- |
| Capture from five AI tools; original request continues; new input only | Card 1, connection details, trust | Chapter 1 | README.md; CONTEXT.md |
| Direct input; Chinese/English/mixed input | Card 2 | Chapter 1 | MainWindowView.swift; CONTEXT.md |
| Focused field / selection refinement | Card 2, Mac details | Chapter 1 | FocusedTextRefinement.swift; YiYanServicesProvider.swift |
| Natural English, focused notes, examples | Card 3 | Chapters 1–2, exact before/after and real record | RecordCardView.swift |
| Record-specific Mac follow-up chat | Card 3; privacy details | Chapter 2, explicitly Mac | RecordChatView.swift; CONTEXT.md |
| US/UK, writing style, explanation language, preserve tone | Card 4 | Represented by refinement; individual settings stay on page | SettingsView.swift |
| Calendar, bookmarks, copy, retry, deletion | Card 5 | Bookmarks in chapter 3; routine management stays on page | MainWindowView.swift; RecordCardView.swift |
| Optional private iCloud sync; same Apple account; iPhone beta | Card 6, connection/privacy details, download CTA | Chapter 3, visible caveat | SettingsView.swift; MobileSettingsScreen.swift |
| iPhone search, calendar, bookmarks, offline synced records | Connection details, card 5 | Bookmarks in chapter 3; browsing details stay on page | RecordsScreen.swift; MobileRecordsCalendar.swift; MobileSettingsScreen.swift |
| iPhone speech, active recall, daily reminders | Card 6 | Chapter 3 | MobileRecordCard.swift; ReviewScreen.swift; MobileSettingsScreen.swift |
| Copy context / open ChatGPT, Claude, Gemini; user sends | Card 6, Mac details | Chapter 3, AI handoff | RecordsScreen.swift; AgentAppHandoff.swift |
| Local default; filtering, redaction; preserve code/paths/URLs; AI service still used | Trust, privacy details | Refinement proof; privacy details stay on page | README.md; CONTEXT.md |
| Local-only follow-up chat; separate cloud deletion | Privacy details | Mac follow-up label; storage details stay on page | CONTEXT.md; SettingsView.swift |
| Shortcuts, Services, pinning, opacity, theme, text size, login startup, updates, CLI export | Mac details; closed Homebrew installation | Utilities stay on page | SettingsView.swift; MainWindowView.swift; Sources/YiYanCLI |

The short film shows the complete core journey rather than every settings switch. The website carries the full audited capability inventory without requiring visitors to read expanded details.

## Advisor decisions

Accepted the approach advice: keep complete detail on the page and the core experience in the film. Put optional iCloud and TestFlight status directly in the iPhone card and final chapter, rather than only in a disclosure.

Completion advisor found no material feature inaccuracy or delivery blocker, verified all 12 video hashes and posters, and confirmed the visible beta/sync caveat. Accepted its wording: this is a 15-second re-edit of existing local MiniMax H3 footage.

## Validation

Final export inspection: every locale is 15 seconds / 360 frames, H.264 yuv420p, 1280×720, 24 fps, no audio. Keyframes were extracted from actual encoded files. Native fonts handle Arabic and Indic shaping. Chinese, English and Arabic responsive browser checks include playback, horizontal overflow and details expansion. Site build and existing SEO/artifact checks pass. No deployment or native-app changes.
