"""Export H3's whole-object closure; localized glyphs remain exact SVG paths."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v8'
PUBLIC = ROOT / 'public/v/fondfont'
GRADE = "lutrgb=r='min(255,val*255/248)':g='min(255,val*255/248)':b='min(255,val*255/248)'"


def main():
    movie = ASSETS / 'shared-library-h3.mp4'
    out = PUBLIC / 'hero-h3-v8.mp4'
    poster = PUBLIC / 'hero-h3-v8.jpg'
    if out.exists():
        raise RuntimeError('Preserve exported movies; use a new version.')
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(movie)]))
    duration = float(probe['format']['duration'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ASSETS / 'end-anchor.png'), '-vf', GRADE, '-frames:v', '1', '-q:v', '2', str(poster)], check=True)
    graph = (
        f"[0:v]setpts=PTS-STARTPTS,fps=30,{GRADE},trim=duration=0.7,format=yuv420p[a];"
        f"[1:v]setpts={3.6/duration}*(PTS-STARTPTS),{GRADE},minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,trim=duration=3.6,format=yuv420p[b];"
        f"[2:v]setpts=PTS-STARTPTS,fps=30,{GRADE},trim=duration=1.4,format=yuv420p[c];"
        "[a][b]xfade=transition=fade:duration=0.15:offset=0.55[ab];"
        "[ab][c]xfade=transition=fade:duration=0.2:offset=3.95[v]"
    )
    subprocess.run(['ffmpeg', '-v', 'error', '-loop', '1', '-framerate', '30', '-i', str(ASSETS / 'start-anchor.png'),
                    '-i', str(movie), '-loop', '1', '-framerate', '30', '-i', str(ASSETS / 'end-anchor.png'),
                    '-filter_complex', graph, '-map', '[v]', '-t', '5.35', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)], check=True)
    final = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(out)]))
    files = [ASSETS / name for name in ['start-reference.png', 'end-reference.png', 'start-anchor.png', 'end-anchor.png', 'h3-prompt.txt', 'shared-library-h3.mp4', 'font-manifest.json']]
    (ASSETS / 'manifest.json').write_text(json.dumps({
        'engine': 'MiniMax-H3', 'scope': 'Conceptual full iOS library enclosure. Not actual hardware or native UI. Exact localized typography is a separate SVG layer.',
        'rawProbe': probe, 'finalProbe': final,
        'framing': 'New complete object geometry. Only empty studio-ground margins are trimmed when preparing anchors; no silhouette mask or object crop.',
        'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
        'outputs': [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in [out, poster]],
    }, indent=2) + '\n')
    print(out)


if __name__ == '__main__':
    main()
