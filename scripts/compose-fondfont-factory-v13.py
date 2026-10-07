"""Compose a font foundry → FondFont truck → iOS delivery story over real H3."""
import argparse
from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tempfile
import cairosvg
import numpy as np
from PIL import Image
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'scripts/assets/fondfont/animation/v13'
PUBLIC=ROOT/'public/v/fondfont'
W,H,FPS,SECONDS=1152,720,30,18
spec=importlib.util.spec_from_file_location('fondfont_font_tools',ROOT/'scripts/compose-fondfont-comparison-v11.py')
f=importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
smooth=f.smooth
inter=f.TextFace({'path':'scripts/assets/fondfont/animation/v9/fonts/Inter[opsz,wght].ttf','variation':{'wght':550,'opsz':14}})
sans=f.TextFace({**f.fonts[1],'variation':{'wght':500}})
GLYPHS=f.glyphs
PHRASE='明月松间照'
LOCALE='zh-hans'
BRAND='爱装字体'
MARKETING='喜欢的字体，轻松装进 iOS。'
LABEL_FACE=sans
DISPLAY_RECORD=f.selected
CARGO_SIZE=44
UNIT_CENTERS=[(i+.5)*1000 for i in range(5)]
UNIT_ADVANCE=5000
MARKETING_COPY={
 'en':'Your favorite fonts, installed in iOS.',
 'zh-hans':'喜欢的字体，轻松装进 iOS。',
 'zh-hant':'喜歡的字體，輕鬆裝進 iOS。',
 'ja':'お気に入りのフォントを、iOS へ。',
 'ko':'좋아하는 폰트, iOS에 간편하게.',
 'fr':'Vos polices préférées, installées dans iOS.',
 'de':'Deine Lieblingsschriften. Jetzt in iOS.',
}

def configure_locale(requested):
 global LOCALE,BRAND,MARKETING,LABEL_FACE,DISPLAY_RECORD,PHRASE,GLYPHS,CARGO_SIZE,UNIT_CENTERS,UNIT_ADVANCE
 names=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {FONDFONT_LOCALES} from './src/i18n/fondfont-locales.mjs'; process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(FONDFONT_LOCALES).map(([key,value])=>[key,value.name]))));"],cwd=ROOT))
 (ASSETS/'localized-names.json').write_text(json.dumps(names,ensure_ascii=False,indent=2)+'\n')
 LOCALE=requested if requested in names else 'en'; BRAND=names[LOCALE]; MARKETING=MARKETING_COPY[LOCALE]
 allfonts=json.loads((ROOT/'scripts/assets/fondfont/animation/v9/font-manifest.json').read_text())['locales']
 DISPLAY_RECORD=allfonts[LOCALE][2]
 PHRASE=json.loads((ROOT/'src/i18n/fondfont-poems.json').read_text())[LOCALE][2]['phrase']
 LABEL_FACE=f.TextFace({**allfonts[LOCALE][1],'variation':{'wght':500}}) if LOCALE in ('zh-hans','zh-hant','ja','ko') else inter
 face=f.TextFace(DISPLAY_RECORD)
 buffer=f.hb.Buffer();buffer.add_str(PHRASE);buffer.guess_segment_properties();buffer.language={'zh-hans':'zh-cn','zh-hant':'zh-tw'}.get(LOCALE,LOCALE)
 f.hb.shape(face.hbfont,buffer,{'kern':True,'liga':True})
 cursor=0;GLYPHS=[];UNIT_CENTERS=[];scale=1000/face.units
 for info,pos in zip(buffer.glyph_infos,buffer.glyph_positions):
  if not info.codepoint: raise ValueError('Uncovered poetic glyph')
  glyph=face.glyphset[face.font.getGlyphName(info.codepoint)];pen=SVGPathPen(face.glyphset)
  glyph.draw(TransformPen(pen,(scale,0,0,-scale,(pos.x_offset-pos.x_advance/2)*scale,-pos.y_offset*scale)))
  d=pen.getCommands()
  if d:
   GLYPHS.append(d);UNIT_CENTERS.append((cursor+pos.x_advance/2)*scale)
  cursor+=pos.x_advance
 UNIT_ADVANCE=cursor*scale; CARGO_SIZE=min(44,220/UNIT_ADVANCE*1000)


