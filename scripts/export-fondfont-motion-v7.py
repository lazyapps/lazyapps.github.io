"""Export the original font-drawer installation metaphor as a silent hero film.

H3 supplies the actual insertion, latch and cover-retraction motion. The exact
paired reference frames provide brief readable starting/installed holds. This is
conceptual editorial artwork, not captured iOS or app UI.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v7'
PUBLIC = ROOT / 'public/v/fondfont'
GRADE = "lutrgb=r='min(255,val*255/248)':g='min(255,val*255/248)':b='min(255,val*255/248)'"


def run(cmd):
    subprocess.run(cmd,check=True)


def main():
    movie=ASSETS/'type-drawer-h3.mp4'
    out=PUBLIC/'hero-h3-v7.mp4'
    poster=PUBLIC/'hero-h3-v7.jpg'
    if out.exists():raise RuntimeError('Preserve exported movies; use a new version.')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(movie)]))
    raw_duration=float(probe['format']['duration'])
    # A neutral white matte lets multiply blending carry the website's actual
    # paper tone through the artwork without a tinted rectangular video field.
    run(['ffmpeg','-v','error','-y','-i',str(ASSETS/'end-anchor.png'),'-vf',GRADE,'-frames:v','1','-q:v','2',str(poster)])
    graph=(
        f"[0:v]setpts=PTS-STARTPTS,fps=30,{GRADE},trim=duration=0.65,format=yuv420p[a];"
        f"[1:v]setpts={4.2/raw_duration}*(PTS-STARTPTS),{GRADE},minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,"
        "trim=duration=4.2,format=yuv420p[b];"
        f"[2:v]setpts=PTS-STARTPTS,fps=30,{GRADE},trim=duration=1.2,format=yuv420p[c];"
        "[a][b]xfade=transition=fade:duration=0.15:offset=0.5[ab];"
        "[ab][c]xfade=transition=fade:duration=0.25:offset=4.45[v]"
    )
    run(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(ASSETS/'start-anchor.png'),
        '-i',str(movie),'-loop','1','-framerate','30','-i',str(ASSETS/'end-anchor.png'),
        '-filter_complex',graph,'-map','[v]','-t','5.65','-an','-c:v','libx264','-preset','slow','-crf','19',
        '-pix_fmt','yuv420p','-movflags','+faststart',str(out)])
    final_probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(out)]))
    sources=[ASSETS/name for name in ['start-reference.png','end-reference.png','start-anchor.png','end-anchor.png','h3-prompt.txt','type-drawer-h3.mp4']]
    manifest={
        'scope':'Original conceptual font drawer installing into the shared iOS system font library. Not native UI. Compatibility is stated in localized copy.',
        'engine':'MiniMax-H3','sourceDuration':raw_duration,'finalProbe':final_probe,
        'treatment':'Readable owned-font filename, H3 docking and cover retraction, installed inventory hold. Neutral-white matte; no loop or reverse.',
        'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
        'outputs':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [out,poster]],
    }
    (ASSETS/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(out)


if __name__=='__main__':main()
