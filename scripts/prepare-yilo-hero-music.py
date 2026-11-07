"""Prepare the credited, lightweight comic pulse for the Yilo pedaling film."""
from pathlib import Path
import hashlib,json,subprocess,urllib.request
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scripts/assets/yilo/audio/fluffing-a-duck.mp3'
URL='https://incompetech.com/music/royalty-free/mp3-royaltyfree/Fluffing%20a%20Duck.mp3'
TRACK='https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100768'
if not SOURCE.exists():SOURCE.write_bytes(urllib.request.urlopen(URL,timeout=60).read())
TARGET=ROOT/'video/yilo-hero/public/music.wav'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(SOURCE),'-t','14','-af','loudnorm=I=-24:TP=-4:LRA=7,afade=t=in:st=0:d=0.15,afade=t=out:st=13.2:d=0.8','-ar','48000','-ac','2','-c:a','pcm_s16le',str(TARGET)],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=dict(checkedOn='2026-11-07',title='Fluffing a Duck',author='Kevin MacLeod',trackUrl=TRACK,downloadUrl=URL,license='CC BY 4.0',licenseUrl='https://creativecommons.org/licenses/by/4.0/',isrc='USUAN1100768',originalTempoBPM=122,source=str(SOURCE.relative_to(ROOT)),sourceSHA256=sha(SOURCE),output=str(TARGET.relative_to(ROOT)),outputSHA256=sha(TARGET),changes='Original seconds 0–14, background loudness adjustment, 0.15-second fade in and 0.8-second fade out. Tempo unchanged.')
(ROOT/'scripts/assets/yilo/audio/source.json').write_text(json.dumps(receipt,indent=2)+'\n')
credits='''Yilo hero — music attribution

“Fluffing a Duck” — Kevin MacLeod (incompetech.com).
Author: https://incompetech.com/
Track: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100768
Licensed under Creative Commons: By Attribution 4.0 License
https://creativecommons.org/licenses/by/4.0/
ISRC: USUAN1100768.

Changes: original seconds 0–14, background loudness adjustment,
0.15-second fade in and 0.8-second fade out. Tempo unchanged (122 BPM).
Keep this attribution with shared video, in the description or accompanying page.
The license covers the music, not the Yilo brand or the complete film.

Earlier v7–v16 films retain their original soundtrack and attribution:
https://lazyapps.com/v/yilo/music-credits-v16.txt
'''
(ROOT/'scripts/assets/yilo/hero-music-credits.txt').write_text(credits)
(ROOT/'public/v/yilo/music-credits.txt').write_text(credits)
