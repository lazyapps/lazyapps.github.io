"""Compose a font foundry → FondFont truck → iOS delivery story over real H3."""
import argparse
import base64
import hashlib
import importlib.util
import json
import math
from functools import lru_cache
from pathlib import Path
import subprocess
import tempfile
import cairosvg
import numpy as np
from PIL import Image
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'scripts/assets/fondfont/animation/v15'
PAINT=ROOT/'scripts/assets/fondfont/animation/v14/paint'
PHYSICAL=ROOT/'scripts/assets/fondfont/animation/v13'
PUBLIC=ROOT/'public/v/fondfont'
W,H,FPS,SECONDS=1152,720,30,18
spec=importlib.util.spec_from_file_location('fondfont_font_tools',ROOT/'scripts/compose-fondfont-comparison-v11.py')
f=importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
smooth=f.smooth
inter=f.TextFace({'path':'scripts/assets/fondfont/animation/v9/fonts/Inter[opsz,wght].ttf','variation':{'wght':550,'opsz':14}})
sans=f.TextFace({**f.fonts[1],'variation':{'wght':500}})
GLYPHS=[]
LOCALE='zh-hans'
BRAND='爱装字体'
MARKETING='喜欢的字体，轻松装进 iOS。'
LABEL_FACE=sans
CARGO_SIZE=44
MARKETING_COPY={
 'en':'Your favorite fonts, installed in iOS.',
 'zh-hans':'喜欢的字体，轻松装进 iOS。',
 'zh-hant':'喜歡的字體，輕鬆裝進 iOS。',
 'ja':'お気に入りのフォントを、iOS へ。',
 'ko':'좋아하는 폰트, iOS에 간편하게.',
 'fr':'Vos polices préférées, installées dans iOS.',
 'de':'Deine Lieblingsschriften. Jetzt in iOS.',
}

# Cargo is the same multilingual batch in every locale. Only paint and wording localize.
CARGO=[]
PAINT_IMAGE=''
PAINT_PATH=None

def configure_locale(requested):
 global LOCALE,BRAND,MARKETING,LABEL_FACE,CARGO,GLYPHS,PAINT_IMAGE,PAINT_PATH
 names=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {FONDFONT_LOCALES} from './src/i18n/fondfont-locales.mjs'; process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(FONDFONT_LOCALES).map(([key,value])=>[key,value.name]))));"],cwd=ROOT))
 (ASSETS/'localized-names.json').write_text(json.dumps(names,ensure_ascii=False,indent=2)+'\n')
 LOCALE=requested if requested in names else 'en'; BRAND=names[LOCALE]; MARKETING=MARKETING_COPY[LOCALE]
 fonts=json.loads((ROOT/'scripts/assets/fondfont/animation/v9/font-manifest.json').read_text())['locales']
 LABEL_FACE=f.TextFace({**fonts[LOCALE][1],'variation':{'wght':500}}) if LOCALE in ('zh-hans','zh-hant','ja','ko') else inter
 paint_locale=LOCALE if LOCALE in ('zh-hans','zh-hant','ja','ko') else 'en'
 PAINT_PATH=PAINT/f'paint-fleet-{paint_locale}.png'
 PAINT_IMAGE='data:image/png;base64,'+base64.b64encode(PAINT_PATH.read_bytes()).decode()
 choices=[('明','zh-hans',2),('g','en',2),('あ','ja',2),('ß','de',0),('달','ko',2),('愛','zh-hant',2),('Ω','en',1),('永','zh-hans',0),('&','en',2),('Ж','en',1),('꽃','ko',2),('海','ja',2)]
 positions=[(-92,0,39,-7),(-47,-1,43,5),(0,0,39,-4),(47,-1,42,9),(93,-2,38,-8),(-74,-33,41,-10),(-25,-34,39,7),(23,-34,43,-5),(72,-33,39,12),(-48,-65,40,-8),(0,-64,42,9),(48,-65,39,-6)]
 CARGO=[];GLYPHS=[]
 for (char,language,index),(x,y,size,angle) in zip(choices,positions):
  record=fonts[language][index];face=f.TextFace(record);name=face.font.getBestCmap().get(ord(char))
  if not name or name=='.notdef': raise ValueError(f'Uncovered glyph {char} in {record["family"]}')
  glyph=face.glyphset[name];bounds=BoundsPen(face.glyphset);glyph.draw(bounds)
  x0,y0,x1,y1=bounds.bounds;factor=min(26/(x1-x0),27/(y1-y0))
  pen=SVGPathPen(face.glyphset);glyph.draw(TransformPen(pen,(factor,0,0,-factor,-(x0+x1)/2*factor,(y0+y1)/2*factor)))
  d=pen.getCommands();GLYPHS.append(d)
  CARGO.append({'char':char,'font':record,'glyphName':name,'path':d,'pathSha256':hashlib.sha256(d.encode()).hexdigest(),'material':'imagegen metal type slug, blank face overprinted with exact font contour'})
 for piece,center in zip(CARGO,FACE_CENTERS):piece['photographicFaceCentre']=list(center)
 (ASSETS/'cargo-manifest.json').write_text(json.dumps(CARGO,ensure_ascii=False,indent=2)+'\n')

