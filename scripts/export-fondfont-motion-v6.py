"""Compose genuine Bebas installation excerpts and the H3 workspace handoff.

The final font selector and live typesetting are labelled conceptual design,
not a captured third-party app. Native Settings completion is authentic footage.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v6'
PUBLIC = ROOT / 'public/v/fondfont'
APP = Path('/Users/realazy/Projects/iOS/iOSFontInstaller')
NATIVE = ASSETS / 'native'
W,H,FPS = 768,864,30
PW,PH = 560,704
START = np.array([[110,86],[660,122],[650,772],[120,810]],dtype=float)
END = np.array([[104,80],[664,80],[664,784],[104,784]],dtype=float)
PAPER = (255,255,255)
BEBAS = ASSETS / 'BebasNeue-Regular.ttf'
SF = '/System/Library/Fonts/SFNS.ttf'
SHOTS = [('d2-detail.mp4',1.4),('d3-guide.mp4',2.7),('d4-settings.mp4',0.8),('d5-profile.mp4',0.9),('d6-installed.mp4',1.5)]
HANDOFF = 1.75
EDITOR = 5.0


def editor(t):
    im = Image.new('RGB',(PW,PH),PAPER);d=ImageDraw.Draw(im)
    ui=ImageFont.truetype(SF,32)
    d.line([(36,218),(524,218)],fill='#d1cec7',width=1)
    d.text((36,155),'Aa',font=ImageFont.truetype(SF,40),fill='#686864')
    d.text((112,165),'Bebas Neue',font=ui,fill='#383834')
    d.line([(494,179),(502,187),(510,179)],fill='#686864',width=2)
    for y in [440,510,630]:
        d.line([(36,y),(524,y)],fill='#e2e0da',width=1)
    if t < 1.1:
        d.rounded_rectangle((30,230,530,398),radius=8,fill='#ffffff',outline='#d1cec7',width=1)
        for i, name in enumerate(['System','Bebas Neue','Georgia']):
            y=247+i*47
            if i==1 and t>=0.55:
                d.rounded_rectangle((40,y-5,520,y+39),radius=4,fill='#eae7e0')
                d.line([(483,y+16),(491,y+24),(505,y+7)],fill='#934a35',width=3)
            f=ImageFont.truetype(BEBAS,34) if i==1 else ui
            d.text((112,y),name,font=f,fill='#383834')
        return im
    a=min(4,max(0,int((t-1.1)/0.18)))
    b=min(9,max(0,int((t-1.9)/0.17)))
    f1=ImageFont.truetype(BEBAS,270);f2=ImageFont.truetype(BEBAS,168)
    d.text((36,440),'MAKE'[:a],font=f1,fill='#30302d',anchor='ls')
    d.text((36,630),'IT YOURS.'[:b],font=f2,fill='#30302d',anchor='ls')
    if t < 4.2 and int(t*2)%2==0:
        if t<1.9: x=36+f1.getlength('MAKE'[:a]);top,bottom=245,440
        else: x=36+f2.getlength('IT YOURS.'[:b]);top,bottom=508,630
        d.line([(x+3,top),(x+3,bottom)],fill='#934a35',width=2)
    return im


def warp(texture, corners):
    # PIL maps each output point into the source. Solve exact projective mapping.
    dst=np.array(corners,dtype=float);src=np.array([[0,0],[PW,0],[PW,PH],[0,PH]],dtype=float)
    rows=[];vals=[]
    for (x,y),(u,v) in zip(dst,src):
        rows.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
        vals.extend([u,v])
    coeff=np.linalg.solve(np.array(rows),np.array(vals))
    rgba=texture.convert('RGBA')
    result=rgba.transform((W,H),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
    base=Image.new('RGB',(W,H),PAPER);base.paste(result,mask=result.getchannel('A'))
    return base


NATIVE_IMAGES = {}

def native_frame(name, pan=0):
    if name not in NATIVE_IMAGES:
        data=subprocess.check_output(['ffmpeg','-v','error','-ss','0.3','-i',str(NATIVE/name),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
        from io import BytesIO
        NATIVE_IMAGES[name]=Image.open(BytesIO(data)).convert('RGB')
    image=NATIVE_IMAGES[name]
    # Retain font identity, completion title, all profile details and controls;
    # omit the cover-display status strip outside the app's work area.
    top=40+round(440*pan)
    crop=image.crop((48,top,1178,top+1470))
    crop.thumbnail((PW,PH),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(PW,PH),PAPER)
    canvas.paste(crop,((PW-crop.width)//2,0))
    return canvas


def track_plane(frame):
    # The paired references intentionally isolate one darker planar region.
    a=np.asarray(frame.convert('RGB'))
    ys,xs=np.nonzero(np.max(a,axis=2)<231)
    keep=(xs>45)&(xs<723)&(ys>30)&(ys<835);xs=xs[keep];ys=ys[keep]
    if len(xs)<150000:
        raise RuntimeError('H3 plane not trackable; inspect generation before export.')
    p=np.column_stack([xs,ys]);s=xs+ys;q=xs-ys
    return np.array([p[np.argmin(s)],p[np.argmax(q)],p[np.argmax(s)],p[np.argmin(q)]],dtype=float)


def h3_frames():
    raw=ASSETS/'workspace-handoff-h3.mp4'
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(raw),'-vf',f'fps={FPS},scale={W}:{H}',
        '-f','rawvideo','-pix_fmt','rgb24','-'])
    frames=np.frombuffer(data,dtype=np.uint8).reshape(-1,H,W,3)
    count=round(HANDOFF*FPS)
    indices=np.linspace(0,len(frames)-1,count).round().astype(int)
    frames=[Image.fromarray(frames[i]) for i in indices]
    corners=np.array([track_plane(f) for f in frames])
    # A brief symmetric smoothing removes pixel-level segmentation jitter;
    # endpoints stay locked to the supplied reference layout.
    for _ in range(2):
        corners[1:-1]=(corners[:-2]+2*corners[1:-1]+corners[2:])/4
    corners += ((START-corners[0])[None,:,:]*(1-np.linspace(0,1,count))[:,None,None]
                +(END-corners[-1])[None,:,:]*np.linspace(0,1,count)[:,None,None])
    (ASSETS/'tracked-plane.json').write_text(json.dumps({'frames':corners.tolist(),'fps':FPS},indent=2)+'\n')
    return frames,corners


def compose(preview=False):
    PUBLIC.mkdir(parents=True,exist_ok=True)
    poster=warp(editor(5),END)
    target=ASSETS/'storyboard.png' if preview else PUBLIC/'hero-h3-v6a.jpg'
    poster.save(target,quality=92)
    source_frames=[native_frame(name) for name,_ in SHOTS]
    contact=Image.new('RGB',(W*4,H),PAPER)
    for i,frame in enumerate([warp(source_frames[0],START),warp(source_frames[1],START),warp(source_frames[-1],START),poster]):
        contact.paste(frame,(i*W,0))
    contact.save(ASSETS/'storyboard-contact.png')
    if preview:return
    out=PUBLIC/'hero-h3-v6a.mp4'
    if out.exists():raise RuntimeError('Preserve published export; use a new suffix.')
    h3,corners=h3_frames()
    cmd=['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-an','-c:v','libx264','-preset','slow','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    native_end=sum(duration for _,duration in SHOTS)
    frames=0
    for source,(name,duration) in zip(source_frames,SHOTS):
        f=warp(source,START)
        for i in range(round(duration*FPS)):
            if name == 'd3-guide.mp4':
                progress=min(1,max(0,(i/FPS-1.4)/0.8))
                progress=progress*progress*(3-2*progress)
                f=warp(native_frame(name,progress),START)
            encoder.stdin.write(f.tobytes());frames+=1
    for i,(raw,quad) in enumerate(zip(h3,corners)):
        progress=i/(len(h3)-1)
        alpha=min(1,max(0,(progress-0.08)/0.38))
        texture=Image.blend(source_frames[-1],editor(0),alpha)
        # H3 contributes the full tracked perspective. Exact captured UI and
        # licensed glyphs replace the deliberately empty tracking surface.
        f=warp(texture,quad)
        encoder.stdin.write(f.tobytes());frames+=1
    for i in range(round(EDITOR*FPS)):
        f=warp(editor(i/FPS),END)
        encoder.stdin.write(f.tobytes());frames+=1
    encoder.stdin.close()
    if encoder.wait():raise RuntimeError('Encoding failed')
    manifest={
        'model':'MiniMax-H3','dimensions':[W,H],'fps':FPS,'frames':frames,
        'duration':frames/FPS,'illustrationFromSeconds':native_end,
        'nativeFootageLocale':'en-US','nativeCrop':{'x':48,'width':1130,'height':1470,'top':40,'guidePanTo':480},
        'scope':'Actual FondFont and iOS Settings installation excerpts, then explicitly labelled conceptual font selector and typesetting. No Pages recording claimed.',
        'sources':[{'path':str(NATIVE/name),'sha256':hashlib.sha256((NATIVE/name).read_bytes()).hexdigest(),'holdSeconds':duration} for name,duration in SHOTS],
        'h3':{'path':str((ASSETS/'workspace-handoff-h3.mp4').relative_to(ROOT)),'sha256':hashlib.sha256((ASSETS/'workspace-handoff-h3.mp4').read_bytes()).hexdigest(),'purpose':'Tracked perspective handoff of one software work plane; not generated UI'},
        'font':{'name':'Bebas Neue Regular','file':str(BEBAS.relative_to(ROOT)),'sha256':hashlib.sha256(BEBAS.read_bytes()).hexdigest(),'license':'Bebas-OFL.txt'},
        'outputs':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [out,PUBLIC/'hero-h3-v6a.jpg']],
    }
    (ASSETS/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--storyboard',action='store_true')
    compose(parser.parse_args().storyboard)
