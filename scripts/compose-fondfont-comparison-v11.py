"""Compose accurate font actors over H3 footage; render two 12s comparison films."""
import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import cairosvg
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'scripts/assets/fondfont/animation/v11'
PUBLIC = ROOT/'public/v/fondfont'
W, H, FPS, SECONDS = 1152, 720, 30, 12
fonts = json.loads((ROOT/'scripts/assets/fondfont/animation/v9/font-manifest.json').read_text())['locales']['zh-hans']
selected = fonts[2]
poem = json.loads((ROOT/'src/i18n/fondfont-poems.json').read_text())['zh-hans'][2]
font = TTFont(ROOT/selected['path'])
glyphset = font.getGlyphSet()
factor = 1000/font['head'].unitsPerEm
glyphs = []
for c in poem['phrase']:
 pen = SVGPathPen(glyphset)
 glyphset[font.getBestCmap()[ord(c)]].draw(TransformPen(pen,(factor,0,0,-factor,-500,0)))
 glyphs.append(pen.getCommands())

class TextFace:
 def __init__(self, record):
  self.path = ROOT/record['path']
  self.font = TTFont(self.path)
  self.axes = record.get('variation') or {}
  self.glyphset = self.font.getGlyphSet(location=self.axes)
  self.units = self.font['head'].unitsPerEm
  self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(str(self.path))))
  self.hbfont.scale = (self.units,self.units)
  self.hbfont.set_variations(self.axes)

 @lru_cache(maxsize=None)
 def shape(self, value):
  if any(ord(c) not in self.font.getBestCmap() for c in value): raise ValueError(value)
  b = hb.Buffer(); b.add_str(value); b.guess_segment_properties(); b.language='zh-cn'
  hb.shape(self.hbfont,b,{'kern':True,'liga':True})
  pen = SVGPathPen(self.glyphset); x=0; s=1000/self.units
  for info,pos in zip(b.glyph_infos,b.glyph_positions):
   if not info.codepoint: raise ValueError('Unexpected .notdef')
   g=self.glyphset[self.font.getGlyphName(info.codepoint)]
   g.draw(TransformPen(pen,(s,0,0,-s,(x+pos.x_offset)*s,-pos.y_offset*s)))
   x += pos.x_advance
  return pen.getCommands(),x*s

sans, display = TextFace(fonts[1]), TextFace(selected)

def text(value,x,y,size=20,color='#66685f',anchor='start',face=None):
 d, advance=(face or sans).shape(value)
 offset = advance*size/1000*(.5 if anchor=='middle' else 1 if anchor=='end' else 0)
 return f'<path d="{d}" fill="{color}" transform="translate({x-offset:.3f} {y}) scale({size/1000})"/>'

def phrase(x,y,width,height,color='#242720'):
 return f'<svg x="{x}" y="{y}" width="{width}" height="{height}" viewBox="{poem["viewBox"]}" preserveAspectRatio="xMidYMid meet"><path d="{poem["d"]}" fill="{color}"/></svg>'

def smooth(t,a,b):
 q=max(0,min(1,(t-a)/(b-a)))
 return q*q*(3-2*q)

