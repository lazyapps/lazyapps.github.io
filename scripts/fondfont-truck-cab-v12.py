"""Editable automotive surface cage and projections onto its evaluated shell."""
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# Explicit section controls: height, rear, front, half-width, front corner radius.
# The cage is retained separately so these surfaces can be edited in Blender.
SECTIONS = [
    (.79, .88, 2.30, .745, .12),
    (.84, .845, 2.345, .795, .135),
    (.95, .83, 2.36, .812, .14),
    (1.26, .83, 2.345, .825, .145),
    (1.43, .83, 2.325, .83, .145),
    (1.48, .83, 2.315, .83, .145),
    (1.99, .84, 2.215, .815, .125),
    (2.22, .85, 2.165, .805, .11),
    (2.28, .87, 2.15, .80, .10),
    (2.325, .91, 2.12, .775, .09),
    (2.355, .96, 2.085, .745, .08),
    (2.365, .99, 2.06, .725, .075),
    (2.365, 1.00, 2.05, .715, .07),
]

def build_cab(mesh, paint, truck):
    vertices = []
    for height, rear, front, width, radius in SECTIONS:
        ring = []
        # The four long panel centers are deliberate controls, not beveled edges.
        for cx, cz, r, start in [
            (front-radius, width-radius, radius, 0),
            (rear+.10, width-.10, .10, 90),
            (rear+.10, -width+.10, .10, 180),
            (front-radius, -width+radius, radius, 270),
        ]:
            for j in range(5):
                angle = math.radians(start+j*90/4)
                ring.append((cx+r*math.cos(angle), height, cz+r*math.sin(angle)))
            # Subdivision's broad span between corner arcs makes a continuous panel.
        vertices.extend(ring)
    count = 20
    faces = []
    for row in range(len(SECTIONS)-1):
        for j in range(count):
            a = row*count+j; b = row*count+(j+1)%count
            faces.append((a, b, b+count, a+count))
    faces.append(tuple(range((len(SECTIONS)-1)*count, len(SECTIONS)*count)))
    cab = mesh('Subdivision automotive cab shell', vertices, faces, paint, truck)
    for modifier in list(cab.modifiers):
        cab.modifiers.remove(modifier)
    # Closed top, open underside: solidification creates an actual hollow shell.
    import bmesh
    bm = bmesh.new(); bm.from_mesh(cab.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(cab.data); bm.free()
    surface = cab.modifiers.new('Editable automotive curvature', 'SUBSURF')
    surface.levels = 2; surface.render_levels = 2
    archive = bpy.data.collections.new('Editable truck surface controls')
    bpy.context.scene.collection.children.link(archive)
    cage = cab.copy(); cage.data = cab.data.copy(); cage.name = 'Cab editable quad cage'
    archive.objects.link(cage); cage.hide_render = True; cage.hide_set(True)
    archive.hide_render = True
    bpy.context.view_layer.objects.active = cab
    bpy.ops.object.modifier_apply(modifier=surface.name)
    bpy.context.view_layer.update()
    shell = BVHTree.FromObject(cab, bpy.context.evaluated_depsgraph_get())
    thickness = cab.modifiers.new('Actual pressed shell thickness', 'SOLIDIFY')
    thickness.thickness = .028; thickness.offset = -1
    bpy.ops.object.modifier_apply(modifier=thickness.name)
    cab['surface_source'] = 'Cab editable quad cage; subdivision level 2'
    return cab, cage, shell

def front_point(shell, z, height, offset=0):
    point, normal, _, _ = shell.ray_cast(Vector((3.0, -z, height)), Vector((-1, 0, 0)))
    if point is None:
        raise ValueError(f'Front control outside cab: {z}, {height}')
    point += normal*offset
    return (point.x, point.z, -point.y)

def side_point(shell, x, height, sign, offset=0):
    point, normal, _, _ = shell.ray_cast(Vector((x, -sign*1.5, height)), Vector((0, sign, 0)))
    if point is None:
        raise ValueError(f'Side control outside cab: {x}, {height}')
    point += normal*offset
    return (point.x, point.z, -point.y)

def glazing(mesh, name, outline, project, material, truck):
    a = sum(p[0] for p in outline)/len(outline)
    b = sum(p[1] for p in outline)/len(outline)
    vertices = [(a, b, 0)] + [(x,y,0) for x,y in outline]
    faces = [(0, i+1, (i+1)%len(outline)+1) for i in range(len(outline))]
    # Subdivide in parameter space, then project every vertex onto the real shell.
    # A single warped triangle fan gives glass conspicuous planar reflections.
    import bmesh
    bm = bmesh.new()
    points = [bm.verts.new(p) for p in vertices]
    for f in faces: bm.faces.new([points[i] for i in f])
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=5, use_grid_fill=True)
    bm.verts.ensure_lookup_table(); bm.verts.index_update()
    vertices = [project(v.co.x, v.co.y) for v in bm.verts]
    faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    glass = mesh(name, vertices, faces, material, truck)
    for modifier in list(glass.modifiers): glass.modifiers.remove(modifier)
    return glass