def mix(a,b,p): return a+(b-a)*p

def word(value,x,y,size,color='#55534b',anchor='middle',face=inter):
 return f.text(value,x,y,size,color,anchor,face=face)

@lru_cache(maxsize=None)
def photo(name):
 path=ASSETS/f'sprite-{name}.png'
 return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()

SPRITES=json.loads((ASSETS/'sprite-layout.json').read_text())

def raster(name,x=0,y=0,width=None,height=None):
 image=Image.open(ASSETS/f'sprite-{name}.png')
 if width is None:width=image.width
 if height is None:height=image.height
 return f'<image xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="{photo(name)}" x="{x}" y="{y}" width="{width}" height="{height}"/>'

CARGO_WIDTH=215
SOURCE_X,SOURCE_Y=190,452
LOAD_X,LOAD_Y=361,436
FACE_CENTERS=[(335,665),(569,665),(798,669),(1034,668),(1273,668),(455,462),(711,467),(964,465),(1236,465),(559,251),(840,260),(1095,254)]

@lru_cache(maxsize=1)
def cargo_photo():
 # The generated material has blank faces. Every printed contour is the actual
 # source font, mapped onto the matching metal face in the photographic pallet.
 factor=CARGO_WIDTH/1327
 content=[raster('cargo',0,0,1619,971)]
 for piece,(x,y) in zip(CARGO,FACE_CENTERS):
  d=piece['path']
  content.append(f'<path d="{d}" fill="#efe7d1" opacity=".22" transform="translate({x+.5/factor} {y+.6/factor}) scale({1/factor})"/>')
  content.append(f'<path d="{d}" fill="{('#e0e0d5' if CARGO.index(piece) in (1,4,7,11) else '#343a31')}" opacity=".84" transform="translate({x} {y}) scale({1/factor})"/>')
 return ''.join(content)


def pallet(x,y,scale=1,tilt=0,clip=None):
 factor=CARGO_WIDTH/1327*scale
 inside=f'<g transform="translate({x:.5f} {y:.5f}) rotate({tilt:.5f}) scale({factor:.7f}) translate(-810 -890)">{cargo_photo()}</g>'
 return f'<g clip-path="url(#{clip})">{inside}</g>' if clip else inside


def link(name,a,b,length):
 p0,p1=SPRITES[name]['pivots']
 native_length=math.hypot(p1[0]-p0[0],p1[1]-p0[1]);factor=length/native_length
 native_angle=math.degrees(math.atan2(p1[1]-p0[1],p1[0]-p0[0]))
 angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))-native_angle
 return f'<g transform="translate({a[0]:.5f} {a[1]:.5f}) rotate({angle:.5f}) scale({factor:.7f}) translate({-p0[0]:.7f} {-p0[1]:.7f})">{raster(name)}</g>'


