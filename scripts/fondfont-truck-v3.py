"""Modeled FondFont delivery truck (v3), after the Codex imagegen blueprint
scripts/assets/fondfont/blender-v3/imagegen/truck-orthographic-v1.png.

A red Japanese cab-over light truck with a dropside flatbed and tandem rear
axle. The animation rig of the previous truck is kept exactly: Truck root,
Steer_*/Wheel_* pivots (radius 0.435), LoadingSideGate hinge, deck height
1.07 and the label anchors. Only mesh children are replaced.

Truck-local Blender space: +X forward, +Y towards the loading side, +Z up.
Small imagegen decals (wheel face, headlamp, tail lamp, grille) carry fine
detail; everything else is geometry with flat physically based colours.
"""
from pathlib import Path
import math
import bpy, bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / 'scripts/assets/fondfont/blender-v3/textures'

R = .435          # wheel radius (motion.mjs WHEEL_RADIUS)
DECK = 1.07       # deck top (motion.mjs DECK)
BED_X0, BED_X1 = -2.62, .80
BED_Y = .97
RAIL_TOP = 1.457
GATE_Z0 = 1.02
CAB_X0, CAB_X1 = .86, 2.40
CAB_Y = .86


# ------------------------------------------------------------ materials
def _mat(name, color, roughness=.5, metallic=0., coat=0., texture=None, alpha_clip=False):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = roughness
    b.inputs['Metallic'].default_value = metallic
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = .08
    if texture:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(str(TEXTURES / texture), check_existing=True)
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if alpha_clip:
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
            m.blend_method = 'CLIP' if hasattr(m, 'blend_method') else None
    m.diffuse_color = (*color, 1)
    return m


def materials():
    return {
        'paint': _mat('v3 truck signal red', (.70, .012, .014), .3, coat=.7),
        'charcoal': _mat('v3 truck charcoal panel', (.045, .047, .052), .55),
        'black': _mat('v3 truck satin black', (.012, .012, .014), .6),
        'rubber': _mat('v3 truck tyre rubber', (.018, .018, .02), .85),
        'bumper': _mat('v3 truck bumper grey', (.13, .135, .14), .45),
        'glass': _mat('v3 truck glazing', (.016, .022, .028), .05),
        'chrome': _mat('v3 truck bright metal', (.8, .8, .8), .18, 1.),
        'aluminium': _mat('v3 truck aluminium tank', (.72, .73, .74), .28, 1.),
        'oak': bpy.data.materials.get('imagegen oak'),
        'wheel': _mat('v3 truck wheel face', (1, 1, 1), .4, texture='truck-wheel-face.png'),
        'headlamp': _mat('v3 truck headlamp', (1, 1, 1), .15, texture='truck-headlamp.png'),
        'taillamp': _mat('v3 truck tail lamp', (1, 1, 1), .25, texture='truck-taillight.png'),
        'grille': _mat('v3 truck grille', (1, 1, 1), .5, texture='truck-grille.png'),
        'amber': _mat('v3 truck amber lens', (1., .35, .02), .2),
    }


