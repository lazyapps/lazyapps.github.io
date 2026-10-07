"""Export photographic H3 material motion beside an authentic iOS installation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v3'
TARGET = ROOT / 'public/v/fondfont'
PHONE = (365, 32, 380, 777)
SCREEN = (385, 51, 340, 738)
SECONDS = 9


def run(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-n', *map(str, args)], check=True)


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=nw=1:nk=1', str(path)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path, help='FondFont app repository')
    args = parser.parse_args()
    footage = args.source.resolve() / 'AppStore/Preview/Remotion/public/v8-footage'
    source = ASSETS / 'paper-material-h3.mp4'
    output = TARGET / 'hero-h3-v3c.mp4'
    if output.exists():
        parser.error('Preserve exports; use a new version.')
    guide, settings, installed = [footage / name for name in
        ['c2-sheet.mp4', 'c3-ios-install.mp4', 'c4-installed.mp4']]
    native = ASSETS / 'native-install-sequence.mkv'
    if not native.exists():
        run('-i', guide, '-i', settings, '-i', installed, '-filter_complex',
        '[0:v]trim=start=0.1:duration=0.9,setpts=PTS-STARTPTS,scale=340:738,fps=24,setsar=1[g];'
        '[1:v]trim=start=3.2,setpts=PTS-STARTPTS,scale=340:738,fps=24,setsar=1[s];'
        '[2:v]scale=340:738,fps=24,tpad=stop_mode=clone:stop_duration=7,'
        'trim=duration=7,setpts=PTS-STARTPTS,setsar=1[d];'
        '[g][s][d]concat=n=3:v=1:a=0,trim=duration=9,format=rgba[n]',
            '-map', '[n]', '-an', '-t', SECONDS, '-c:v', 'ffv1', '-threads', '2', native)
    mask = Image.new('L', SCREEN[2:], 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 339, 737), radius=53, fill=255)
    mask.save(ASSETS / 'screen-mask.png')
    # The original bezel is the unmodified Apple device artwork used by the app preview.
    with Image.open(ASSETS / 'iphone-bezel.png') as bezel:
        bezel.resize(PHONE[2:], Image.Resampling.LANCZOS).save(ASSETS / 'bezel-web.png')
    if not (ASSETS / 'guide-screen.png').exists():
        run('-ss', '0.1', '-i', guide, '-vf', 'scale=340:738', '-frames:v', '1', ASSETS / 'guide-screen.png')
    print_mask = Image.new('L', (768, 864), 0)
    ImageDraw.Draw(print_mask).rectangle((25, 395, 370, 752), fill=255)
    print_mask.filter(ImageFilter.GaussianBlur(8)).save(ASSETS / 'print-mask.png')
    normalize = "lutrgb=r='min(255,val*255/250)':g='min(255,val*255/249)':b='min(255,val*255/248)'"
    movie_white = "lutrgb=r='min(255,val*255/249)':g='min(255,val*255/244)':b='min(255,val*255/241)'"
    graph = (
        '[0:v]trim=duration=0.3,setpts=4.5*(PTS-STARTPTS),minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,split[forward][back];'
        '[back]reverse[reverse];[forward][reverse]concat=n=2:v=1:a=0,'
        f'{movie_white},fps=24,tpad=stop_mode=clone:stop_duration=9,trim=duration=9,format=yuv420p[movingPaper];'
        f'[4:v]{normalize},split[resetPaper][print];'
        '[print]format=rgb24[printRGB];[8:v]format=gray[printMask];[printRGB][printMask]alphamerge[fixedPrint];'
        '[movingPaper][fixedPrint]overlay=0:0[paper];'
        '[1:v]format=rgb24[ui];[2:v]format=gray[mask];[ui][mask]alphamerge[screen];'
        '[paper][screen]overlay=x=385:y=51:shortest=1[withScreen];'
        '[3:v]format=rgba[bezel];[withScreen][bezel]overlay=x=365:y=32[film];'
        '[5:v]format=rgb24[guide];[6:v]format=gray[resetMask];[guide][resetMask]alphamerge[resetUI];'
        '[resetPaper][resetUI]overlay=x=385:y=51[resetScreen];'
        '[7:v]format=rgba[resetBezel];[resetScreen][resetBezel]overlay=x=365:y=32[reset];'
        '[film][reset]xfade=transition=fade:duration=0.5:offset=8.5,trim=duration=9,format=yuv420p[out]'
    )
    run('-i', source, '-i', native,
        '-loop', '1', '-framerate', '24', '-i', ASSETS / 'screen-mask.png',
        '-loop', '1', '-framerate', '24', '-i', ASSETS / 'bezel-web.png',
        '-loop', '1', '-framerate', '24', '-i', ASSETS / 'paper-anchor.png',
        '-loop', '1', '-framerate', '24', '-i', ASSETS / 'guide-screen.png',
        '-loop', '1', '-framerate', '24', '-i', ASSETS / 'screen-mask.png',
        '-loop', '1', '-framerate', '24', '-i', ASSETS / 'bezel-web.png',
        '-loop', '1', '-framerate', '24', '-i', ASSETS / 'print-mask.png',
        '-filter_complex', graph, '-map', '[out]', '-an', '-t', SECONDS,
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-threads', '2',
        '-movflags', '+faststart', output)
    # Keep the static reference's full photographic detail in the no-motion poster.
    run('-i', ASSETS / 'paper-anchor.png', '-ss', '0.5', '-i', installed,
        '-i', ASSETS / 'screen-mask.png', '-i', ASSETS / 'bezel-web.png',
        '-filter_complex', f'[0:v]{normalize}[paper];[1:v]scale=340:738,format=rgb24[ui];'
        '[2:v]format=gray[mask];[ui][mask]alphamerge[screen];'
        '[paper][screen]overlay=385:51[a];[a][3:v]overlay=365:32[out]',
        '-map', '[out]', '-frames:v', '1', '-q:v', '2', output.with_suffix('.jpg'))
    def provenance(path):
        try:
            name = str(path.relative_to(ROOT))
        except ValueError:
            name = 'FondFont/' + str(path.relative_to(args.source.resolve()))
        return {'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    output.with_suffix('.json').write_text(json.dumps({
        'model': 'MiniMax-H3', 'referenceMode': 'Built-in imagegen photographic reference',
        'silent': True, 'sharedAcrossLocales': True, 'seconds': duration(output),
        'sources': [provenance(p) for p in [source, ASSETS / 'paper-reference-source.png',
                    ASSETS / 'paper-anchor.png', ASSETS / 'iphone-bezel.png', guide, settings, installed]],
        'scope': 'The first 0.3 seconds of H3 material motion are retimed and reversed for a restrained paper lift. Exact reference artwork locks the printed body to prevent glyph drift. The Apple bezel and native FondFont/iOS screen recordings fully cover the generated device; no synthetic interface is displayed. Profile Installed is held as the dominant result.',
    }, ensure_ascii=False, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