def robot(x,y,receiving=False,scale=1):
 base=(1015,430) if receiving else (160,480)
 l1,l2=(150,190) if receiving else (130,130)
 # Pallet forks are level independently of the forearm's angle. Wrist is below
 # the support surface, so the visible photograph carries the actual pallet.
 native_contact=SPRITES['fork']['contact'];native_wrist=SPRITES['fork']['pivots'][0]
 fork_factor=CARGO_WIDTH*scale/SPRITES['fork']['supportWidth']
 wrist=(x,y-12*scale+(native_wrist[1]-native_contact[1])*fork_factor)
 dx,dy=wrist[0]-base[0],wrist[1]-base[1];r=math.hypot(dx,dy)
 if not abs(l1-l2)+.5<=r<=l1+l2-.5:raise ValueError(f'Robot reach violated: {receiving} {wrist} r={r}')
 along=(l1*l1-l2*l2+r*r)/(2*r);height=math.sqrt(max(0,l1*l1-along*along))
 sign=1 if receiving else -1
 elbow=(base[0]+dx/r*along-sign*dy/r*height,base[1]+dy/r*along+sign*dx/r*height)
 p0=SPRITES['base']['pivots'][0];base_factor=.42
 content=f'<g transform="translate({base[0]} {base[1]}) scale({base_factor}) translate({-p0[0]} {-p0[1]})">{raster('base')}</g>'
 content+=link('upper',base,elbow,l1)+link('fore',elbow,wrist,l2)
 content+=f'<g transform="translate({x:.6f} {y-12*scale:.6f}) scale({fork_factor:.6f}) translate({-native_contact[0]:.6f} {-native_contact[1]:.6f})">{raster('fork')}</g>'
 return content


def receiving_support():
 x,y,scale=814,390,.5
 contact=SPRITES['fork']['contact'];pivot=SPRITES['fork']['pivots'][0];factor=CARGO_WIDTH*scale/SPRITES['fork']['supportWidth']
 wrist_y=y-12*scale+(pivot[1]-contact[1])*factor
 base_pivot=SPRITES['base']['pivots'][0]
 content=f'<g transform="translate({x} {wrist_y}) scale(.20) translate({-base_pivot[0]} {-base_pivot[1]})">{raster('base')}</g>'
 content+=f'<g transform="translate({x} {y-12*scale}) scale({factor}) translate({-contact[0]} {-contact[1]})">{raster('fork')}</g>'
 return content


