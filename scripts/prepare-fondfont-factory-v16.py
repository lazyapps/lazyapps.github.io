"""Prepare dimensionally consistent still anchors for actual H3 handling."""
import importlib.util, io, json, math
from pathlib import Path
import cairosvg
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/animation/v16'
spec=importlib.util.spec_from_file_location('v15',ROOT/'scripts/compose-fondfont-factory-v15.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.configure_locale('zh-hans');v.CARGO_WIDTH=140;v.cargo_photo.cache_clear()
tracking=json.loads((v.PHYSICAL/'truck-observed.json').read_text())

def robot(x,y,receiving=False):
    base=(1040,480) if receiving else (160,480)
    l1=l2=190 if receiving else 130
    contact=v.SPRITES['fork']['contact'];pivot=v.SPRITES['fork']['pivots'][0]
    factor=v.CARGO_WIDTH/v.SPRITES['fork']['supportWidth']
    wrist=(x,y-12+(pivot[1]-contact[1])*factor)
    dx,dy=wrist[0]-base[0],wrist[1]-base[1];r=math.hypot(dx,dy)
    if not 1<r<l1+l2-1:raise ValueError((base,wrist,r))
    along=r/2;height=math.sqrt(l1*l1-along*along);sign=1 if receiving else -1
    elbow=(base[0]+dx/r*along-sign*dy/r*height,base[1]+dy/r*along+sign*dx/r*height)
    pivot=v.SPRITES['base']['pivots'][0]
    content=f'<g transform="translate({base[0]} {base[1]}) scale(.34) translate({-pivot[0]} {-pivot[1]})">{v.raster("base")}</g>'
    content+=v.link('upper',base,elbow,l1)+v.link('fore',elbow,wrist,l2)
    content+=f'<g transform="translate({x} {y-12}) scale({factor}) translate({-contact[0]} {-contact[1]})">{v.raster("fork")}</g>'
    return content

def loaded_pose(at_end=False):
    start,end=tracking['anchors'];bounds=end if at_end else start
    scale=(bounds[2]-bounds[0])/(start[2]-start[0])
    return (bounds[0]+(361-start[0])*scale,bounds[1]+(436-start[1])*scale)

def clip(at_end=False):
    start,end=tracking['anchors'];b=end if at_end else start
    scale=(b[2]-b[0])/(start[2]-start[0]);cab=b[0]+(548-start[0])*scale
    bed=b[1]+(399-start[1])*scale;left=b[0]-3;right=b[2]+3
    return f'<defs><clipPath id="behind"><rect width="{left}" height="720"/><rect x="{left}" width="{cab-left}" height="{bed}"/><rect x="{cab}" width="{right-cab}" height="{b[1]-3}"/><rect x="{right}" width="{1152-right}" height="720"/><rect x="{left}" y="535" width="{right-left}" height="185"/></clipPath><clipPath id="source"><rect x="98" y="328" width="172" height="108"/></clipPath><clipPath id="bay"><rect x="756" y="328" width="249" height="108" rx="10"/></clipPath></defs>'

def components(at_end=False,cargo='source'):
    content=clip(at_end)
    content+=f'<g clip-path="url(#behind)">{robot(190,430)}{robot(814,430,True)}</g>'
    if cargo=='source':content+=v.pallet(190,430,clip='source')
    elif cargo=='truck':content+=v.pallet(*loaded_pose(at_end),clip='behind')
    elif cargo=='bay':content+='<g clip-path="url(#bay)">'+v.pallet(850,430,clip='behind')+'</g>'
    return content

def save(name,at_end,cargo):
    content=components(at_end,cargo)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1152" height="720">{content}</svg>'
    background=Image.open(v.PHYSICAL/('end-anchor.png' if at_end else 'start-anchor.png')).convert('RGBA').resize((1152,720),Image.Resampling.LANCZOS)
    background.alpha_composite(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))
    background.convert('RGB').save(OUT/f'{name}.png')
    (OUT/f'{name}.svg').write_text(svg)

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    save('scene-first-v2',False,'source');save('scene-loaded-v2',False,'truck')
    save('unload-first-v2',True,'truck');save('unload-last-v2',True,'bay')
    (OUT/'anchor-geometry-v2.json').write_text(json.dumps({'cargoWidth':140,'scale':1,'source':[190,430],'truckStart':loaded_pose(),'truckEnd':loaded_pose(True),'receiver':[850,430],'sourceRobotLinks':[130,130],'receiverRobotLinks':[190,190],'receiverBase':[1040,480],'note':'Receiving robot base is beside the right truck cabin, joints rise visibly above the bed. No moving cargo is generated natively; all H3 anchor pallet sizes agree.'},indent=2)+'\n')
