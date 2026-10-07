"""Compose a silent H3 glyph opening and authentic localized installation guide."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v5'
OUT = ROOT / 'public/v/fondfont'
LOCALES = {'en':'en-US','zh-hans':'zh-Hans','zh-hant':'zh-Hant',
           'ja':'ja','ko':'ko','fr':'fr-FR','de':'de-DE'}


def ffmpeg(*args):
    subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    args = parser.parse_args()
    movie = ASSETS / 'type-assembly-h3.mp4'
    native = args.source.resolve() / 'AppStore/Preview/Remotion/public/footage/iphone'
    if not movie.exists():
        parser.error('Generate and inspect the H3 take first.')
    if any((OUT / f'hero-h3-v5-{locale}.mp4').exists() for locale in LOCALES):
        parser.error('Preserve previous exports; use a new version.')
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fondfont-v5-') as folder:
        temporary = Path(folder)
        opening = temporary / 'opening.mkv'
        # Interpolation only retimes actual H3 motion, not a substitute for it.
        duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries',
            'format=duration','-of','csv=p=0',str(movie)],text=True))
        ffmpeg('-i',movie,'-vf',
            f'setpts={3.0/duration:.8f}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci,'
            "lutrgb=r='min(val*255/242,255)':g='min(val*255/242,255)':b='min(val*255/242,255)',"
            'tpad=stop_mode=clone:stop_duration=0.4,trim=duration=3.25,setsar=1,format=yuv420p',
            '-an','-c:v','ffv1','-threads','2',opening)
        for locale,store in LOCALES.items():
            clip = native / store / '04-install.mp4'
            selection = temporary / f'selection-{locale}.mkv'
            guide = temporary / f'guide-{locale}.mkv'
            # Full original viewport stays intact. Select the genuine selection
            # view and loaded guide; omit the intervening sheet loading transition.
            fit = 'scale=376:-2,pad=768:864:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1,format=yuv420p,fps=30'
            ffmpeg('-i',clip,'-vf','trim=start=0:end=0.25,setpts=PTS-STARTPTS,'+fit+
                ',tpad=stop_mode=clone:stop_duration=1.05,trim=duration=1.3',
                '-an','-c:v','ffv1','-threads','2',selection)
            ffmpeg('-i',clip,'-vf','trim=start=2:end=6,setpts=PTS-STARTPTS,'+fit+
                ',tpad=stop_mode=clone:stop_duration=1.5,trim=duration=5.5',
                '-an','-c:v','ffv1','-threads','2',guide)
            output = OUT / f'hero-h3-v5-{locale}.mp4'
            ffmpeg('-i',opening,'-i',selection,'-i',guide,'-filter_complex',
                '[0:v][1:v]xfade=transition=fade:duration=0.4:offset=2.85[handoff];'
                '[handoff][2:v]xfade=transition=fade:duration=0.25:offset=3.90[out]',
                '-map','[out]','-an','-c:v','libx264','-threads','2','-preset','slow',
                '-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',output)
            poster = OUT / f'hero-h3-v5-{locale}.jpg'
            ffmpeg('-ss','3','-i',clip,'-vf',fit,'-frames:v','1','-q:v','2',poster)
            info = {
                'model':'MiniMax-H3',
                'concept':'Rigid sculptural glyph convergence, then actual font selection and installation guide',
                'nativeScope':'The footage explains profile download and completion in Settings; it does not show OS completion confirmation.',
                'playback':'Silent, once, no controls, final native installation-guide poster for reduced motion',
                'openingSeconds':3.25,'nativeSelectionSeconds':1.3,'nativeGuideSeconds':5.5,
                'sources':[
                    {'path':str(movie.relative_to(ROOT)),'sha256':digest(movie)},
                    {'path':f'AppStore/Preview/Remotion/public/footage/iphone/{store}/04-install.mp4','sha256':digest(clip)},
                ],
                'output':output.name,'bytes':output.stat().st_size,
            }
            (OUT / f'hero-h3-v5-{locale}.json').write_text(json.dumps(info,indent=2)+'\n')
            print(locale,output.stat().st_size,'bytes',flush=True)


if __name__ == '__main__':
    main()
