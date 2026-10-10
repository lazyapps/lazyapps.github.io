"""Compose local H3 cinematography, exact shaped typography and real YiYan UI.

The English example is transcribed from the existing, authentic localized
learning-record screenshots. No app controls or translation results are invented.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v2'
PUBLIC = ROOT / 'public/v/yiyan'
W, H, FPS, SECONDS = 1280, 720, 24, 25
INK = (42, 37, 33)
MUTED = (105, 89, 77)
ACCENT = (176, 66, 39)
PAPER = (250, 245, 237)
COPY_PATH = ROOT / 'src/i18n/yiyan-video-copy.json'
COPY = json.loads(COPY_PATH.read_text())


def run(command):
    subprocess.run([str(s) for s in command], check=True)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def smooth(x):
    x = max(0, min(1, x))
    return x * x * (3 - 2 * x)


def text_config():
    entries = []
    for locale, c in COPY.items():
        def add(key, text, width, height, size, color=INK, bold=False, center=False, english=False):
            entries.append(dict(file=f'{locale}-{key}.png', text=text, width=width, height=height,
                                size=size, color=[n / 255 for n in color], bold=bold,
                                align='center' if center else 'left', rtl=locale == 'ar' and not english))
        add('brand', c['brand'], 360, 54, 32, bold=True, english=True)
        add('hook', c['hook'], 490, 212, 64, bold=True)
        add('intro', c['intro'], 482, 116, 30, MUTED)
        add('hosts', 'Pi · Claude Code · Codex · OpenCode · Antigravity', 1130, 40, 23, MUTED, english=True)
        add('alongside', c['alongside'], 940, 46, 26, ACCENT)
        add('example', c['example'], 1140, 90, 46, bold=True)
        add('original-label', c['original'], 1080, 44, 26, MUTED)
        add('original', 'avoid unnecessary decorations etc.', 1080, 78, 48, MUTED, english=True)
        add('natural-label', c['natural'], 1080, 44, 26, ACCENT)
        add('natural', 'Avoid unnecessary decorative elements.', 1080, 82, 50, bold=True, english=True)
        add('real', c['real'], 960, 40, 24, MUTED)
        add('proof', c['proof'], 1140, 72, 42, bold=True)
        add('collection', c['collection'], 490, 220, 59, bold=True)
        add('reuse', c['reuse'], 486, 104, 30, MUTED)
        add('phrase', 'decorative elements', 430, 62, 36, ACCENT, bold=True, english=True)
        add('close-brand', c['brand'], 680, 118, 88, bold=True, center=True)
        add('closing', c['closing'], 1130, 150, 45, bold=True, center=True)
        add('local', c['local'], 1120, 48, 26, MUTED, center=True)
        add('assistant', c['assistant'], 1120, 48, 26, MUTED, center=True)
        add('url', 'lazyapps.com/yiyan', 1120, 42, 25, ACCENT, center=True, english=True)
    config = ASSETS / 'text-config.json'
    config.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n')
    run([ASSETS / 'render-text', config, ASSETS / 'text'])


def make_plates():
    for scene in ['prompt-notebook', 'phrase-collection']:
        raw = ASSETS / f'{scene}-h3.mp4'
        output = ASSETS / f'{scene}-plate.mp4'
        if output.exists():
            continue
        duration = float(probe(raw)['format']['duration'])
        run(['ffmpeg', '-v', 'error', '-i', raw, '-an', '-vf',
             f'setpts={5 / duration}*(PTS-STARTPTS),scale={W}:{H}:flags=lanczos,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=1,trim=duration=5,setpts=PTS-STARTPTS',
             '-t', '5', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', output])


def read_plate(path):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    frames = np.frombuffer(data, dtype=np.uint8).reshape(-1, H, W, 3)
    return frames


class Film:
    def __init__(self, locale, plates=None, preview=False):
        self.locale = locale
        self.plates = plates
        self.preview = preview
        self.layers = {}
        for path in (ASSETS / 'text').glob(f'{locale}-*.png'):
            key = path.name[len(locale) + 1:-4]
            layer = Image.open(path).convert('RGBA')
            entry = next(e for e in json.loads((ASSETS/'text-config.json').read_text()) if e['file'] == path.name)
            if layer.size != (entry['width'], entry['height']):
                layer = layer.resize((entry['width'], entry['height']), Image.Resampling.LANCZOS)
            self.layers[key] = layer
        self.icon = Image.open(ROOT / 'src/assets/img/yiyan-icon.png').convert('RGBA')
        source = ROOT / ('src/assets/img/yiyan-showcase.png' if locale == 'zh-hans' else f'src/assets/img/yiyan/{locale}/yiyan-showcase.png')
        self.screenshot_path = source
        self.screenshot = Image.open(source).convert('RGB').crop((32, 448, 1160, 938))
        self.anchors = [Image.open(ASSETS/f'{scene}-anchor.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
                        for scene in ['prompt-notebook','phrase-collection']]

    def layer(self, canvas, key, xy, alpha=1, lift=0):
        if alpha <= 0:
            return
        im = self.layers[key]
        if alpha < 1:
            im = im.copy()
            im.putalpha(im.getchannel('A').point(lambda n: round(n * alpha)))
        canvas.paste(im, (round(xy[0]), round(xy[1] + lift)), im)

    def brand(self, canvas):
        im = self.icon.resize((42,42),Image.Resampling.LANCZOS)
        canvas.paste(im,(62,52),im)
        self.layer(canvas,'brand',(118,45))

    def paper(self, index, t):
        if self.plates is None:
            return self.anchors[index].copy()
        f = min(len(self.plates[index])-1, max(0,round(t*FPS)))
        return Image.fromarray(self.plates[index][f]).copy()

    def scene(self, index, t):
        if index == 0:
            im = self.paper(0,t)
            self.brand(im)
            # Opening is useful as a standalone poster; no blank intro frame.
            self.layer(im,'hook',(62,185))
            self.layer(im,'intro',(62,416))
            self.layer(im,'hosts',(62,625))
        elif index == 1:
            im=Image.new('RGB',(W,H),PAPER)
            d=ImageDraw.Draw(im)
            self.brand(im)
            self.layer(im,'example',(62,130))
            self.layer(im,'original-label',(80,252))
            self.layer(im,'original',(80,302))
            d.line((80,404,1200,404),fill=(217,199,183),width=2)
            # Original work stays intact. The learning version arrives later.
            self.layer(im,'alongside',(80,613))
            a=smooth((t-.85)/.65)
            d.rounded_rectangle((62,434,1218,578),radius=18,fill=(255,253,249))
            self.layer(im,'natural-label',(80,439),a,14*(1-a))
            self.layer(im,'natural',(80,487),a,14*(1-a))
            d.line((80,570,1198,570),fill=ACCENT,width=3)
        elif index == 2:
            im=Image.new('RGB',(W,H),PAPER)
            self.brand(im)
            self.layer(im,'real',(62,108))
            self.layer(im,'proof',(62,151))
            # Authentic lower learning-record card, without date or unrelated record.
            width=1077
            height=468
            shot=self.screenshot.resize((width,height),Image.Resampling.LANCZOS)
            im.paste(shot,(101,220))
        elif index == 3:
            im=self.paper(1,t)
            self.brand(im)
            self.layer(im,'collection',(62,185))
            self.layer(im,'reuse',(62,430))
            d=ImageDraw.Draw(im)
            d.rounded_rectangle((62,560,510,632),radius=18,fill=(255,249,238))
            self.layer(im,'phrase',(78,564))
        else:
            im=Image.new('RGB',(W,H),PAPER)
            icon=self.icon.resize((86,86),Image.Resampling.LANCZOS)
            im.paste(icon,(597,78),icon)
            self.layer(im,'close-brand',(300,184))
            self.layer(im,'closing',(75,325))
            self.layer(im,'local',(80,499))
            self.layer(im,'assistant',(80,547))
            self.layer(im,'url',(80,624))
        return im

    def frame(self,t):
        starts=[0,5,11,16,21]
        index=max(i for i,s in enumerate(starts) if t>=s)
        local=t-starts[index]
        im=self.scene(index,local)
        # Short whole-scene dissolves preserve reading time and never reverse H3 motion.
        if index and local<.3:
            previous=self.scene(index-1,starts[index]-starts[index-1]-.01)
            im=Image.blend(previous,im,smooth(local/.3))
        d=ImageDraw.Draw(im)
        d.rectangle((62,697,1218,700),fill=(226,212,196))
        d.rectangle((62,697,62+round(1156*min(t/SECONDS,1)),700),fill=ACCENT)
        return im


def export(locale, plates):
    film=Film(locale,plates)
    output=PUBLIC/f'hero-{locale}-v2.mp4'
    if output.exists():
        raise RuntimeError(f'Preserve previous exports: {output}')
    process=subprocess.Popen(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-framerate',str(FPS),'-i','-',
                              '-an','-c:v','libx264','-preset','slow','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',
                              '-metadata','title=YiYan — everyday words, useful English',
                              '-metadata','comment=Original AI-generated paper motion from local MiniMax H3; exact typography and authentic app screenshot compositing.',str(output)],stdin=subprocess.PIPE)
    try:
        for frame in range(FPS*SECONDS):
            process.stdin.write(film.frame(frame/FPS).tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError('FFmpeg export failed')
    except BaseException:
        process.kill()
        raise
    poster=PUBLIC/f'hero-{locale}-v2.jpg'
    film.frame(.8).save(poster,quality=90,optimize=True)
    sources=[ASSETS/f'{s}-h3.mp4' for s in ['prompt-notebook','phrase-collection']]+[film.screenshot_path,COPY_PATH,Path(__file__),ROOT/'scripts/render-yiyan-text.swift']
    manifest=dict(model='MiniMax-H3',mode='local generation + native editorial compositing',locale=locale,
                  dimensions=[W,H],fps=FPS,seconds=SECONDS,silent=True,
                  timeline={'H3_prompt_notebook':[0,5],'exact_example':[5,11],'authentic_record':[11,16],'H3_phrase_collection':[16,21],'brand_local_default':[21,25]},
                  example={'original':'avoid unnecessary decorations etc.','natural':'Avoid unnecessary decorative elements.','source':str(film.screenshot_path.relative_to(ROOT))},
                  sources=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
                  outputs=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [output,poster]],probe=probe(output))
    (ASSETS/f'manifest-{locale}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(output,flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--locale',choices=COPY)
    p.add_argument('--text-only',action='store_true')
    p.add_argument('--review-frames',action='store_true')
    args=p.parse_args()
    if args.text_only or not (ASSETS/'text').exists():
        text_config()
    if args.text_only:
        return
    if args.review_frames:
        folder=ROOT/'docs/reviews/yiyan-video-20261008/frames'
        folder.mkdir(exist_ok=True)
        for locale in [args.locale] if args.locale else COPY:
            film=Film(locale)
            for t in [.8,8,13,18,23]:
                film.frame(t).save(folder/f'{locale}-{t}.jpg',quality=92)
        return
    make_plates()
    plates=[read_plate(ASSETS/f'{scene}-plate.mp4') for scene in ['prompt-notebook','phrase-collection']]
    for locale in [args.locale] if args.locale else COPY:
        export(locale,plates)

if __name__=='__main__':
    main()