def actor(i,t,variant):
 p=smooth(t,6.3,8.5)
 x0=300+140*i
 x1=240+168*i
 base0=[548,550,528,519,544][i] if variant=='playground' else 521
 x=x0+(x1-x0)*p
 y=base0+(327-base0)*p
 scale=.145+(.123-.145)*p
 angle=0; bounce=0
 if variant=='playground' and t<6.3:
  if i<4:
   angle=52*smooth(t,1.05+i*.32,1.35+i*.32)
   recovery=smooth(t,4.20+(3-i)*.20,4.6+(3-i)*.20)
   angle*=1-recovery
   dt=t-(4.6+(3-i)*.20)
   if 0<dt<1.2: angle+=-8*math.sin(dt*16)*math.exp(-dt*3)
  else:
   angle=-13*smooth(t,2.35,2.62)*(1-smooth(t,3.8,4.25))
   bounce=-13*math.sin(math.pi*smooth(t,3.65,4.15))
 color='#ad543a' if variant=='playground' else '#383e32'
 result=[]
 if variant=='playground':
  # Native shape extrusions: copies of the identical real glyph, no deformation.
  for depth in range(8,0,-2):
   result.append(f'<g transform="translate({x+depth*.35:.3f} {y+bounce+depth*.6:.3f}) rotate({angle:.3f}) scale({scale})"><path d="{glyphs[i]}" fill="#743d2c" opacity=".65"/></g>')
  result.append(f'<ellipse cx="{x+angle*.6:.2f}" cy="{base0+11+(346-base0)*p:.2f}" rx="53" ry="4" fill="#46412f" opacity="{.055*(1-p):.3f}"/>')
 elif t<6.3:
  # Letterforms already exist. Illumination changes their ink, not their shape.
  glow=smooth(t,1+i*.58,1.85+i*.58)
  shade=round(115+(42-115)*glow)
  color=f'rgb({shade},{shade+5},{shade-5})'
 result.append(f'<g transform="translate({x:.3f} {y+bounce:.3f}) rotate({angle:.3f}) scale({scale})"><path d="{glyphs[i]}" fill="{color}"/></g>')
 return ''.join(result)

def overlay(t,variant):
 p=smooth(t,6.3,8.5)
 app=smooth(t,8.1,8.9)
 ink='#ad543a' if variant=='playground' else '#383e32'
 content=[f'<rect width="{W}" height="{H}" fill="#f8f8f6" opacity="{p*.95:.4f}"/>']
 content.append(text('FondFont',48,55,24,'#55564d'))
 content.append(''.join(actor(i,t,variant) for i in range(5)))
 content.append(f'<g opacity="{1-p:.4f}">'+text('王维 · 山居秋暝',576,648,18,'#8b897f','middle')+'</g>')
 content.append(f'<g opacity="{app:.4f}">')
 content.append(text('iOS 字体库 · 已安装',576,397,24,'#373b33','middle'))
 content.append('<path d="m389 384 6 6 12-14" fill="none" stroke="#bd6d50" stroke-width="2" stroke-linecap="round"/>')
 label_width=sans.shape(selected['label'])[1]*18/1000
 label_x=576-(label_width+65)/2
 badge_x=label_x+label_width+14
 content.append(text(selected['label'],label_x,431,18,'#74756c'))
 content.append(f'<rect x="{badge_x}" y="410" width="51" height="28" rx="5" fill="none" stroke="#d7d7cf"/>'+text('TTF',badge_x+25.5,430,16,'#74756c','middle'))
 # App layouts are conceptual compositions, not fabricated native screenshots.
 content.append('<rect x="171" y="464" width="360" height="160" rx="5" fill="#fdfdfb" stroke="#dfdfd6"/><rect x="621" y="464" width="360" height="160" rx="5" fill="#fdfdfb" stroke="#dfdfd6"/>')
 content.append(text('Pages',193,494,18,'#7a7c70')+text('Keynote',643,494,18,'#7a7c70'))
 content.append(phrase(195,512,311,46,ink))
 content.append(text('清泉石上流',202,599,39,ink,face=display))
 content.append(phrase(647,526,310,58,ink))
 content.append(text('安装一次，多个兼容 App 可用',576,668,25,'#55594f','middle'))
 content.append('</g>')
 return '<svg xmlns="http://www.w3.org/2000/svg" width="1152" height="720" viewBox="0 0 1152 720">'+''.join(content)+'</svg>'

