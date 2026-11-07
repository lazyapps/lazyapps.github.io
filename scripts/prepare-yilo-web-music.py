"""Prepare opt-in AAC audio for the native Yilo web animation."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'scripts/assets/yilo/audio/source.json').read_text())
original=ROOT/source['output']
output=ROOT/'public/v/yilo/web-demo-music-v1.m4a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(original)==source['outputSHA256']
if not output.exists():
 subprocess.run(['ffmpeg','-v','error','-i',str(original),'-c:a','aac','-b:a','192k','-movflags','+faststart','-metadata','title=Fluffing a Duck — Yilo 14-second excerpt','-metadata','artist=Kevin MacLeod','-metadata','copyright=CC BY 4.0 — https://lazyapps.com/v/yilo/music-credits.txt',str(output)],check=True)
(ROOT/'scripts/assets/yilo/web-music-source.json').write_text(json.dumps(dict(source=str(original.relative_to(ROOT)),sourceSHA256=sha(original),output=str(output.relative_to(ROOT)),sha256=sha(output),seconds=14,credits='/v/yilo/music-credits.txt'),indent=2)+'\n')
print(output)
