"""Compose H3 document opening with installed hold and a quiet forward reset."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v9'
PUBLIC = ROOT / 'public/v/fondfont'


def main():
 movie = ASSETS / 'shared-documents-h3.mp4'
 out = PUBLIC / 'hero-h3-v9.mp4'
 if out.exists(): raise RuntimeError('Preserve media exports; use a new version.')
 raw = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(movie)]))
 duration = float(raw['format']['duration'])
 graph = (
  '[0:v]setpts=PTS-STARTPTS,fps=30,trim=duration=1,format=yuv420p[a];'
  f'[1:v]setpts={3/duration}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=1,trim=duration=3,format=yuv420p[b];'
  '[2:v]setpts=PTS-STARTPTS,fps=30,trim=duration=5.7,format=yuv420p[c];'
  '[3:v]setpts=PTS-STARTPTS,fps=30,trim=duration=0.7,format=yuv420p[d];'
  '[a][b]xfade=transition=fade:duration=0.15:offset=0.85[ab];'
  '[ab][c]xfade=transition=fade:duration=0.2:offset=3.65[abc];'
  '[abc][d]xfade=transition=fade:duration=0.35:offset=8.65[v]'
 )
 subprocess.run(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(ASSETS/'start-anchor.png'),'-i',str(movie),'-loop','1','-framerate','30','-i',str(ASSETS/'end-anchor.png'),'-loop','1','-framerate','30','-i',str(ASSETS/'start-anchor.png'),'-filter_complex',graph,'-map','[v]','-t','9','-an','-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
 final = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(out)]))
 sources = [ASSETS/name for name in ['start-reference.png','end-reference.png','start-anchor.png','end-anchor.png','imagegen-start-prompt.txt','imagegen-end-prompt.txt','h3-prompt.txt','shared-documents-h3.mp4','font-manifest.json']]
 (ASSETS/'manifest.json').write_text(json.dumps({
  'engine':'MiniMax-H3', 'scope':'Conceptual installation and shared font library. H3 moves only the two complete blank document planes; all type and system/install state is exact code/SVG, not generated native UI.',
  'rawProbe':raw,'finalProbe':final,'timeline':{'source':[0,.8],'profile':[.8,1.8],'settingsInstall':[1.8,3.2],'registered':[3.2,4.2],'shared':[4.2,8.35],'quietReset':[8.35,9]},
  'loop':'Forward document opening, stable installed outputs, brief fade to poised start. No reversed installation or glyph motion.',
  'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
  'outputs':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [out,PUBLIC/'hero-h3-v9.jpg']],
 },ensure_ascii=False,indent=2)+'\n')
 print(out)


if __name__=='__main__': main()
