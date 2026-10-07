"""Prepare pale paper H3 anchors and authentic installation screen layers."""
import argparse
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v2'
FONT = ASSETS.parent / 'BebasNeue-Regular.ttf'


def hero(completed):
    scale = 2
    image = Image.new('RGB', (704 * scale, 832 * scale), '#f8f8f6')
    draw = ImageDraw.Draw(image)

    def panel(box, radius=8, fill='#fdfcf7'):
        shadow = Image.new('RGBA', image.size)
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(tuple(n * scale for n in (box[0]+4,box[1]+8,box[2]+4,box[3]+8)),
                             radius=radius * scale, fill=(75, 61, 48, 32))
        image.paste(shadow.filter(ImageFilter.GaussianBlur(12 * scale)), (0,0),
                    shadow.filter(ImageFilter.GaussianBlur(12 * scale)))
        draw.rounded_rectangle(tuple(n * scale for n in box), radius=radius * scale,
                               fill=fill, outline='#e8e4db', width=scale)

    def text(pos, value, size, fill='#262525'):
        draw.text(tuple(n * scale for n in pos), value,
                  font=ImageFont.truetype(str(FONT), size * scale), fill=fill, anchor='mm')

    # These are original typography specimens, not fabricated app screens.
    panel((478, 116, 666, 357))
    if completed:
        text((572, 190), 'Aa', 80)
    for y, right in [(257,638),(270,628),(283,638),(296,606),(320,638)]:
        draw.line([(503*scale,y*scale),(right*scale,y*scale)],fill='#c7c5bd',width=2*scale)
    panel((468, 550, 680, 720))
    if completed:
        text((574, 615), 'Aa', 76)
    draw.line([(494*scale,680*scale),(543*scale,680*scale)],fill='#c83f2a',width=3*scale)
    draw.line([(552*scale,680*scale),(651*scale,680*scale)],fill='#c7c5bd',width=3*scale)

    # The iPhone and its entire screen stay fixed for deterministic real footage.
    panel((173, 42, 513, 790), 46, '#efede6')
    draw.rounded_rectangle((182*scale,53*scale,504*scale,779*scale),radius=38*scale,
                           fill='#faf9f4',outline='#d9d4ca',width=scale)
    draw.rounded_rectangle((196*scale,67*scale,490*scale,706*scale),radius=24*scale,
                           fill='#f7f5ee')
    # Exact native symbol, outside the real screen, identifies the tool.
    icon = Image.open(ROOT / 'src/assets/img/fondfont-icon.png').convert('RGBA')
    icon.thumbnail((48*scale,48*scale),Image.Resampling.LANCZOS)
    image.paste(icon,(319*scale,721*scale),icon)
    if not completed:
        panel((16, 300, 161, 495), 7)
        text((89, 373), 'Aa', 94)
        text((89, 457), '.ttf', 25, '#a59d90')
    return image.resize((704,832),Image.Resampling.LANCZOS)


def paper():
    image = Image.new('RGB',(768,960),'#f8f8f6')
    relief = Image.new('RGBA',image.size)
    d = ImageDraw.Draw(relief)
    font = ImageFont.truetype(str(FONT),800)
    d.text((-190,245),'A',font=font,fill=(132,119,103,30))
    d.text((525,-190),'g',font=font,fill=(163,148,126,24))
    relief = relief.filter(ImageFilter.GaussianBlur(28))
    image.paste(relief,(0,0),relief)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output-directory',type=Path,default=ASSETS)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    for name, image in [('hero-start.png',hero(False)),('hero-end.png',hero(True)),('paper-anchor.png',paper())]:
        target = args.output_directory / name
        if target.exists():
            raise FileExistsError(target)
        image.save(target)
    footage = args.source.resolve() / 'AppStore/Preview/Remotion/public/v8-footage'
    for name, clip, time in [('guide-screen.png','c2-sheet.mp4','0.1'),('installed-screen.png','c4-installed.mp4','0')]:
        subprocess.run(['ffmpeg','-v','error','-n','-ss',time,'-i',str(footage / clip),
                        '-frames:v','1',str(args.output_directory / name)],check=True)


if __name__ == '__main__':
    main()
