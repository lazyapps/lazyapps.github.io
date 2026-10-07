"""Continue the approved H3 openings with real-font theatrical choreography."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tempfile
import cairosvg
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fondfont_v11',ROOT/'scripts/compose-fondfont-comparison-v11.py')
v11 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v11)
ASSETS = ROOT/'scripts/assets/fondfont/animation/v12'
PUBLIC = ROOT/'public/v/fondfont'
W,H,FPS,SECONDS = 1152,720,30,14
smooth,text = v11.smooth,v11.text
characters = '明月松间照清泉石上流'
paths = []
for c in characters:
 pen = SVGPathPen(v11.glyphset)
 v11.glyphset[v11.font.getBestCmap()[ord(c)]].draw(TransformPen(pen,(v11.factor,0,0,-v11.factor,-500,0)))
 paths.append(pen.getCommands())
centers=[]
for d in paths:
 pen=BoundsPen(None); parse_path(d,pen); centers.append((pen.bounds[1]+pen.bounds[3])/2)

def mix(a,b,p): return a+(b-a)*p

def letter(index,x,baseline,size,angle=0,color='#ad543a',opacity=1,depth=False):
 if opacity <= 0: return ''
 layers=[]
 if depth:
  for z in (6,4,2):
   layers.append(f'<g transform="translate({x+z*.35:.3f} {baseline+z*.6:.3f}) rotate({angle:.3f}) scale({size/1000:.5f})"><path d="{paths[index]}" fill="#743d2c" opacity=".55"/></g>')
 layers.append(f'<g transform="translate({x:.3f} {baseline:.3f}) rotate({angle:.3f}) scale({size/1000:.5f})"><path d="{paths[index]}" fill="{color}"/></g>')
 return f'<g opacity="{opacity:.4f}">'+''.join(layers)+'</g>'

def reflected_actor(index,x,center,size,angle,face_y,opacity,color):
 # Orthographic projection of the whole rigid glyph turning around its horizontal
 # axis. The font contour never changes; only its viewing angle does.
 return f'<g opacity="{opacity:.4f}" transform="translate({x:.3f} {center:.3f}) rotate({angle:.3f}) scale({size/1000:.5f} {size/1000*face_y:.5f}) translate(0 {-centers[index]:.4f})"><path d="{paths[index]}" fill="{color}"/></g>'

def envelope(t,a,b,c,d): return smooth(t,a,b)*(1-smooth(t,c,d))

def playground(t):
 result=[]
 # The set remains a theatre. The largest actor claims the right half of the poster.
 for i in range(5):
  x0=300+140*i; y0=[548,550,528,519,544][i]
  if i==4:
   crouch=13*envelope(t,6.35,6.65,6.8,7.05)
   leap=smooth(t,6.8,8.0)
   land=smooth(t,8.0,9.35)
   x=mix(x0,460,leap); y=mix(y0,260,leap)+crouch
   x=mix(x,790,land); y=mix(y,585,land)
   size=mix(145,180,leap); size=mix(size,440,land)
   angle=-32*math.sin(math.pi*leap)*(1-land)+15*math.sin(math.pi*land)
   dt=t-9.35
   if 0 < dt < 1.1:
    y-=15*math.sin(dt*12)*math.exp(-dt*3.4)
    angle+=3*math.sin(dt*12)*math.exp(-dt*3.4)
  else:
   a=7.1+i*.19; b=9.1+i*.19
   p=smooth(t,a,b)
   x1=[305,478,305,478][i]; y1=[256,256,429,429][i]
   x=mix(x0,x1,p); y=mix(y0,y1,p)-165*math.sin(math.pi*p)
   size=mix(145,170,p)
   angle=(-20 if i%2 else 18)*math.sin(math.pi*p)
   if i==3:
    angle=-11*smooth(t,9.65,9.84)*(1-smooth(t,10.3,10.7))
    x+=11*envelope(t,9.65,9.9,10.25,10.7)
   if i==2:
    x-=18*smooth(t,9.98,10.32)
   dt=t-b
   if 0 < dt < .8: y-=7*math.sin(dt*13)*math.exp(-dt*4)
  result.append(letter(i,x,y,size,angle,depth=True))
 return ''.join(result)

def poetry(t):
 water=505
 lifted=smooth(t,6.3,7.15)
 fade=smooth(t,10.0,10.65)
 ripple=envelope(t,6.3,7.1,9.6,10.4)
 result=[f'<ellipse cx="576" cy="593" rx="{mix(215,420,smooth(t,6.3,9.8)):.2f}" ry="{mix(10,22,smooth(t,6.3,9.8)):.2f}" fill="none" stroke="#737e71" stroke-width=".8" opacity="{ripple*.1:.4f}"/>']
 for i in range(5):
  x0=300+140*i; base=mix(521,467,lifted)
  # A real, whole-outline reflection; no warped brush shapes or letter substitution.
  start=7.5+([1,0,2,3,4][i])*.30
  p=smooth(t,start,start+1.65)
  main_alpha=1-smooth(t,start+.25,start+1.7)
  result.append(letter(i,x0,base,145,color='#2f382c',opacity=main_alpha))
  drift=6*math.sin((t-6.3)*1.8+i*.5)*lifted
  if p==0:
   reflection_alpha=smooth(t,6.45,7.15)*.15
   mirror=letter(i,x0+drift,base,145,color='#526751',opacity=reflection_alpha)
   result.append(f'<g transform="translate(0 {2*water}) scale(1 -1)">{mirror}</g>')
  else:
   # Start at the reflection's exact visual centre. It turns upright continuously,
   # without crossfading in a second copy or jumping to a different baseline.
   x=mix(x0+drift,522,p)+32*math.sin(math.pi*p)*(-1 if i%2 else 1)
   size=mix(145,112,p)
   reflected_center=2*water-(base+centers[i]*.145)
   final_center=200+i*105+centers[i]*.112
   center=mix(reflected_center,final_center,p)
   angle=(-13 if i%2 else 11)*math.sin(math.pi*p)
   face_y=-math.cos(math.pi*smooth(t,start,start+.85))
   strength=smooth(t,start,start+.75)
   color='rgb('+','.join(str(round(mix(a,b,strength))) for a,b in zip((82,103,81),(41,57,44)))+')'
   result.append(reflected_actor(i,x,center,size,angle,face_y,mix(.15,1,strength),color))
 # One quiet vertical inscription belongs to the poem, not to an explanatory layout.
 stamp_alpha=smooth(t,10.6,11.15)
 result.append(f'<g opacity="{stamp_alpha:.4f}"><rect x="626" y="557" width="27" height="27" rx="1" fill="#ae5c46"/>'+text('维',639.5,577,19,'#faf8f2','middle',face=v11.display)+'</g>')
 return ''.join(result)

def continuation(t,variant):
 # No installation status, flow line, app cards or replacement of system UI.
 bleach=smooth(t,6.3,10.5)*(.20 if variant=='playground' else .35)
 content=[f'<rect width="1152" height="720" fill="#f8f8f6" opacity="{bleach:.4f}"/>']
 content.append(text('FondFont',48,55,24,'#55564d'))
 content.append(playground(t) if variant=='playground' else poetry(t))
 attribution=1-smooth(t,6.3,7.0)
 content.append(f'<g opacity="{attribution:.4f}">'+text('王维 · 山居秋暝',576,648,18,'#8b897f','middle')+'</g>')
 benefit=smooth(t,11.0,11.5)
 content.append(f'<g opacity="{benefit:.4f}">'+text('装进 iOS，在不同兼容 App 里创作。',576,675,23,'#66685d','middle')+'</g>')
 return ''.join(content)

def overlay(t,variant):
 if t < 6.3: return v11.overlay(t,variant)
 return '<svg xmlns="http://www.w3.org/2000/svg" width="1152" height="720" viewBox="0 0 1152 720">'+continuation(t,variant)+'</svg>'

def preview(variant,t):
 folder=ASSETS/variant; folder.mkdir(parents=True,exist_ok=True)
 svg=overlay(t,variant)
 (folder/f'overlay-{t:g}.svg').write_text(svg)
 png=cairosvg.svg2png(bytestring=svg.encode())
 (folder/f'overlay-{t:g}.png').write_bytes(png)
 from PIL import Image
 import io
 backdrop=Image.open(ROOT/f'scripts/assets/fondfont/animation/v11/{variant}/end-anchor.png').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
 backdrop.alpha_composite(Image.open(io.BytesIO(png)))
 backdrop.convert('RGB').save(folder/f'story-{t:g}.png')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('variant',choices=['playground','poetry'])
 parser.add_argument('--preview',action='store_true')
 parser.add_argument('--revision',choices=['v12','v12b'],default='v12')
 args=parser.parse_args(); variant=args.variant; folder=ASSETS/variant
 folder.mkdir(parents=True,exist_ok=True)
 if args.preview:
  for t in (6.3,7.8,9.6,10.8,11.8,13.0): preview(variant,t)
  return
 out=PUBLIC/f'concept-{variant}-brush-{args.revision}.mp4'
 if out.exists(): raise RuntimeError('Preserve existing exports; choose a new path.')
 source=ROOT/f'scripts/assets/fondfont/animation/v11/{variant}'
 duration=float(v11.probe(source/'scene-h3.mp4')['format']['duration'])
 with tempfile.TemporaryDirectory(prefix=f'fondfont-v12-{variant}-') as tmp:
  tmp=Path(tmp); plate=tmp/'plate.mp4'; film=tmp/'film.mp4'
  graph=('[0:v]fps=30,trim=duration=0.5,format=yuv420p[a];'
   f'[1:v]setpts={6/duration}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=0.2,trim=duration=6,format=yuv420p[b];'
   '[2:v]fps=30,trim=duration=7.95,format=yuv420p[c];'
   '[a][b]xfade=transition=fade:duration=0.15:offset=0.35[ab];'
   '[ab][c]xfade=transition=fade:duration=0.25:offset=6.10,scale=1152:720[v]')
  subprocess.run(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(source/'start-anchor.png'),'-i',str(source/'scene-h3.mp4'),'-loop','1','-framerate','30','-i',str(source/'end-anchor.png'),'-filter_complex',graph,'-map','[v]','-t',str(SECONDS),'-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(plate)],check=True)
  process=subprocess.Popen(['ffmpeg','-v','error','-i',str(plate),'-f','image2pipe','-framerate',str(FPS),'-vcodec','png','-i','-','-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto[v]','-map','[v]','-t',str(SECONDS),'-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',str(film)],stdin=subprocess.PIPE)
  try:
   for frame in range(FPS*SECONDS):
    process.stdin.write(cairosvg.svg2png(bytestring=overlay(frame/FPS,variant).encode()))
   process.stdin.close()
   if process.wait(): raise RuntimeError('Compositing failed')
  except BaseException:
   process.kill(); raise
  graph='[0:v]split[full][first];[first]trim=end_frame=1,loop=loop=-1:size=1:start=0,setpts=N/(30*TB),trim=duration=0.75[reset];[full][reset]xfade=transition=fade:duration=0.6:offset=13.25[v]'
  subprocess.run(['ffmpeg','-v','error','-i',str(film),'-filter_complex',graph,'-map','[v]','-t',str(SECONDS),'-an','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-vf',"select='eq(n,0)+eq(n,60)+eq(n,120)+eq(n,180)+eq(n,240)+eq(n,300)+eq(n,360)+eq(n,396)',scale=384:240,tile=4x2",'-frames:v','1',str(folder/'contact-sheet.png')],check=True)
  subprocess.run(['ffmpeg','-y','-v','error','-ss','11.8','-i',str(out),'-frames:v','1',str(folder/'story-film.png')],check=True)
 sources=[source/n for n in ('start-anchor.png','end-anchor.png','scene-h3.mp4','generation.json','h3-prompt.txt')]
 sources += [ROOT/'scripts/compose-fondfont-comparison-v11.py',Path(__file__).resolve(),ROOT/v11.selected['path']]
 (folder/('manifest.json' if args.revision=='v12' else f'manifest-{args.revision}.json')).write_text(json.dumps({'kind':'Reused approved full-model MiniMax-H3 opening, followed by native real-glyph choreography','font':v11.selected,'phrase':characters,'scope':'Typography theatre, not native iOS UI, font installation instructions or interface-font replacement. Benefit line limits cross-app usage to compatible apps on iOS.','timeline':{'approvedOpening':[0,6.3],'continuingStory':[6.3,13.25],'loopReset':[13.25,14]},'probe':v11.probe(out),'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'output':{'path':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}},ensure_ascii=False,indent=2)+'\n')
 print(out,flush=True)

if __name__=='__main__': main()