def handling(t,bounds,tracking):
 start=tracking['anchors'][0];scale=(bounds[2]-bounds[0])/(start[2]-start[0]);dx=bounds[0]-start[0];dy=bounds[1]-start[1]
 load_x=bounds[0]+(LOAD_X-start[0])*scale;load_y=start[1]+(LOAD_Y-start[1])*scale+dy
 # One level loaded pallet. No glyph-specific motion or alpha dissolution.
 if t<2:
  cargo_x,cargo_y=SOURCE_X,SOURCE_Y
 elif t<3.85:
  lift=smooth(t,2,2.45);travel=smooth(t,2.45,3.35);lower=smooth(t,3.35,3.85)
  cargo_x=mix(SOURCE_X,LOAD_X,travel);cargo_y=SOURCE_Y-64*lift+48*lower
 elif t<9:
  cargo_x,cargo_y=load_x,load_y
 else:
  lift=smooth(t,9,9.5);travel=smooth(t,9.5,10.2);lower=smooth(t,10.2,10.8)
  cargo_x=mix(load_x,814,travel);cargo_y=load_y-48*lift+(390-load_y+48)*travel
 # Source forks release after the pallet has landed, then withdraw before drive.
 if t<4.12:source_x,source_y=cargo_x,cargo_y
 elif t<4.3:source_x,source_y=LOAD_X,LOAD_Y+8*smooth(t,4.12,4.3)
 elif t<5:
  p=smooth(t,4.3,4.95);source_x=mix(LOAD_X,SOURCE_X,p);source_y=mix(LOAD_Y+8,SOURCE_Y,p)
 else:source_x,source_y=SOURCE_X,SOURCE_Y
 # Receiver insertion occurs while cargo stays on the truck. Handing off to the
 # bay is followed by empty fork withdrawal, not an empty arm following goods.
 if t<8.5:receive_x,receive_y=815,432
 elif t<9:
  p=smooth(t,8.5,9);receive_x=mix(815,load_x,p);receive_y=mix(432,load_y,p)
 elif t<10.8:receive_x,receive_y=cargo_x,cargo_y
 elif t<11.05:receive_x,receive_y=814,390+6*smooth(t,10.8,11.05)
 else:
  p=smooth(t,11.05,11.8);receive_x=mix(814,815,p);receive_y=mix(396,432,p)
 cab_x=bounds[0]+(548-start[0])*scale;bed_y=start[1]+(399-start[1])*scale+dy
 left=bounds[0]-4;right=bounds[2]+4;cab_top=bounds[1]-4
 # Union of visible rectangles avoids relying on SVG-mask luminance semantics.
 # Both machinery and pallet are really behind the full foreground bed/cabin.
 content=(f'<defs><clipPath id="behind-truck"><rect x="0" y="0" width="{left}" height="720"/>'
  f'<rect x="{left}" y="0" width="{cab_x-left}" height="{bed_y}"/>'
  f'<rect x="{cab_x}" y="0" width="{right-cab_x}" height="{cab_top}"/>'
  f'<rect x="{right}" y="0" width="{1152-right}" height="720"/>'
  f'<rect x="{left}" y="535" width="{right-left}" height="185"/></clipPath>'
  '<clipPath id="bay"><rect x="756" y="328" width="249" height="108" rx="10"/></clipPath></defs>')
 receive_scale=mix(1,.5,smooth(t,9.5,10.2)) if t<11.05 else mix(.5,1,smooth(t,11.05,11.8))
  # Before docking, the parked gripper has its full scale.
 if t<9.5:receive_scale=1
 content+=f'<g clip-path="url(#behind-truck)"><g clip-path="url(#bay)">{receiving_support()}</g>{robot(source_x,source_y)}{robot(receive_x,receive_y,True,receive_scale)}</g>'
 if t<9.5:
  content+=pallet(cargo_x,cargo_y,scale if t>=5 else 1,clip='behind-truck')
 elif t<10.2:
  content+=pallet(cargo_x,cargo_y,mix(scale,.5,smooth(t,9.5,10.2)),clip='behind-truck')
 elif t<11.8:
  # It recedes into the open bay, lands on its floor, then rolls behind the
  # right jamb. The visible goods never dissolve into the wall.
  cargo_scale=.5
  travel=smooth(t,11.05,11.8);cargo_x=mix(814,1080,travel)
  content+=f'<g clip-path="url(#bay)">'+pallet(cargo_x,cargo_y,cargo_scale,clip='behind-truck')+'</g>'
 # The next batch emerges from the workshop as the empty truck returns. It is
 # already stable on its pallet before the next loading cycle begins.
 content='<defs><clipPath id="foundry-stock"><rect x="98" y="328" width="172" height="108"/></clipPath></defs>'+pallet(235,423,.5,clip='foundry-stock')+content
 if t>=14:
  p=smooth(t,14,17.6);new_x=mix(235,SOURCE_X,p);new_y=mix(423,SOURCE_Y,p);new_scale=mix(.5,1,p)
  content+=pallet(new_x,new_y,new_scale,clip='behind-truck')
 return content


