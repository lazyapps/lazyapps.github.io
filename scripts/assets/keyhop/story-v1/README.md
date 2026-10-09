# KeyHop local production files

This directory holds local MiniMax H3 source footage, imagegen first-frame anchors, downloaded licensed music, native text plates, encoder logs and archived edits. These production files remain local; reviewed web assets are published in `public/v/keyhop/`.

The repository retains `scripts/generate-keyhop-story.py`, `scripts/compose-keyhop-story.py`, the final movie/poster and12VTTtracks, plus provenance and review records in `docs/reviews/keyhop-story-20261009/`. `asset-provenance.json` records actual local inference commands, seeds and anchor hashes; `validation-v4.json` records source/output hashes and specifications. `music-license.md` records the original track URL and CC BY4.0 attribution.

To recompose locally, provide the3source clips and their anchors plus the original music at the paths used by the scripts. Existing outputs are never overwritten. Older publicv3edits remain available locally for previous preview links.
