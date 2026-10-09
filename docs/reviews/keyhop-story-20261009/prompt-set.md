# 灵感追车记 / The runaway idea

15 seconds, three five-second chapters. Orange fox, cream muzzle and tail tip, violet knitted sweater, warm ivory miniature studio and lavender shadows; one golden idea spark remains alive throughout.

1. **Where did that app go?** Two eager reaching attempts and two near misses. A thought bubble establishes Notes as the desired app. Notes, Safari and Mail appear as oversized tactile toy cards; ordering changes between attempts, at 1.6 and 3.15 seconds. The Notes icon remains identical and gold outlined.
2. **Your apps. Their own places.** The same fox anticipates and makes one joyful little hop to the left. Ten fixed home-row toy keys carry genuine app icons; Notes has its permanent D slot, positioned beneath the actual H3 landing. No modifier choreography or settings narration.
3. **Idea intact. Keep going.** The fox types its own work at an ivory desk on a lavender laptop, then gives a relieved proud grin. Coral cup, living spark and a little satisfied tail motion. Product signature and short closing line.

## First-frame artwork

Built-in `image_gen.imagegen` created three single wide cinematic stills. The first establishes the exact original character and studio; subsequent calls use it as an identity/style reference. No app UI, icon or text is generated into these anchors. No external photographic assets. Music is the author's CC BY 4.0 recording of Monkeys Spinning Monkeys.

- chase: `exec-22f4e61e-3807-4bbe-bc0f-f49041c81a54.png`
- hop: `exec-eb05277c-438c-496c-9e3f-d4e703716155.png`
- flow: `exec-d664aa09-4e16-4c9d-ae19-e98b123602c7.png`

The project copies are in `scripts/assets/keyhop/story-v1/*-anchor.png`. All invariants, exact animation prompts, seeds and H3 options are in `scripts/generate-keyhop-story.py`; each generation additionally saves its actual command and anchor hash beside the MP4.

## Local video production

Installed binary `/Users/realazy/tmp/h3.c/h3`; cached MiniMaxAI/MiniMax-H3 snapshot `42ed227ee7df40d41602854ae760620d6eb651fe`. All three character performances are generated locally, not through a remote video service. 65 requested frames, 20 denoising steps, 50 layers, reuse 2, BF16 SSD streaming, internal 640×352, output 1280×704. Shot timing is interpolated to five seconds each in the final 1280×720, 24 fps H.264 film.

`scripts/compose-keyhop-story.py` shapes captions using AppKit/CoreText, adds genuine existing macOS app icons on narrative props, and edits Kevin MacLeod's CC BY 4.0 Monkeys Spinning Monkeys to a 15-second background score. First-frame images are unchanged. Twelve localized exports use the same animated footage and credited soundtrack. See music-license.md for the author's source and attribution.

Reproduce: `python3 scripts/generate-keyhop-story.py all`, then `python3 scripts/compose-keyhop-story.py`. Generation/export scripts deliberately refuse to overwrite earlier MP4s; preserve or version prior output before another run.