def wheel_track():
 path=ASSETS/'wheel-observed.json'
 if path.exists():return json.loads(path.read_text())
 tracking=json.loads((PHYSICAL/'truck-observed.json').read_text())
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(PHYSICAL/'transport-h3.mp4'),'-vf','fps=24,scale=1152:720','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
 frames=np.frombuffer(data,dtype=np.uint8).reshape(-1,H,W,3)
 def observe(image,bounds):
  image=np.asarray(image.convert('RGB')) if isinstance(image,Image.Image) else image
  out=[]
  for fraction in (.125,.303,.817):
   predicted=bounds[0]+fraction*(bounds[2]-bounds[0]);left=int(predicted-44);right=int(predicted+44)
   area=image[502:534,left:right,:];mask=np.max(area,axis=2)<110
   columns=np.flatnonzero(mask.sum(axis=0)>3);groups=np.split(columns,np.where(np.diff(columns)>3)[0]+1)
   group=max(groups,key=lambda values:mask[:,values].sum())
   out.append([left+(group[0]+group[-1])/2,490,35])
  return out
 observations=[observe(frame,bounds) for frame,bounds in zip(frames,tracking['frames'])]
 arr=np.asarray(observations,dtype=float)
 for i in range(len(arr)):
  lo=max(0,i-2);hi=min(len(arr),i+3);arr[i,:,0]=np.mean(np.asarray(observations)[lo:hi,:,0],axis=0)
 anchors=[observe(Image.open(PHYSICAL/name).resize((W,H),Image.Resampling.LANCZOS),bounds) for name,bounds in zip(('start-anchor.png','end-anchor.png'),tracking['anchors'])]
 result={'method':'Observed lower tire silhouettes in real H3 frames; circular generated wheels roll by signed displacement / radius. Fixed grounded centre height and radius.','fps':24,'frames':arr.tolist(),'anchors':anchors}
 path.write_text(json.dumps(result,indent=2)+'\n');return result


def wheels(t,tracking):
 data=wheel_track();start,end=data['anchors']
 if t<5 or t>=15.5:current=start
 elif 8.5<=t<12:current=end
 else:
  p=(t-5)/3.5 if t<8.5 else 1-(t-12)/3.5;n=max(0,min(len(data['frames'])-1,p*(len(data['frames'])-1)));i=int(n);j=min(i+1,len(data['frames'])-1)
  current=[[mix(a,b,n-i) for a,b in zip(x,y)] for x,y in zip(data['frames'][i],data['frames'][j])]
 if 5<=t<8.5:
  a=smooth(t,5,5.15);b=smooth(t,8.35,8.5)
  current=[[mix(mix(u,v,a),w,b) for u,v,w in zip(s,c,e)] for s,c,e in zip(start,current,end)]
 elif 12<=t<15.5:
  a=smooth(t,12,12.15);b=smooth(t,15.35,15.5)
  current=[[mix(mix(u,v,a),w,b) for u,v,w in zip(e,c,s)] for e,c,s in zip(end,current,start)]
 content=[]
 for index,(x,y,r) in enumerate(current):
  angle=math.degrees((x-start[index][0])/r)
  factor=r/(539*192/1254);px=628*192/1254;py=619.5*192/1254
  content.append(f'<g transform="translate({x:.6f} {y}) rotate({angle:.6f}) scale({factor:.7f}) translate({-px:.7f} {-py:.7f})">{raster('wheel')}</g>')
 return ''.join(content)


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
 anchors=[truck_observation(Image.open(PHYSICAL/name).resize((W,H),Image.Resampling.LANCZOS)) for name in ('start-anchor.png','end-anchor.png')]
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


