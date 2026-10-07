"""Edit actual H3 loading, accepted H3 travel and actual H3 unloading into a film.

Native overlays retain accurate localized branding and exact font contours on
the rigid pallet ONLY during accepted travel. No native cargo handling animation.
"""
import argparse,hashlib,importlib.util,io,json,subprocess,tempfile
from pathlib import Path
import cairosvg
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'scripts/assets/fondfont/animation/v16'
PUBLIC=ROOT/'public/v/fondfont'
spec=importlib.util.spec_from_file_location('anchors',ROOT/'scripts/prepare-fondfont-factory-v16.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);v=a.v
FPS,SECONDS=30,20

def old_time(t):
    if t<5.5:return 0
    if t<9.1:return 5+(t-5.5)/3.6*3.5
    if t<14.4:return 8.5
    if t<18:return 12+(t-14.4)/3.6*3.5
    return 0

def fixed_machines(bounds):
    start=a.tracking['anchors'][0];scale=(bounds[2]-bounds[0])/(start[2]-start[0])
    cab=bounds[0]+(548-start[0])*scale;bed=bounds[1]+(399-start[1])*scale
    left=bounds[0]-3;right=bounds[2]+3
    content=f'<defs><clipPath id="behind"><rect width="{left}" height="720"/><rect x="{left}" width="{cab-left}" height="{bed}"/><rect x="{cab}" width="{right-cab}" height="{bounds[1]-3}"/><rect x="{right}" width="{1152-right}" height="720"/><rect x="{left}" y="535" width="{right-left}" height="185"/></clipPath><clipPath id="bay"><rect x="756" y="328" width="249" height="108" rx="10"/></clipPath></defs>'
    return content+f'<g clip-path="url(#behind)">{a.robot(190,430)}{a.robot(814,430,True)}</g>'

def travel_overlay(t):
    ot=old_time(t);bounds=v.pose(ot,a.tracking);start=a.tracking['anchors'][0]
    scale=(bounds[2]-bounds[0])/(start[2]-start[0]);content=fixed_machines(bounds)
    if 5.5<=t<9.1:
        x=bounds[0]+(361-start[0])*scale;y=bounds[1]+(436-start[1])*scale
        content+=v.pallet(x,y,clip='behind')
    elif 14.4<=t<18:
        content+='<g clip-path="url(#bay)">'+v.pallet(850,430,clip='behind')+'</g>'
    return content

def labels(t):
    ot=old_time(t);bounds=v.pose(ot,a.tracking);start=a.tracking['anchors'][0]
    scale=(bounds[2]-bounds[0])/(start[2]-start[0]);tx=bounds[0]-start[0]*scale;ty=bounds[1]-start[1]*scale
    content=v.wheels(ot,a.tracking)
    content+=v.word('Type Foundry',180,314,24,'#4c5047')+v.word('iOS',916,267,79,'#5f655a')
    content+=f'<defs><clipPath id="paint"><path d="M209 405H543V443H209Z"/></clipPath></defs><g transform="translate({tx:.5f} {ty:.5f}) scale({scale:.7f})"><image xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="{v.PAINT_IMAGE}" width="1152" height="720" preserveAspectRatio="none" clip-path="url(#paint)"/></g>'
    opacity=v.smooth(t,14.2,14.8)*(1-v.smooth(t,18.5,19.1))
    size=min(48,1000/(v.LABEL_FACE.shape(v.MARKETING)[1]/1000))
    content+=f'<g opacity="{opacity:.6f}">'+v.word(v.MARKETING,576,130,size,'#373e33',face=v.LABEL_FACE)+'</g>'
    return content

def make_plate(out):
    # Only the idle receiver region is replaced with its revised still layout;
    # H3 loading robot and cargo pixels at the left are preserved completely.
    corrected_load=ASSETS/'load-receiver-layout-v2.mp4'
    if not corrected_load.exists():
        alpha="255*min(1,min(min(X,W-1-X),min(Y,H-1-Y))/8)"
        graph=f"[0:v]scale=1152:720[raw];[1:v]crop=452:290:700:270,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='{alpha}'[patch];[raw][patch]overlay=700:270:format=auto[v]"
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(ASSETS/'load-h3.mp4'),'-loop','1','-i',str(ASSETS/'scene-first-v2.png'),'-filter_complex',graph,'-map','[v]','-t','3.75','-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(corrected_load)],check=True)
    segments=[('scene-first-v2.png',.4,'still'),('load-receiver-layout-v2.mp4',4.8,'video'),('scene-loaded-v2.png',.3,'still'),
              ('transport-h3.mp4',3.6,'travel'),('unload-first-v2.png',.2,'still'),('unload-h3-v2.mp4',4.8,'video'),
              ('unload-last-v2.png',.3,'still'),('transport-h3.mp4',3.6,'return')]
    files=[]
    for index,(name,duration,kind) in enumerate(segments):
        path=(v.ROOT/'scripts/assets/fondfont/animation/v14/physical-plate.mp4') if kind in ('travel','return') else ASSETS/name
        target=out/f'part-{index}.mp4';command=['ffmpeg','-v','error','-y']
        if kind=='still':command+=['-loop','1','-framerate','30']
        if kind in ('travel','return'):command+=['-ss',('5' if kind=='travel' else '12'),'-t','3.5']
        command+=['-i',str(path)]
        if kind=='still':vf='fps=30,scale=1152:720'
        else:
            input_duration=3.5 if kind in ('travel','return') else float(v.f.probe(path)['format']['duration'])
            vf=f'setpts={duration/input_duration}*(PTS-STARTPTS),tpad=stop_mode=clone:stop_duration=0.5,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,scale=1152:720'
        vf+=f',tpad=stop_mode=clone:stop_duration=1,fps=30,trim=duration={duration},setpts=PTS-STARTPTS'
        command+=['-vf',vf,'-t',str(duration),'-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(target)]
        subprocess.run(command,check=True)
        stream=v.f.probe(target)['streams'][0]
        assert int(stream['nb_frames'])==round(duration*FPS),(name,stream['nb_frames'],duration)
        files.append(target)
    # Editorial loop reset after the empty truck has completely stopped.
    # Bay cargo stays in its destination; the next shipment appears with the
    # whole-scene transition rather than a newly invented ingress animation.
    content=a.clip(False)+f'<g clip-path="url(#behind)">{a.robot(190,430)}{a.robot(814,430,True)}</g>'
    content+='<g clip-path="url(#bay)">'+v.pallet(850,430,clip='behind')+'</g>'
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1152" height="720">'+content+'</svg>'
    still=Image.open(v.PHYSICAL/'start-anchor.png').convert('RGBA').resize((1152,720),Image.Resampling.LANCZOS)
    still.alpha_composite(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))
    empty=ASSETS/'returned-empty.png';still.convert('RGB').save(empty)
    reset=out/'reset.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-framerate','30','-i',str(empty),'-loop','1','-framerate','30','-i',str(ASSETS/'scene-first-v2.png'),
      '-filter_complex','[0:v]fps=30,format=yuv420p,settb=AVTB[a];[1:v]fps=30,format=yuv420p,settb=AVTB[b];[a][b]xfade=transition=fade:duration=0.8:offset=0.65[v]',
      '-map','[v]','-t','2','-an','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(reset)],check=True)
    files.append(reset)
    listing=out/'concat.txt';listing.write_text(''.join(f"file '{path}'\n" for path in files))
    joined=out/'joined.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(joined)],check=True)
    return joined

def main():
    p=argparse.ArgumentParser();p.add_argument('--locale',default='zh-hans');p.add_argument('--plate',type=Path);p.add_argument('--plate-only',action='store_true');args=p.parse_args()
    v.configure_locale(args.locale);v.CARGO_WIDTH=140;v.cargo_photo.cache_clear()
    output=PUBLIC/f'concept-factory-{v.LOCALE}-v16.mp4'
    if output.exists():p.error('Preserve previous movie; create another version to change it.')
    if args.plate_only:
        with tempfile.TemporaryDirectory(prefix='fondfont-v16-plate-') as d:
            plate=make_plate(Path(d));import shutil;shutil.copy2(plate,ASSETS/'h3-editorial-plate.mp4')
        return
    plate=args.plate or ASSETS/'h3-editorial-plate.mp4'
    # The final short editorial dissolve restarts the shipping story. It is a
    # whole-film transition, never a pallet shrinking/fading during handling.
    process=subprocess.Popen(['ffmpeg','-v','error','-i',str(plate),'-f','image2pipe','-framerate','30','-vcodec','png','-i','-',
      '-filter_complex','[0:v][1:v]overlay=shortest=1:format=auto,tpad=stop_mode=clone:stop_duration=0.1,fps=30:start_time=0,trim=duration=20,setpts=PTS-STARTPTS[v]',
      '-map','[v]','-an','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
    try:
        for frame in range(FPS*SECONDS):
            t=frame/FPS;content=labels(t)
            if 5.5<=t<9.1 or 14.4<=t<18:content=travel_overlay(t)+content
            svg='<svg xmlns="http://www.w3.org/2000/svg" width="1152" height="720">'+content+'</svg>'
            process.stdin.write(cairosvg.svg2png(bytestring=svg.encode()))
        process.stdin.close()
        if process.wait():raise RuntimeError('Movie compositing failed')
    except BaseException:process.kill();raise
    sources=[Path(__file__),ROOT/'scripts/prepare-fondfont-factory-v16.py',ROOT/'scripts/generate-fondfont-factory-v16.py',ROOT/'scripts/compose-fondfont-factory-v15.py']+[ASSETS/name for name in ('load-first.png','load-last.png','scene-first-v2.png','scene-loaded-v2.png','unload-first-v2.png','unload-last-v2.png','load-h3.mp4','unload-h3-v2.mp4','load-generation.json','unload-generation-v2.json','load-h3-prompt.txt','unload-h3-v2-prompt.txt','anchor-geometry-v2.json')]+[v.PHYSICAL/'transport-h3.mp4',v.PHYSICAL/'truck-observed.json',v.PAINT_PATH]+[v.ASSETS/name for name in ('robot-sprites.png','cargo-pallet.png','wheel.png','fork-support.png','sprite-layout.json','wheel-observed.json')]+[ROOT/path for path in sorted({piece['font']['path'] for piece in v.CARGO})]
    manifest={'engine':'Actual MiniMax H3 v16 load/unload and accepted actual H3 v13 travel','handling':'Entire cargo/machinery movement during loading and unloading is H3-rendered pixels. No native handling keyframes or IK. Native overlays only lettering, labels, wheel repair and rigid travel cargo.','locale':v.LOCALE,'truckName':v.BRAND,'copy':v.MARKETING,'timeline':{'load':[.4,5.2],'travel':[5.5,9.1],'unload':[9.3,14.1],'return':[14.4,18],'loopEditorialReset':[18,20]},'sources':[{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in sources],'output':{'path':str(output.relative_to(ROOT)),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},'probe':v.f.probe(output)}
    (ASSETS/f'manifest-{v.LOCALE}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(output,flush=True)
if __name__=='__main__':main()