def batch_centers(center):
 return [center+(x-UNIT_ADVANCE/2)*CARGO_SIZE/1000 for x in UNIT_CENTERS]


def mix(a,b,p): return a+(b-a)*p

def word(value,x,y,size,color='#55534b',anchor='middle',face=inter):
 return f.text(value,x,y,size,color,anchor,face=face)

def type_piece(i,x,baseline,size=None):
 if size is None: size=CARGO_SIZE
 result=[]
 for z in (4,3,2,1):
  result.append(f'<path d="{GLYPHS[i]}" fill="#8a8b80" transform="translate({x+z*.48:.3f} {baseline+z*.54:.3f}) scale({size/1000:.5f})"/>')
 result.append(f'<path d="{GLYPHS[i]}" fill="#3e453b" transform="translate({x:.3f} {baseline:.3f}) scale({size/1000:.5f})"/>')
 return ''.join(result)

def machine(t):
 # Movable platen and flywheel fit the rendered atelier's real press, rather than
 # placing a diagram frame around the glyphs. The complete casting batch is real.
 cycle=2.85/len(GLYPHS)
 active=0<=t<2.85
 phase=(t/cycle)%1 if active else 0
 down=smooth(phase,0,.36)*(1-smooth(phase,.36,.68))
 stroke=25*down
 angle=360*min(t/cycle,len(GLYPHS)) if active else 360*len(GLYPHS)
 content=['<path d="M82 383h254v7H82z" fill="#b8beb5"/><path d="m82 383 5-4h254l-5 4z" fill="#eff0e8"/><path d="M92 390h7v29h-7zM318 390h7v30h-7z" fill="#a9afa5"/>',
  f'<g transform="translate(127 394) rotate({angle:.3f})"><circle r="16" fill="#3e4339" stroke="#a4a895" stroke-width="2"/><path d="M-15 0H15M0-15V15M-11-11 11 11M-11 11 11-11" stroke="#989b87" stroke-width="1.5"/><circle r="3" fill="#c5baa0"/></g>']
 return ''.join(content)


def casting_head(t):
 cycle=2.85/len(GLYPHS)
 phase=(t/cycle)%1 if t<2.85 else 0
 down=smooth(phase,0,.36)*(1-smooth(phase,.36,.68)); y=331+25*down
 return ('<path d="M158 320h6v22h-6z" fill="#969d91"/>'
  f'<path d="M131 {y:.4f}h59v7h-59z" fill="#777e70"/>'
  f'<path d="m131 {y:.4f} 4-3h59l-4 3z" fill="#cbd0c2"/>')


def truck_observation(image):
 image=np.asarray(image.convert('RGB'))
 r,g,b=(image[:,:,i].astype(float) for i in range(3))
 mask=(r>150)&(r>g*1.6)&(g>b*1.1)&((r-b)>75)
 mask[:int(H*.40)]=False; mask[int(H*.73):]=False
 columns=np.flatnonzero(mask.sum(axis=0)>8)
 groups=np.split(columns,np.where(np.diff(columns)>15)[0]+1)
 group=max(groups,key=lambda values:mask[:,values].sum())
 mask[:,:group[0]]=False; mask[:,group[-1]+1:]=False
 ys,xs=np.nonzero(mask)
 if len(xs)<1000: raise RuntimeError('Truck paint could not be observed')
 return [float(np.percentile(xs,.3)),float(np.percentile(ys,.3)),float(np.percentile(xs,99.7)),float(np.percentile(ys,99.7))]


def build_tracking(raw):
 probe=f.probe(raw); duration=float(probe['format']['duration'])
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(raw),'-vf','fps=24,scale=1152:720','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
 frames=np.frombuffer(data,dtype=np.uint8).reshape(-1,H,W,3)
 observations=[truck_observation(Image.fromarray(frame)) for frame in frames]
 anchors=[truck_observation(Image.open(ASSETS/name).resize((W,H),Image.Resampling.LANCZOS)) for name in ('start-anchor.png','end-anchor.png')]
 result={'fps':24,'duration':duration,'frames':observations,'anchors':anchors,'method':'Observed strongest connected terracotta paint bounds in real H3 frames, not hypothetical linear truck motion.'}
 (ASSETS/'truck-observed.json').write_text(json.dumps(result,indent=2)+'\n')
 return result