def overlay(t,tracking):
 bounds=pose(t,tracking); start=tracking['anchors'][0]
 scale=(bounds[2]-bounds[0])/(start[2]-start[0])
 dx=bounds[0]-start[0]; dy=bounds[1]-start[1]
 content=[handling(t,bounds,tracking),wheels(t,tracking)]
 content.append(word('Type Foundry',180,314,24,'#4c5047'))
 content.append(word('iOS',916,267,79,'#5f655a'))
 # Whole generated frame used as a side-board texture in movie compositing.
 # The body board remains in the source coordinate frame and follows observed H3 motion.
 tx=bounds[0]-start[0]*scale;ty=bounds[1]-start[1]*scale
 content.append(f'<defs><clipPath id="paint"><path d="M209 405H543V443H209Z"/></clipPath></defs><g transform="translate({tx:.5f} {ty:.5f}) scale({scale:.6f})"><image xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="{PAINT_IMAGE}" x="0" y="0" width="1152" height="720" preserveAspectRatio="none" clip-path="url(#paint)"/></g>')
 marketing=smooth(t,12,12.5)*(1-smooth(t,16.2,16.8))
 marketing_size=min(48,1000/(LABEL_FACE.shape(MARKETING)[1]/1000))
 content.append(f'<g opacity="{marketing:.4f}">'+word(MARKETING,576,130,marketing_size,'#373e33',face=LABEL_FACE)+'</g>')
 return '<svg xmlns="http://www.w3.org/2000/svg" width="1152" height="720" viewBox="0 0 1152 720">'+''.join(content)+'</svg>'


