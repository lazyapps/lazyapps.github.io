"""Compose H3 motion with real iOS installation evidence, then export web assets."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v2'
TARGET = ROOT / 'public/v/fondfont'
SCREEN = (196,67,294,640)


def run(*args):
    subprocess.run(['ffmpeg','-v','error','-n',*map(str,args)],check=True)


def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries',
        'format=duration','-of','default=nw=1:nk=1',str(path)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path,help='FondFont app repository')
    parser.add_argument('--scene',required=True,choices=['hero','paper'])
    args = parser.parse_args()
    TARGET.mkdir(parents=True,exist_ok=True)
    source = ASSETS / f'{args.scene}-h3.mp4'
    output = TARGET / f'{args.scene}-h3-v2.mp4'
    if output.exists():
        parser.error('Preserve existing exports; use a new version.')
    source_files = [source]
    if args.scene == 'paper':
        loop_start = ASSETS / 'paper-loop-start-toned.png'
        tone = "lutrgb=r='max(0,255-(255-val)*2)':g='max(0,255-(255-val)*2)':b='max(0,255-(255-val)*2)'"
        run('-i',source,'-vf',tone,'-frames:v','1',loop_start)
        run('-i',source,'-loop','1','-framerate','24','-i',loop_start,
            '-filter_complex',f'[0:v]setpts={12 / duration(source)}*(PTS-STARTPTS),fps=24,scale=768:960,{tone},format=yuv420p[p];'
            '[1:v]format=yuv420p[r];[p][r]xfade=transition=fade:duration=0.75:offset=11.25,trim=duration=12[out]',
            '-map','[out]','-t','12','-an','-c:v','libx264','-preset','slow','-crf','25','-threads','2',
            '-movflags','+faststart',output)
        run('-i',output,'-frames:v','1',output.with_suffix('.jpg'))
    else:
        footage = args.source.resolve() / 'AppStore/Preview/Remotion/public/v8-footage'
        settings, installed = [footage / name for name in ['c3-ios-install.mp4','c4-installed.mp4']]
        source_files += [ASSETS / 'guide-screen.png', settings, installed]
        native = ASSETS / 'native-install-sequence.mkv'
        run('-loop','1','-framerate','24','-i',ASSETS / 'guide-screen.png',
            '-i',settings,'-i',installed,'-filter_complex',
            '[0:v]scale=294:640,fps=24,trim=duration=0.8,setpts=PTS-STARTPTS,setsar=1[g];'
            '[1:v]trim=start=3.2,setpts=PTS-STARTPTS,scale=294:640,fps=24,setsar=1[s];'
            '[2:v]scale=294:640,fps=24,tpad=stop_mode=clone:stop_duration=6,trim=duration=6,setpts=PTS-STARTPTS,setsar=1[d];'
            '[g][s][d]concat=n=3:v=1:a=0,trim=duration=8.5,format=rgba[n]',
            '-map','[n]','-an','-t','8.5','-c:v','ffv1','-threads','2',native)
        mask = Image.new('L',(294,640),0)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,293,639),radius=24,fill=255)
        mask.save(ASSETS / 'screen-mask.png')
        with Image.open(ASSETS / 'hero-end.png') as image:
            image.crop((171,40,515,792)).save(ASSETS / 'fixed-device.png')
        # Normalize only the illustrated field to white; actual screen pixels are preserved.
        normalize = "lutrgb=r='min(255,val*255/248)':g='min(255,val*255/248)':b='min(255,val*255/246)'"
        graph = (
            f'[0:v]setpts=PTS-STARTPTS,fps=24,{normalize},format=yuv420p,'
            f'tpad=stop_mode=clone:stop_duration={8.5-duration(source)},trim=duration=8.5[movingArt];'
            f'[6:v]{normalize},format=rgba[fixedDevice];'
            '[movingArt][fixedDevice]overlay=x=171:y=40[art];'
            '[1:v]format=rgb24[native];[2:v]format=gray[mask];[native][mask]alphamerge[screen];'
            '[art][screen]overlay=x=196:y=67:shortest=1[film];'
            f'[3:v]{normalize},format=rgba[resetArt];'
            '[4:v]scale=294:640,format=rgb24[resetScreen];'
            '[5:v]format=gray[resetMask];[resetScreen][resetMask]alphamerge[resetUI];'
            '[resetArt][resetUI]overlay=x=196:y=67[reset];'
            '[film][reset]xfade=transition=fade:duration=0.5:offset=8,trim=duration=8.5,format=yuv420p[out]'
        )
        run('-i',source,'-i',native,'-loop','1','-framerate','24','-i',ASSETS / 'screen-mask.png',
            '-loop','1','-framerate','24','-i',ASSETS / 'hero-start.png',
            '-loop','1','-framerate','24','-i',ASSETS / 'guide-screen.png',
            '-loop','1','-framerate','24','-i',ASSETS / 'screen-mask.png',
            '-loop','1','-framerate','24','-i',ASSETS / 'fixed-device.png',
            '-filter_complex',graph,'-map','[out]','-an','-t','8.5','-c:v','libx264',
            '-preset','slow','-crf','21','-threads','2','-movflags','+faststart',output)
        run('-ss','5.5','-i',output,'-frames:v','1',output.with_suffix('.jpg'))
    def provenance(path):
        try:
            name = str(path.relative_to(ROOT))
        except ValueError:
            name = 'FondFont/' + str(path.relative_to(args.source.resolve()))
        return {'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    output.with_suffix('.json').write_text(json.dumps({
        'model':'MiniMax-H3','scene':args.scene,'sharedAcrossLocales':True,'silent':True,
        'seconds':duration(output),'sources':[provenance(path) for path in source_files],
        'scope':('New H3 font-file handoff and paper specimens; authentic English FondFont guide and iOS Settings installation/confirmation recordings composited in the fixed screen. Specimens are illustrations, not external-app recordings.'
                 if args.scene == 'hero' else 'New H3 cotton-paper illumination and typographic relief, retimed for a gentle page-wide loop.'),
    },ensure_ascii=False,indent=2)+'\n')
    print(output)


if __name__ == '__main__':
    main()