def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('variant',choices=['playground','poetry'])
 parser.add_argument('--preview',action='store_true',help='Render original SVG stills without waiting for H3')
 args=parser.parse_args(); folder=ASSETS/args.variant
 if args.preview:
  for t in [0,2.8,4.7,9.8]:
   svg=overlay(t,args.variant)
   (folder/f'overlay-brush-{t:g}.svg').write_text(svg)
   cairosvg.svg2png(bytestring=svg.encode(),write_to=str(folder/f'overlay-brush-{t:g}.png'))
  return
 out=PUBLIC/f'concept-{args.variant}-brush-v11.mp4'
 if out.exists(): raise RuntimeError('Preserve exports; choose a new version.')
 raw=probe(folder/'scene-h3.mp4'); duration=float(raw['format']['duration'])
 with tempfile.TemporaryDirectory(prefix=f'fondfont-v11-{args.variant}-') as temp:
  temp=Path(temp); plate=temp/'plate.mp4'; film=temp/'film.mp4'
  graph=('[0:v]fps=30,trim=duration=0.5,format=yuv420p[a];'
   f'[1:v]setpts={6/duration}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=0.2,trim=duration=6,format=yuv420p[b];'
   '[2:v]fps=30,trim=duration=5.95,format=yuv420p[c];'
   '[a][b]xfade=transition=fade:duration=0.15:offset=0.35[ab];'
   '[ab][c]xfade=transition=fade:duration=0.25:offset=6.10,scale=1152:720[v]')
  subprocess.run(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(folder/'start-anchor.png'),'-i',str(folder/'scene-h3.mp4'),'-loop','1','-framerate','30','-i',str(folder/'end-anchor.png'),'-filter_complex',graph,'-map','[v]','-t','12','-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(plate)],check=True)
  command=['ffmpeg','-v','error','-i',str(plate),'-f','image2pipe','-framerate','30','-vcodec','png','-i','-', '-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto[v]','-map','[v]','-t','12','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(film)]
  process=subprocess.Popen(command,stdin=subprocess.PIPE)
  try:
   for frame in range(FPS*SECONDS):
    svg=overlay(frame/FPS,args.variant)
    process.stdin.write(cairosvg.svg2png(bytestring=svg.encode()))
   process.stdin.close()
   if process.wait(): raise RuntimeError('Compositing failed')
  except BaseException:
   process.kill(); raise
  graph='[0:v]split[full][first];[first]trim=end_frame=1,loop=loop=-1:size=1:start=0,setpts=N/(30*TB),trim=duration=0.5[reset];[full][reset]xfade=transition=fade:duration=0.4:offset=11.5[v]'
  subprocess.run(['ffmpeg','-v','error','-i',str(film),'-filter_complex',graph,'-map','[v]','-t','12','-an','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
  subprocess.run(['ffmpeg','-v','error','-ss','9.8','-i',str(out),'-frames:v','1',str(folder/'shared-result-brush.png')],check=True)
  subprocess.run(['ffmpeg','-v','error','-i',str(out),'-vf','fps=1/2,scale=384:240,tile=3x2','-frames:v','1',str(folder/'contact-sheet-brush.png')],check=True)
 sources=[folder/n for n in ['start-reference.png','end-reference.png','start-anchor.png','end-anchor.png','h3-prompt.txt','scene-h3.mp4','generation.json']]
 (folder/'manifest-brush.json').write_text(json.dumps({'kind':'Original H3 physical scene with exact native-outline compositing','engine':'MiniMax-H3','font':selected,'poem':'明月松间照','source':'王维 · 山居秋暝','sameTypeface':'MaShanZheng-Regular.ttf in central specimen, Pages body and Keynote title. Label outlines are separately shaped from NotoSansSC.','scope':'Conceptual typography/app compositions, same-device iOS shared font library in compatible apps; not native UI footage.','timeline':{'physicalStory':[0,6.3],'settleAndInstall':[6.3,8.9],'simultaneousCompatibleApps':[8.9,11.5],'wholeSceneLoopReset':[11.5,12]},'probe':probe(out),'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'output':{'path':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}},ensure_ascii=False,indent=2)+'\n')
 print(out,flush=True)

if __name__=='__main__': main()