# ------------------------------------------------------------ mesh helpers
class Mesh:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')
        self.mats = []

    def mi(self, key):
        if key not in self.mats:
            self.mats.append(key)
        return self.mats.index(key)

    def face(self, key, pts, uvs=None, smooth=False):
        vs = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(vs)
        f.material_index = self.mi(key)
        f.smooth = smooth
        for i, loop in enumerate(f.loops):
            loop[self.uv].uv = uvs[i] if uvs else (0, 0)
        return f

    def box(self, key, x0, x1, y0, y1, z0, z1, skip=()):
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        for side, idx in {'bottom': (0, 3, 2, 1), 'top': (4, 5, 6, 7), 'front': (0, 1, 5, 4), 'back': (2, 3, 7, 6),
                          'left': (3, 0, 4, 7), 'right': (1, 2, 6, 5)}.items():
            if side not in skip:
                self.face(key, [v[i] for i in idx])

    def rounded_box(self, key, x0, x1, y0, y1, z0, z1, r, segments=2):
        """Box with bevelled edges, built as its own bmesh island."""
        tmp = bmesh.new()
        bmesh.ops.create_cube(tmp, size=1)
        bmesh.ops.scale(tmp, vec=(x1 - x0, y1 - y0, z1 - z0), verts=tmp.verts)
        bmesh.ops.translate(tmp, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=tmp.verts)
        bmesh.ops.bevel(tmp, geom=list(tmp.edges), offset=r, segments=segments, affect='EDGES', profile=.5)
        self._merge(tmp, key, smooth=True)

    def cylinder(self, key, centre, axis, r, length, segments=16, caps=True, smooth=True):
        tmp = bmesh.new()
        bmesh.ops.create_cone(tmp, cap_ends=caps, segments=segments, radius1=r, radius2=r, depth=length)
        rot = Vector((0, 0, 1)).rotation_difference(Vector(axis))
        bmesh.ops.rotate(tmp, verts=tmp.verts, matrix=rot.to_matrix())
        bmesh.ops.translate(tmp, vec=centre, verts=tmp.verts)
        self._merge(tmp, key, smooth=smooth)

    def _merge(self, tmp, key, smooth=False):
        mapping = {v: self.bm.verts.new(v.co) for v in tmp.verts}
        for f in tmp.faces:
            nf = self.bm.faces.new([mapping[v] for v in f.verts])
            nf.material_index = self.mi(key)
            nf.smooth = smooth and len(f.verts) == 4 and abs(f.normal.z) < .99
            for loop in nf.loops:
                loop[self.uv].uv = (0, 0)
        tmp.free()

    def decal(self, key, corners):
        """Quad with full 0..1 UVs, corners counter-clockwise from bottom-left as seen from outside."""
        return self.face(key, corners, [(0, 0), (1, 0), (1, 1), (0, 1)])

    def finish(self, name, parent, palette, collection):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for key in self.mats:
            me.materials.append(palette[key])
        o = bpy.data.objects.new(name, me)
        collection.objects.link(o)
        o.parent = parent
        return o


# ------------------------------------------------------------ cab
def _cab_profile():
    """Side silhouette of the cab in XZ (counter-clockwise seen from -Y), with the front wheel arch."""
    pts = [(CAB_X0, .74)]
    cx, ar = 1.62, .53
    a0 = math.asin((.74 - R) / ar)
    for i in range(13):
        a = math.pi - a0 - (math.pi - 2 * a0) * i / 12
        pts.append((cx + ar * math.cos(a), R + ar * math.sin(a)))
    pts += [(CAB_X1, .74), (CAB_X1, 1.6), (CAB_X1 - .045, 2.16), (CAB_X1 - .13, 2.33), (CAB_X1 - .26, 2.365),
            (CAB_X0 + .08, 2.365), (CAB_X0, 2.30)]
    # The wheel arch points were generated rear-to-front; order the outline counter-clockwise.
    return pts