def make_plate(tmp):
 raw=PHYSICAL/'transport-h3.mp4'; duration=float(f.probe(raw)['format']['duration'])
 graph=('[0:v]fps=30,trim=duration=5.15,format=yuv420p[a];[1:v]split[forward][back];'
  f'[forward]setpts={3.5/duration}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=0.3,trim=duration=3.65,format=yuv420p[b];'
  '[2:v]fps=30,trim=duration=3.65,format=yuv420p[c];'
  f'[back]reverse,setpts={3.5/duration}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=0.3,trim=duration=3.65,format=yuv420p[d];'
  '[3:v]fps=30,trim=duration=2.5,format=yuv420p[e];'
  '[a][b]xfade=transition=fade:duration=0.15:offset=5[ab];[ab][c]xfade=transition=fade:duration=0.15:offset=8.5[abc];'
  '[abc][d]xfade=transition=fade:duration=0.15:offset=12[abcd];[abcd][e]xfade=transition=fade:duration=0.15:offset=15.5,scale=1152:720[v]')
 out=ROOT/'scripts/assets/fondfont/animation/v14/physical-plate.mp4'
 if out.exists(): return out
 subprocess.run(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(PHYSICAL/'start-anchor.png'),'-i',str(raw),'-loop','1','-framerate','30','-i',str(PHYSICAL/'end-anchor.png'),'-loop','1','-framerate','30','-i',str(PHYSICAL/'start-anchor.png'),'-filter_complex',graph,'-map','[v]','-t',str(SECONDS),'-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(out)],check=True)
 return out


def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('--preview',action='store_true'); p.add_argument('--locale',default='zh-hans'); a=p.parse_args()
 configure_locale(a.locale)
 tracking_file=PHYSICAL/'truck-observed.json'
 if tracking_file.exists(): tracking=json.loads(tracking_file.read_text())
 elif (PHYSICAL/'transport-h3.mp4').exists(): tracking=build_tracking(PHYSICAL/'transport-h3.mp4')
 else:
  anchors=[truck_observation(Image.open(PHYSICAL/name).resize((W,H),Image.Resampling.LANCZOS)) for name in ('start-anchor.png','end-anchor.png')]
  tracking={'anchors':anchors,'frames':[anchors[0],anchors[1]]}
 if a.preview:
  for t in (0,1.4,2.95,4.0,5.0,8.5,10.3,11.3,13.5,17.5):
   svg=overlay(t,tracking); (ASSETS/f'overlay-{LOCALE}-{t:g}.svg').write_text(svg)
   png=cairosvg.svg2png(bytestring=svg.encode()); (ASSETS/f'overlay-{LOCALE}-{t:g}.png').write_bytes(png)
   import io
   if 5<t<8.5 or 12<t<15.5:
    duration=float(f.probe(PHYSICAL/'transport-h3.mp4')['format']['duration'])
    progress=(t-5)/3.5 if t<8.5 else 1-(t-12)/3.5
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(progress*duration),'-i',str(PHYSICAL/'transport-h3.mp4'),'-vf','scale=1152:720','-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'])
    image=Image.open(io.BytesIO(data)).convert('RGBA')
   else:
    image=Image.open(PHYSICAL/('end-anchor.png' if t>=8.5 and t<12 else 'start-anchor.png')).convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
   image.alpha_composite(Image.open(io.BytesIO(png))); image.convert('RGB').save(ASSETS/f'story-{LOCALE}-{t:g}.png')
  return
 out=PUBLIC/f'concept-factory-{LOCALE}-v15.mp4'
 if out.exists(): p.error('Preserve previous movie; choose a new version.')
 if not tracking_file.exists(): tracking=build_tracking(PHYSICAL/'transport-h3.mp4')
 with tempfile.TemporaryDirectory(prefix='fondfont-v15-') as temporary:
  tmp=Path(temporary); plate=make_plate(tmp)
  process=subprocess.Popen(['ffmpeg','-v','error','-i',str(plate),'-f','image2pipe','-framerate','30','-vcodec','png','-i','-','-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto,tpad=stop_mode=clone:stop_duration=0.3,fps=30:start_time=0,setpts=PTS-STARTPTS,trim=duration=18[v]','-map','[v]','-t',str(SECONDS),'-an','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
  try:
   for frame in range(FPS*SECONDS): process.stdin.write(cairosvg.svg2png(bytestring=overlay(frame/FPS,tracking).encode()))
   process.stdin.close()
   if process.wait(): raise RuntimeError('Compositing failed')
  except BaseException:
   process.kill(); raise
 subprocess.run(['ffmpeg','-v','error','-i',str(out),'-vf',"select='eq(n,0)+eq(n,45)+eq(n,89)+eq(n,120)+eq(n,195)+eq(n,255)+eq(n,315)+eq(n,345)+eq(n,405)+eq(n,465)+eq(n,510)+eq(n,539)',scale=384:240,tile=4x3",'-frames:v','1',str(ASSETS/f'contact-sheet-{LOCALE}.png')],check=True)
 sources=[PHYSICAL/name for name in ('start-anchor.png','end-anchor.png','transport-h3.mp4','generation.json','h3-prompt.txt','truck-observed.json')]+[Path(__file__).resolve(),PAINT_PATH,ASSETS/'cargo-manifest.json',ASSETS/'robot-sprites.png',ASSETS/'cargo-pallet.png',ASSETS/'wheel.png',ASSETS/'fork-support.png',ASSETS/'sprite-layout.json',ASSETS/'wheel-observed.json']+[ROOT/path for path in sorted({item['font']['path'] for item in CARGO})]
 (ASSETS/f'manifest-{LOCALE}.json').write_text(json.dumps({'engine':'Accepted actual MiniMax-H3 v13 truck travel; imagegen v14 truck paint plus new v15 photo-matched hardware, type pallet and wheel. Native kinematics and exact font contours.','locale':LOCALE,'truckPaintName':BRAND,'nameSource':'src/i18n/fondfont-locales.mjs','cargo':'One shared mixed multilingual batch, real font contours on metal type slugs. Never localized or swapped during the journey.','paint':'Built-in imagegen v14 surface painting, reused unchanged.','handling':'Built-in imagegen physical machinery, pallet, metal slug materials and complete circular wheel; fixed-length IK, level forks, supported handoffs, signed distance / radius rolling. Exact font contours mapped onto blank generated metal faces.','copy':MARKETING,'scope':'External Type Foundry manufactures font goods; FondFont transports; iOS receives. Same-device font library in compatible apps; not font generation by FondFont, OS UI replacement or device sync.','timeline':{'prepare':[0,2],'supportedLoad':[2,5],'loadedTruck':[5,8.5],'unloadIntoIOS':[8.5,12],'marketingAndEmptyTruckReturn':[12,15.5],'reset':[15.5,18]},'probe':f.probe(out),'sources':[{'path':str(s.relative_to(ROOT)),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for s in sources],'output':{'path':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}},ensure_ascii=False,indent=2)+'\n')
 print(out,flush=True)

if __name__=='__main__': main()
