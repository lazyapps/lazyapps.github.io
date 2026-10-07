"""Native iPhone roof and spatial garden, using untouched complete imagegen textures."""
import bpy, bmesh, math
from pathlib import Path
from mathutils import Vector

def build_details(root):
    out=root/'scripts/assets/fondfont/blender-v2'
    world=bpy.data.objects['Architecture'];warehouse=bpy.data.objects['Warehouse']
    if warehouse.get('phone_garden'):return
    def p(v):return (v[0],-v[2],v[1])
    def material(name,color,rough=.5,metal=0,image=None,alpha=False):
        m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF')
        c=[int(color[i:i+2],16)/255 for i in (1,3,5)];c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
        n.inputs['Base Color'].default_value=(*c,1);n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=metal
        if image:
            t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(out/image),check_existing=True);t.image.pack();m.node_tree.links.new(t.outputs['Color'],n.inputs['Base Color'])
            if alpha:m.node_tree.links.new(t.outputs['Alpha'],n.inputs['Alpha']);m.surface_render_method='DITHERED'
        return m
    def group(name,parent):
        o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;return o
    def mesh(name,verts,faces,mat,parent,at=(0,0,0),uv=None,bevel=0):
        me=bpy.data.meshes.new(name);me.from_pydata([p(v) for v in verts],[],faces);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;o.location=p(at);me.materials.append(mat)
        if uv:
            layer=me.uv_layers.new()
            for loop in me.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
        if bevel:
            mod=o.modifiers.new('Machined edge','BEVEL');mod.width=bevel;mod.segments=3
            bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
        return o
    # Remove the outlined rectangular plinth entirely, with no replacement ground-color slab.
    for o in list(world.children):
        if o.type!='MESH':continue
        if o.name.startswith('Limestone diorama') or any(m.name=='imagegen limestone plinth' for m in o.data.materials):bpy.data.objects.remove(o,do_unlink=True)
    import json
    angle=math.atan2(19,29.5);s=math.sin(angle);c=math.cos(angle)
    specs=json.loads((out/'industrial-projection.json').read_text())
    for spec in specs:
        parent=bpy.data.objects[spec['root']];art_root=group(spec['group'],parent)
        W,H=spec['size'];xmin,ymin,xmax,ymax=spec['bounds']
        scale=6.6/(xmax-xmin);cx=(xmin+xmax)/2;ground=spec['ground']
        left,head,right,floor=spec['portal'];eave=spec['roof'];glass=spec['glass']
        artwork=material(spec['material'],'#ffffff',1,0,spec['file'],True)
        def surface(px,py,z):
            projected=(ground-py)*scale-s*.55
            return ((px-cx)*scale,(projected+s*z)/c,z+1.25)
        def depth(px,py,inside):
            chimney=spec['chimney']
            if chimney and chimney[0]<=px<=chimney[1] and py<eave:return -1.3
            if py<glass:
                height=((ground-glass)*scale+s*(.71-.55))/c
                return (c*height-((ground-py)*scale-s*.55))/s
            if py<eave:return .71-(py-glass)/max(1,eave-glass)*.16
            if inside:
                if py<=spec['back_floor']:return -4.4
                return -((ground-py)*scale-s*.55)/s
            return .55
        xs=sorted(set([0,xmin,left,right,xmax,W]+(spec['chimney'] or [])))
        ys=sorted(set([0,ymin,glass,eave,head,spec['back_floor'],floor,ground,ymax,H]))
        verts=[];uv=[];faces=[]
        for x0,x1 in zip(xs,xs[1:]):
            for y0,y1 in zip(ys,ys[1:]):
                inside=x0>=left and x1<=right and y0>=head and y1<=floor
                k=len(verts)
                for px,py in [(x0,y0),(x0,y1),(x1,y1),(x1,y0)]:
                    verts.append(surface(px,py,depth((x0+x1)/2,py,inside)));uv.append((px/W,1-py/H))
                faces.append((k,k+1,k+2,k+3))
        art=mesh('Complete imagegen '+spec['root'],verts,faces,artwork,art_root,uv=uv)
        art['image_bounds']=[xmin/W,1-ymax/H,xmax/W,1-ymin/H]
        art['projection_source']=spec['file'];art['projection_yaw']=0
        px,py,sw,sh=spec['sign'];anchor=bpy.data.objects['FoundrySign' if spec['root']=='Foundry' else 'WarehouseSign']
        anchor.location=p(surface(px,py,.563));anchor['width']=sw*scale;anchor['height']=sh*scale/c
        if spec['chimney']:
            chimney=group('ChimneySmoke',parent)
            chimney.location=p(surface(sum(spec['chimney'])/2,spec['bounds'][1],-1.3))
        if spec['root']=='Warehouse':
            screen=group('PhoneScreenGlyph',parent)
            py=(ymin+glass)/2;z=depth(cx,py,False)
            pos=surface(cx+40,py,z);screen.location=p((pos[0],pos[1]+.012,pos[2]))

    # User requested actual botanical modeling instead of image cards.
    import importlib.util
    module=importlib.util.spec_from_file_location('botanicals',root/'scripts/fondfont-botanical-model.py')
    botanicals=importlib.util.module_from_spec(module);module.loader.exec_module(botanicals)
    garden=group('Garden',world)
    layout=botanicals.build_botanicals(garden)
    (out/'garden-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
    module=importlib.util.spec_from_file_location('garden_life',root/'scripts/fondfont-garden-life-model.py')
    life=importlib.util.module_from_spec(module);module.loader.exec_module(life);life.build_garden_life(world)
    warehouse['phone_garden']=True

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];out=root/'scripts/assets/fondfont/blender-v2'
    bpy.ops.wm.open_mainfile(filepath=str(out/'factory.blend'));build_details(root)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'factory.blend'))
    bpy.ops.export_scene.gltf(filepath=str(out/'factory-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)