def build_cab(m):
    prof = _cab_profile()
    tmp = bmesh.new()
    n = len(prof)
    front = [tmp.verts.new((x, -CAB_Y, z)) for x, z in prof]
    back = [tmp.verts.new((x, CAB_Y, z)) for x, z in prof]
    tmp.faces.new(front[::-1])
    tmp.faces.new(back)
    for i in range(n):
        j = (i + 1) % n
        tmp.faces.new([front[i], front[j], back[j], back[i]])
    bmesh.ops.recalc_face_normals(tmp, faces=tmp.faces)
    # Round every silhouette corner and the side-to-front/roof transitions.
    edges = [e for e in tmp.edges if e.calc_face_angle(0) > math.radians(25)]
    bmesh.ops.bevel(tmp, geom=edges, offset=.085, segments=4, affect='EDGES', profile=.5, clamp_overlap=True)
    m._merge(tmp, 'paint', smooth=True)

    eps = .004
    side = lambda y, pts: [(x, y, z) for x, z in pts]
    # Black wheel-arch liner: a lip on both sides and the inner arch surface.
    cx, ar = 1.62, .53
    a0 = math.asin((.74 - R) / ar)
    arc = [math.pi - a0 - (math.pi - 2 * a0) * i / 16 for i in range(17)]
    for i in range(16):
        a, b2 = arc[i], arc[i + 1]
        p = lambda ang, rr: (cx + rr * math.cos(ang), R + rr * math.sin(ang))
        (ax, az), (bx, bz) = p(a, ar - .004), p(b2, ar - .004)
        m.face('black', [(ax, CAB_Y - .02, az), (bx, CAB_Y - .02, bz), (bx, -CAB_Y + .02, bz), (ax, -CAB_Y + .02, az)])
        for s in (-1, 1):
            (cx0, cz0), (cx1, cz1), (ox0, oz0), (ox1, oz1) = p(a, ar), p(b2, ar), p(a, ar + .05), p(b2, ar + .05)
            quad = [(cx0, s * (CAB_Y + .005), cz0), (cx1, s * (CAB_Y + .005), cz1), (ox1, s * (CAB_Y + .005), oz1), (ox0, s * (CAB_Y + .005), oz0)]
            m.face('black', quad if s < 0 else quad[::-1])
    for s in (-1, 1):
        y = s * (CAB_Y + eps)
        order = (lambda p: p) if s < 0 else (lambda p: p[::-1])
        # Side window with a raked front edge, framed in black rubber.
        win = [(1.36, 1.66), (2.22, 1.66), (2.27, 2.18), (1.36, 2.2)]
        m.face('black', order(side(y, [(1.33, 1.63), (2.25, 1.63), (2.30, 2.21), (1.33, 2.23)])))
        m.face('glass', order(side(y + s * .002, win)))
        # Door shut lines and handle.
        for x0, x1, z0, z1 in ((1.30, 1.315, .98, 2.24), (2.30, 2.315, .98, 1.6), (1.30, 2.315, .965, .98)):
            m.face('black', order(side(y + s * .002, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)])))
        m.face('black', order(side(y + s * .003, [(1.40, 1.50), (1.56, 1.50), (1.56, 1.545), (1.40, 1.545)])))
        # Corner marker lamp and step.
        m.face('amber', order(side(y + s * .003, [(2.24, 1.2), (2.33, 1.2), (2.33, 1.26), (2.24, 1.26)])))
        # Mirror arm and head.
        arm0 = Vector((2.25, s * (CAB_Y - .02), 2.05))
        head = Vector((2.43, s * 1.06, 1.88))
        m.cylinder('black', (arm0 + head) / 2, head - arm0, .012, (head - arm0).length, 6)
        m.rounded_box('black', head.x - .03, head.x + .03, head.y - .06, head.y + .06, head.z - .2, head.z + .16, .015, 1)
    # Windshield: on the raked front face, framed in black, with wipers.
    def front_pt(z, y):
        x = CAB_X1 + eps if z <= 1.6 else CAB_X1 + eps - .045 * (z - 1.6) / .56
        return (x, y, z)
    m.face('black', [front_pt(1.66, -.80), front_pt(1.66, .80), front_pt(2.2, .80), front_pt(2.2, -.80)])
    m.face('glass', [(p[0] + .002, p[1], p[2]) for p in
                     [front_pt(1.69, -.76), front_pt(1.69, .76), front_pt(2.17, .76), front_pt(2.17, -.76)]])
    for y0 in (-.55, .05):
        m.face('black', [(p[0] + .004, p[1], p[2]) for p in
                         [front_pt(1.70, y0), front_pt(1.70, y0 + .5), front_pt(1.725, y0 + .5), front_pt(1.725, y0)]])
    # Fascia: grille band, headlamps, indicator, bumper with fog lamps.
    x = CAB_X1 + eps
    m.decal('grille', [(x, -.42, 1.06), (x, .42, 1.06), (x, .42, 1.24), (x, -.42, 1.24)])
    for s in (-1, 1):
        ya, yb = sorted((s * .44, s * .80))
        # The decal's main beam is on its left; mirror it on the right lamp so main beams sit outboard.
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)] if s < 0 else [(1, 0), (0, 0), (0, 1), (1, 1)]
        m.face('headlamp', [(x, ya, 1.04), (x, yb, 1.04), (x, yb, 1.23), (x, ya, 1.23)], uv)
    m.rounded_box('bumper', 2.30, 2.47, -.88, .88, .62, .93, .03, 2)
    m.box('black', 2.36, 2.45, -.82, .82, .60, .64, skip=('top',))
    for s in (-1, 1):
        ya, yb = sorted((s * .58, s * .76))
        m.face('amber', [(2.473, ya, .80), (2.473, yb, .80), (2.473, yb, .86), (2.473, ya, .86)])
        m.face('chrome', [(2.473, ya, .69), (2.473, yb, .69), (2.473, yb, .76), (2.473, ya, .76)])
    # Rear window on the cab back.
    xb = CAB_X0 - eps
    m.face('glass', [(xb, .35, 1.86), (xb, -.35, 1.86), (xb, -.35, 2.12), (xb, .35, 2.12)])
    # Steps under the doors, behind the front wheel arch.
    for s in (-1, 1):
        y0, y1 = sorted((s * (CAB_Y - .1), s * (CAB_Y + .06)))
        m.box('black', .98, 1.16, y0, y1, .46, .5)