def pose(t,tracking):
 start,end=tracking['anchors']
 if t<5: return start
 if 8.5<=t<12: return end
 if t>=15.5: return start
 progress=(t-5)/3.5 if t<8.5 else 1-(t-12)/3.5
 progress=max(0,min(1,progress)); n=progress*(len(tracking['frames'])-1)
 a=int(n); b=min(a+1,len(tracking['frames'])-1)
 observed=[mix(x,y,n-a) for x,y in zip(tracking['frames'][a],tracking['frames'][b])]
 if t<8.5:
  fade_in=smooth(t,5,5.15); fade_out=smooth(t,8.5,8.65)
  observed=[mix(x,y,fade_in) for x,y in zip(start,observed)]
  return [mix(x,y,fade_out) for x,y in zip(observed,end)]
 fade_in=smooth(t,12,12.15); fade_out=smooth(t,15.5,15.65)
 observed=[mix(x,y,fade_in) for x,y in zip(end,observed)]
 return [mix(x,y,fade_out) for x,y in zip(observed,start)]


def rig(x,y,width,grip,opacity,receiving=False):
 # A jointed industrial arm supports the pallet from underneath, not a text frame.
 center=x+width/2
 base_x,base_y=(1055,432) if receiving else (341,421)
 elbow_x=1015 if receiving else 373
 elbow_y=313 if receiving else 286
 wrist_y=y+7
 return (f'<g opacity="{opacity:.4f}">'
  f'<path d="M{base_x-11} {base_y-14}h22v18h-22z" fill="#929c93"/>'
  f'<path d="M{base_x} {base_y-11} {elbow_x} {elbow_y} {center:.3f} {wrist_y:.3f}" fill="none" stroke="#afb8ab" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"/>'
  f'<path d="M{base_x-2} {base_y-11} {elbow_x-2} {elbow_y} {center-2:.3f} {wrist_y:.3f}" fill="none" stroke="#e2e5dc" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>'
  f'<circle cx="{elbow_x}" cy="{elbow_y}" r="8" fill="#747e73"/><circle cx="{elbow_x-1}" cy="{elbow_y-1}" r="4" fill="#dce0d1"/>'
  f'<path d="M{x:.3f} {wrist_y:.3f}h{width:.3f}" stroke="#8d9789" stroke-width="4"/>'
  '</g>')


def gate(t):
 opened=smooth(t,8.45,8.9)*(1-smooth(t,11.5,12))
 y=329-112*opened
 # Generated factory bay stays fixed; the native shutter is clipped inside it.
 content='<defs><clipPath id="receive"><rect x="756" y="328" width="249" height="108" rx="12"/></clipPath></defs><g clip-path="url(#receive)">'
 content+=f'<g transform="translate(0 {y:.4f})"><rect x="756" y="0" width="249" height="110" fill="#94988d"/>'
 for n in range(7): content+=f'<path d="M756 {n*17+3}H1005" stroke="#747c70" opacity=".5" stroke-width="1"/>'
 content+='</g></g>'
 return content


def cargo(t,bounds,tracking):
 start=tracking['anchors'][0]
 scale=(bounds[2]-bounds[0])/(start[2]-start[0])
 dx=bounds[0]-start[0]
 dy=bounds[1]-start[1]
 source=batch_centers(208); loaded=batch_centers(361)
 content=[]
 if t<3:
  for index in range(len(GLYPHS)):
   cycle=2.85/len(GLYPHS); order=len(GLYPHS)-1-index; a=order*cycle
   formed=smooth(t,a+cycle*.38,a+cycle*.62)
   if formed<=0: continue
   p=smooth(t,a+cycle*.62,2.95)
   x=mix(160,source[index],p)
   y=mix(389,378,p)
   content.append(f'<g opacity="{formed:.4f}">'+type_piece(index,x,y)+'</g>')
 elif t<5:
  lift=smooth(t,3,3.55); travel=smooth(t,3.4,4.35); lower=smooth(t,4.3,4.85)
  shift=mix(0,153,travel); y=378-72*lift+89*lower
  left=208+shift-121; width=242
  content.append(rig(left,y,width,70,1-smooth(t,4.85,5)))
  content.append(f'<path d="M{left:.3f} {y+2:.3f}h242v5h-242z" fill="#b4b9aa"/>')
  for i in range(len(GLYPHS)): content.append(type_piece(i,source[i]+shift,y))
 elif t<8.9:
  for i in range(len(GLYPHS)): content.append(type_piece(i,start[0]+(loaded[i]-start[0])*scale+dx,start[1]+(395-start[1])*scale+dy,CARGO_SIZE*scale))
 elif t<11.7:
  take=smooth(t,8.9,9.45); delivery=smooth(t,9.3,10.8); lower=smooth(t,10.55,11.15)
  y=395-70*take+105*lower
  target=batch_centers(880)
  left=mix(361+dx,880,delivery)-121
  opacity=1-smooth(t,11.05,11.45)
  content.append(rig(left,y,242,70,opacity,receiving=True))
  content.append(f'<path d="M{left:.3f} {y+2:.3f}h242v5h-242z" fill="#b4b9aa" opacity="{opacity:.4f}"/>')
  for i in range(len(GLYPHS)):
   x=mix(loaded[i]+dx,target[i],delivery)
   content.append(f'<g opacity="{opacity:.4f}">'+type_piece(i,x,y)+'</g>')
 return ''.join(content)


def overlay(t,tracking):
 bounds=pose(t,tracking); start=tracking['anchors'][0]
 scale=(bounds[2]-bounds[0])/(start[2]-start[0])
 dx=bounds[0]-start[0]; dy=bounds[1]-start[1]
 brand_x=start[0]+(370-start[0])*scale+dx
 brand_y=start[1]+(439-start[1])*scale+dy
 content=[machine(t),gate(t),cargo(t,bounds,tracking),casting_head(t)]
 content.append(word('Type Foundry',180,314,24,'#4c5047'))
 content.append(word('iOS',916,267,79,'#5f655a'))
 brand_size=min(36,290/(LABEL_FACE.shape(BRAND)[1]/1000))*scale
 content.append('<g opacity=".92">'+word(BRAND,brand_x,brand_y,brand_size,'#fffaf3',face=LABEL_FACE)+'</g>')
 marketing=smooth(t,12,12.5)*(1-smooth(t,16.2,16.8))
 marketing_size=min(48,1000/(LABEL_FACE.shape(MARKETING)[1]/1000))
 content.append(f'<g opacity="{marketing:.4f}">'+word(MARKETING,576,130,marketing_size,'#373e33',face=LABEL_FACE)+'</g>')
 return '<svg xmlns="http://www.w3.org/2000/svg" width="1152" height="720" viewBox="0 0 1152 720">'+''.join(content)+'</svg>'