# ------------------------------------------------------------ chassis and bed
def build_chassis(m):
    for s in (-1, 1):
        m.box('black', -2.58, 2.2, s * .45 - .05, s * .45 + .05, .64, .86)
    for x in (-2.4, -1.3, -.2, .7, 1.9):
        m.box('black', x - .04, x + .04, -.45, .45, .68, .82, skip=('left', 'right'))
    # Fuel tank (loading side) and battery box (road side), between cab and rear axles.
    # The road-facing side (-Y) carries the silver fuel tank, as in the blueprint's side view.
    m.cylinder('aluminium', (.23, -.67, .59), (1, 0, 0), .17, .74, 20)
    for x in (-.02, .48):
        m.cylinder('black', (x, -.67, .59), (1, 0, 0), .176, .035, 20)
    m.rounded_box('black', -.08, .54, .52, .82, .43, .74, .02, 1)
    # Rear mudguards over the tandem wheels and mud flaps.
    for s in (-1, 1):
        y0, y1 = sorted((s * .72, s * 1.04))
        m.box('black', -2.33, -.24, y0, y1, .95, .985)
        m.box('black', -2.36, -2.33, y0, y1, .32, .985)
        m.box('black', -.27, -.24, y0, y1, .72, .985)
    # Rear under-run bar and tail lamps.
    m.box('bumper', -2.66, -2.58, -.9, .9, .46, .56)
    for s in (-1, 1):
        y0, y1 = sorted((s * .58, s * .88))
        m.box('black', -2.62, -2.56, y0, y1, .66, .80)
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)] if s > 0 else [(1, 0), (0, 0), (0, 1), (1, 1)]
        m.face('taillamp', [(-2.625, y1, .675), (-2.625, y0, .675), (-2.625, y0, .785), (-2.625, y1, .785)], uv)


def _dropside(m, x0, x1, y0, y1, z0, z1, posts):
    """Dropside: red frame and posts, charcoal infill, bright hinges and latches."""
    m.box('paint', x0, x1, y0, y1, z1 - .05, z1)          # top rail
    m.box('paint', x0, x1, y0, y1, z0, z0 + .055)         # bottom rail
    m.box('charcoal', x0, x1, y0 + .012, y1 - .012, z0 + .055, z1 - .05, skip=('top', 'bottom'))
    for x in posts:
        m.box('paint', x - .035, x + .035, y0 - .008, y1 + .008, z0, z1)
        m.box('chrome', x - .05, x + .05, y0 - .014, y1 + .014, z1 - .075, z1 - .035)   # latch
    for k in range(len(posts) - 1):
        for t in (.25, .75):
            x = posts[k] + (posts[k + 1] - posts[k]) * t
            m.box('chrome', x - .04, x + .04, y0 - .012, y1 + .012, z0 + .005, z0 + .05)  # hinge


def build_bed(m):
    m.box('oak', BED_X0, BED_X1, -BED_Y + .09, BED_Y - .09, DECK - .03, DECK, skip=('bottom',))
    for x in (-2.3, -1.6, -.9, -.2, .5):
        m.box('black', x - .04, x + .04, -BED_Y, BED_Y, .86, DECK - .03)
    m.box('paint', BED_X0, BED_X1, -BED_Y, BED_Y, GATE_Z0 - .06, GATE_Z0, skip=('top',))
    posts = [BED_X0 + .035, -1.48, -.34, BED_X1 - .035]
    _dropside(m, BED_X0, BED_X1, -BED_Y, -BED_Y + .09, GATE_Z0, RAIL_TOP, posts)
    # Tailgate and headboard.
    m.box('paint', BED_X0 - .02, BED_X0 + .07, -BED_Y, BED_Y, GATE_Z0, RAIL_TOP)
    m.box('charcoal', BED_X0 - .025, BED_X0, -BED_Y + .07, -.03, GATE_Z0 + .06, RAIL_TOP - .05)
    m.box('charcoal', BED_X0 - .025, BED_X0, .03, BED_Y - .07, GATE_Z0 + .06, RAIL_TOP - .05)
    m.box('paint', BED_X1 - .02, BED_X1 + .04, -BED_Y, BED_Y, GATE_Z0, 1.98)
    for y in (-.6, -.2, .2, .6):
        m.box('paint', BED_X1 + .04, BED_X1 + .06, y - .03, y + .03, 1.46, 1.98)
    return posts