def make_plate(tmp):
 raw=ASSETS/'transport-h3.mp4'; duration=float(f.probe(raw)['format']['duration'])
 graph=('[0:v]fps=30,trim=duration=5.15,format=yuv420p[a];[1:v]split[forward][back];'
  f'[forward]setpts={3.5/duration}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=0.3,trim=duration=3.65,format=yuv420p[b];'
  '[2:v]fps=30,trim=duration=3.65,format=yuv420p[c];'
  f'[back]reverse,setpts={3.5/duration}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=0.3,trim=duration=3.65,format=yuv420p[d];'
  '[3:v]fps=30,trim=duration=2.5,format=yuv420p[e];'
  '[a][b]xfade=transition=fade:duration=0.15:offset=5[ab];[ab][c]xfade=transition=fade:duration=0.15:offset=8.5[abc];'
  '[abc][d]xfade=transition=fade:duration=0.15:offset=12[abcd];[abcd][e]xfade=transition=fade:duration=0.15:offset=15.5,scale=1152:720[v]')
 out=tmp/'physical-plate.mp4'
 subprocess.run(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(ASSETS/'start-anchor.png'),'-i',str(raw),'-loop','1','-framerate','30','-i',str(ASSETS/'end-anchor.png'),'-loop','1','-framerate','30','-i',str(ASSETS/'start-anchor.png'),'-filter_complex',graph,'-map','[v]','-t',str(SECONDS),'-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(out)],check=True)
 return out


def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--preview',action='store_true'); p.add_argument('--locale',default='zh-hans'); a=p.parse_args()
 configure_locale(a.locale)
 tracking_file=ASSETS/'truck-observed.json'
 if tracking_file.exists(): tracking=json.loads(tracking_file.read_text())
 elif (ASSETS/'transport-h3.mp4').exists(): tracking=build_tracking(ASSETS/'transport-h3.mp4')
 else:
  anchors=[truck_observation(Image.open(ASSETS/name).resize((W,H),Image.Resampling.LANCZOS)) for name in ('start-anchor.png','end-anchor.png')]
  tracking={'anchors':anchors,'frames':[anchors[0],anchors[1]]}
 if a.preview:
  for t in (0,1.4,2.95,4.0,5.0,8.5,10.3,11.3,13.5,17.5):
   svg=overlay(t,tracking); (ASSETS/f'overlay-{LOCALE}-{t:g}.svg').write_text(svg)
   png=cairosvg.svg2png(bytestring=svg.encode()); (ASSETS/f'overlay-{LOCALE}-{t:g}.png').write_bytes(png)
   import io
   if 5<t<8.5 or 12<t<15.5:
    duration=float(f.probe(ASSETS/'transport-h3.mp4')['format']['duration'])
    progress=(t-5)/3.5 if t<8.5 else 1-(t-12)/3.5
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(progress*duration),'-i',str(ASSETS/'transport-h3.mp4'),'-vf','scale=1152:720','-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    image=Image.open(io.BytesIO(data)).convert('RGBA')
   else:
    image=Image.open(ASSETS/('end-anchor.png' if t>=8.5 and t<12 else 'start-anchor.png')).convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
   image.alpha_composite(Image.open(io.BytesIO(png))); image.convert('RGB').save(ASSETS/f'story-{LOCALE}-{t:g}.png')
  return
 out=PUBLIC/f'concept-factory-{LOCALE}-v13.mp4'
 if out.exists(): p.error('Preserve previous movie; choose a new version.')
 if not tracking_file.exists(): tracking=build_tracking(ASSETS/'transport-h3.mp4')
 with tempfile.TemporaryDirectory(prefix='fondfont-v13-') as temporary:
  tmp=Path(temporary); plate=make_plate(tmp)
  process=subprocess.Popen(['ffmpeg','-v','error','-i',str(plate),'-f','image2pipe','-framerate','30','-vcodec','png','-i','-','-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto[v]','-map','[v]','-t',str(SECONDS),'-an','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
  try:
   for frame in range(FPS*SECONDS): process.stdin.write(cairosvg.svg2png(bytestring=overlay(frame/FPS,tracking).encode()))
   process.stdin.close()
   if process.wait(): raise RuntimeError('Compositing failed')
  except BaseException:
   process.kill(); raise
 subprocess.run(['ffmpeg','-v','error','-i',str(out),'-vf',"select='eq(n,0)+eq(n,45)+eq(n,89)+eq(n,120)+eq(n,195)+eq(n,255)+eq(n,315)+eq(n,345)+eq(n,405)+eq(n,465)+eq(n,510)+eq(n,539)',scale=384:240,tile=4x3",'-frames:v','1',str(ASSETS/f'contact-sheet-{LOCALE}.png')],check=True)
 sources=[ASSETS/name for name in ('start-anchor.png','end-anchor.png','transport-h3.mp4','generation.json','h3-prompt.txt','truck-observed.json')]+[Path(__file__).resolve(),ROOT/DISPLAY_RECORD['path']]
 (ASSETS/f'manifest-{LOCALE}.json').write_text(json.dumps({'engine':'New MiniMax-H3 physical truck journey, full 50 layers / 20 steps / reuse1; native real-font compositing','locale':LOCALE,'truckPaintName':BRAND,'nameSource':'src/i18n/fondfont-locales.mjs','glyphTypeface':DISPLAY_RECORD,'phrase':PHRASE,'copy':MARKETING,'scope':'External Type Foundry manufactures font goods; FondFont transports; iOS receives. Same-device font library in compatible apps; not font generation by FondFont, OS UI replacement or device sync.','timeline':{'cast':[0,3],'gatherAndLoad':[3,5],'loadedTruck':[5,8.5],'unloadIntoIOS':[8.5,12],'marketingAndEmptyTruckReturn':[12,15.5],'reset':[15.5,18]},'probe':f.probe(out),'sources':[{'path':str(s.relative_to(ROOT)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for s in sources],'output':{'path':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}},ensure_ascii=False,indent=2)+'\n')
 print(out,flush=True)

if __name__=='__main__': main()