def build_gate(m, gate_origin, posts):
    """Loading-side dropside in LoadingSideGate space (hinge on its bottom edge)."""
    oy, oz = gate_origin
    _dropside(m, BED_X0, BED_X1, BED_Y - .09 - oy, BED_Y - oy, 0, RAIL_TOP - oz, posts)


# ------------------------------------------------------------ wheel
def build_wheel(m):
    """One wheel, symmetric about its centre plane so all six can share it."""
    seg = 48
    half = .15
    # Tyre: rounded tread band (lathe of a rounded profile around the Y axle).
    prof = [(.37, half), (.415, half - .006), (.432, half - .03), (R, half - .06), (R, -half + .06),
            (.432, -half + .03), (.415, -half + .006), (.37, -half)]
    rings = []
    for r, y in prof:
        rings.append([m.bm.verts.new((r * math.cos(2 * math.pi * i / seg), y, r * math.sin(2 * math.pi * i / seg))) for i in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            f = m.bm.faces.new([a[i], a[j], b[j], b[i]])
            f.material_index = m.mi('rubber')
            f.smooth = True
            for loop in f.loops:
                loop[m.uv].uv = (0, 0)
    # Side faces: textured discs (steel wheel and moulded sidewall from the imagegen decal).
    for s in (-1, 1):
        ring = rings[0] if s > 0 else rings[-1]
        rim = .37
        y = s * (half - .004)
        centre = m.bm.verts.new((0, y - s * .02, 0))
        verts = [m.bm.verts.new((v.co.x, y, v.co.z)) for v in ring]
        for i in range(seg):
            j = (i + 1) % seg
            tri = [centre, verts[i], verts[j]] if s > 0 else [centre, verts[j], verts[i]]
            f = m.bm.faces.new(tri)
            f.material_index = m.mi('wheel')
            for loop in f.loops:
                c = loop.vert.co
                loop[m.uv].uv = (.5 - s * c.x / (2 * R), .5 + c.z / (2 * R))
        # Close the gap between the textured disc and the tyre lip.
        for i in range(seg):
            j = (i + 1) % seg
            quad = [ring[i], ring[j], verts[j], verts[i]] if s > 0 else [ring[j], ring[i], verts[i], verts[j]]
            f = m.bm.faces.new(quad)
            f.material_index = m.mi('rubber')
            for loop in f.loops:
                loop[m.uv].uv = (0, 0)
    bmesh.ops.recalc_face_normals(m.bm, faces=m.bm.faces)


# ------------------------------------------------------------ assembly
def build_truck(collection):
    truck = bpy.data.objects['Truck']
    for o in list(truck.children_recursive):
        if o.type == 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)
    pal = materials()
    body = Mesh()
    build_cab(body)
    build_chassis(body)
    posts = build_bed(body)
    body.finish('Truck body v3', truck, pal, collection)
    gate_empty = bpy.data.objects['LoadingSideGate']
    gate = Mesh()
    build_gate(gate, (gate_empty.location.y, gate_empty.location.z), posts)
    gate.finish('Loading side gate v3', gate_empty, pal, collection)
    wheel = Mesh()
    build_wheel(wheel)
    shared = wheel.finish('Truck wheel v3', None, pal, collection)
    data = shared.data
    bpy.data.objects.remove(shared, do_unlink=True)
    for o in bpy.data.objects:
        if o.name.startswith('Wheel_') and o.parent and o.parent.name.startswith('Steer_'):
            w = bpy.data.objects.new(f'{o.name} tyre', data)
            collection.objects.link(w)
            w.parent = o
    truck['reference'] = 'blender-v3/imagegen/truck-orthographic-v1.png'
    truck['truck_revision'] = 'modeled-v3'
    return truck
