"""Modeled foundry and warehouse for the FondFont campus (v3).

Both buildings follow the orthographic Codex imagegen sheets in
scripts/assets/fondfont/blender-v3/imagegen/. Surfaces use seamless imagegen
tiles in world-scale UVs; small trims use flat physically based colours.
Coordinates are building-local Blender space: +X right, -Y towards the road,
+Z up. The camera has zero yaw, so the front facade and roofs carry the detail;
side and rear walls stay plain closed volumes that only cast shadows.
"""
from pathlib import Path
import math
import bpy, bmesh

ROOT = Path(__file__).resolve().parents[1]
IMAGEGEN = ROOT / 'scripts/assets/fondfont/blender-v3/imagegen'
TEXTURES = ROOT / 'scripts/assets/fondfont/blender-v3/textures'

# ---------------------------------------------------------------- materials
_materials = {}


def _image(name):
    path = TEXTURES / name
    image = bpy.data.images.get(path.name) or bpy.data.images.load(str(path), check_existing=True)
    return image


def material(name, color=(.5, .5, .5), roughness=.8, metallic=0., texture=None, emission=None, alpha=None):
    if name in _materials:
        return _materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if texture:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = _image(texture)
        tex.interpolation = 'Linear'
        m.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission[0], 1)
        bsdf.inputs['Emission Strength'].default_value = emission[1]
    m.diffuse_color = (*color, 1)
    _materials[name] = m
    return m


def palette():
    """Shared campus palette sampled from the imagegen sheets."""
    return {
        'brick': material('v3 brick', (1, 1, 1), .88, texture='brick.png'),
        'slate': material('v3 slate', (1, 1, 1), .62, texture='slate.png'),
        'limestone': material('v3 limestone', (.74, .66, .53), .82),
        'frame': material('v3 window steel', (.075, .08, .085), .42, .55),
        'glass': material('v3 glazing', (.16, .21, .25), .07),
        'iron': material('v3 cast iron', (.13, .135, .14), .48, .6),
        'plum': material('v3 plum enamel', (.17, .045, .085), .38),
        'cladding': material('v3 ivory cladding', (1, 1, 1), .5, texture='cladding.png'),
        'concrete': material('v3 concrete', (1, 1, 1), .9, texture='concrete.png'),
        'galvanized': material('v3 galvanized steel', (.62, .64, .66), .32, .85),
        'titanium': material('v3 champagne titanium', (.63, .53, .43), .28, .9),
        'bezel': material('v3 phone bezel', (.012, .012, .014), .18),
        'screen': material('v3 phone screen', (.93, .89, .80), .32),
        'rubber': material('v3 dock rubber', (.025, .025, .027), .75),
        'warm light': material('v3 interior lamp', (1, .78, .45), .5, emission=((1, .62, .28), 2.5)),
        'chimney cap': material('v3 chimney cap', (.18, .19, .2), .5, .7),
    }


# ------------------------------------------------------------------ builder
class Builder:
    """Collects quads per material; UVs are world-scale box projections."""

    def __init__(self, name, tiles):
        self.name = name
        self.tiles = tiles  # material key -> tile size in metres (None = 0..1 face UV)
        self.faces = {}

    def quad(self, key, verts, uv=None, smooth=False):
        self.faces.setdefault(key, []).append((verts, uv, smooth))

    def box(self, key, x0, x1, y0, y1, z0, z1, skip=()):
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        sides = {
            'bottom': (0, 3, 2, 1), 'top': (4, 5, 6, 7), 'front': (0, 1, 5, 4),
            'back': (2, 3, 7, 6), 'left': (3, 0, 4, 7), 'right': (1, 2, 6, 5)}
        for side, idx in sides.items():
            if side not in skip:
                self.quad(key, [v[i] for i in idx])

    def prism_y(self, key, profile, y0, y1, caps=True):
        """Extrude a closed XZ profile (counter-clockwise seen from -Y) along +Y."""
        n = len(profile)
        if caps:
            self.quad(key, [(x, y0, z) for x, z in profile])
            self.quad(key, [(x, y1, z) for x, z in reversed(profile)])
        for i in range(n):
            (ax, az), (bx, bz) = profile[i], profile[(i + 1) % n]
            self.quad(key, [(ax, y0, az), (ax, y1, az), (bx, y1, bz), (bx, y0, bz)])

    def cylinder(self, key, cx, cy, z0, z1, r, segments=16, caps=True, r1=None):
        r1 = r if r1 is None else r1
        ring = [(math.cos(2 * math.pi * i / segments), math.sin(2 * math.pi * i / segments)) for i in range(segments)]
        circ = 2 * math.pi * r
        tile = self.tiles.get(key) or 1
        for i in range(segments):
            (ax, ay), (bx, by) = ring[i], ring[(i + 1) % segments]
            u0, u1 = circ * i / segments / tile, circ * (i + 1) / segments / tile
            self.quad(key, [(cx + ax * r, cy + ay * r, z0), (cx + bx * r, cy + by * r, z0),
                            (cx + bx * r1, cy + by * r1, z1), (cx + ax * r1, cy + ay * r1, z1)],
                      [(u0, z0 / tile), (u1, z0 / tile), (u1, z1 / tile), (u0, z1 / tile)], smooth=True)
        if caps:
            self.quad(key, [(cx + x * r1, cy + y * r1, z1) for x, y in ring])
            self.quad(key, [(cx + x * r, cy + y * r, z0) for x, y in reversed(ring)])

    def rod(self, key, p0, p1, r):
        """Square-section strut between two points (used for tie rods)."""
        from mathutils import Vector
        a, c = Vector(p0), Vector(p1)
        d = (c - a).normalized()
        u = d.cross(Vector((1, 0, 0)) if abs(d.x) < .9 else Vector((0, 1, 0))).normalized() * r
        w = d.cross(u).normalized() * r
        corners = [u + w, -u + w, -u - w, u - w]
        for i in range(4):
            e, f = corners[i], corners[(i + 1) % 4]
            self.quad(key, [tuple(a + e), tuple(a + f), tuple(c + f), tuple(c + e)][::-1])

    def wall_with_openings(self, key, x0, x1, z0, z1, y, openings, depth, reveal_key=None, back_key=None):
        """A front wall plane at `y` with rectangular holes recessed by `depth`.

        openings: list of (ox0, ox1, oz0, oz1, fill_key or None[, depth[, sill]]).
        """
        xs = sorted({x0, x1, *[o[0] for o in openings], *[o[1] for o in openings]})
        zs = sorted({z0, z1, *[o[2] for o in openings], *[o[3] for o in openings]})
        for i in range(len(xs) - 1):
            for j in range(len(zs) - 1):
                cx, cz = (xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2
                if any(o[0] < cx < o[1] and o[2] < cz < o[3] for o in openings):
                    continue
                self.quad(key, [(xs[i], y, zs[j]), (xs[i + 1], y, zs[j]), (xs[i + 1], y, zs[j + 1]), (xs[i], y, zs[j + 1])])
        rk = reveal_key or key
        for ox0, ox1, oz0, oz1, fill, *extra in openings:
            yb = y + (extra[0] if extra else depth)
            sill = extra[1] if len(extra) > 1 else True
            self.quad(rk, [(ox0, y, oz0), (ox0, yb, oz0), (ox0, yb, oz1), (ox0, y, oz1)])
            self.quad(rk, [(ox1, yb, oz0), (ox1, y, oz0), (ox1, y, oz1), (ox1, yb, oz1)])
            self.quad(rk, [(ox0, y, oz1), (ox0, yb, oz1), (ox1, yb, oz1), (ox1, y, oz1)])
            if sill:
                self.quad(rk, [(ox1, y, oz0), (ox1, yb, oz0), (ox0, yb, oz0), (ox0, y, oz0)])
            if fill:
                self.quad(fill, [(ox0, yb, oz0), (ox1, yb, oz0), (ox1, yb, oz1), (ox0, yb, oz1)])

    def grid_window(self, x0, x1, z0, z1, y, cols, rows, bar=.028, depth=.018, frame=.045):
        """Steel window: outer frame and glazing bars standing proud of the glass plane."""
        f = frame
        self.box('frame', x0, x1, y - depth, y, z0, z0 + f)
        self.box('frame', x0, x1, y - depth, y, z1 - f, z1)
        self.box('frame', x0, x0 + f, y - depth, y, z0 + f, z1 - f)
        self.box('frame', x1 - f, x1, y - depth, y, z0 + f, z1 - f)
        for c in range(1, cols):
            x = x0 + (x1 - x0) * c / cols
            self.box('frame', x - bar / 2, x + bar / 2, y - depth * .7, y, z0 + f, z1 - f, skip=('top', 'bottom'))
        for r in range(1, rows):
            z = z0 + (z1 - z0) * r / rows
            self.box('frame', x0 + f, x1 - f, y - depth * .7, y, z - bar / 2, z + bar / 2, skip=('left', 'right'))

    def build(self, parent, materials, collection):
        made = []
        for key, faces in self.faces.items():
            bm = bmesh.new()
            uv_layer = bm.loops.layers.uv.new('UVMap')
            tile = self.tiles.get(key)
            for verts, uv, smooth in faces:
                bverts = [bm.verts.new(v) for v in verts]
                try:
                    face = bm.faces.new(bverts)
                except ValueError:
                    continue
                face.normal_update()
                face.smooth = smooth
                n = face.normal
                for k, loop in enumerate(face.loops):
                    p = loop.vert.co
                    if uv:
                        loop[uv_layer].uv = uv[k]
                    elif tile:
                        ax = max(range(3), key=lambda a: abs(n[a]))
                        if ax == 0:
                            u, v = (p.y if n.x > 0 else -p.y), p.z
                        elif ax == 1:
                            u, v = (-p.x if n.y > 0 else p.x), p.z
                        else:
                            u, v = p.x, (p.y if n.z > 0 else -p.y)
                        loop[uv_layer].uv = (u / tile, v / tile)
                    else:
                        loop[uv_layer].uv = (0, 0)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
            me = bpy.data.meshes.new(f'{self.name} {key}')
            bm.to_mesh(me)
            bm.free()
            me.materials.append(materials[key])
            o = bpy.data.objects.new(f'{self.name} {key}', me)
            collection.objects.link(o)
            o.parent = parent
            o['architecture_role'] = 'structure'
            made.append(o)
        return made


# ------------------------------------------------------------------ foundry
FRONT = -1.8
HALF = 3.3
BACK = .55
PHONE_BAND = .26
SIGN_Z = 2.56  # warehouse sign centre, kept below the line of sight past the eave
WAREHOUSE_EAVE = 2.96
# Phone roof footprint (building-local): 28 cm eaves at the ends, 25 cm at the front, 20 cm at the back.
_roof_y0, _roof_y1 = FRONT - .25, BACK + .2
WAREHOUSE_ROOF = {'cx': 0., 'cy': (_roof_y0 + _roof_y1) / 2, 'hx': HALF + .28, 'hy': (_roof_y1 - _roof_y0) / 2}
WAREHOUSE_ROOF.update(screen_hx=WAREHOUSE_ROOF['hx'] - .17, screen_hy=WAREHOUSE_ROOF['hy'] - .17,
                      pill_x=-WAREHOUSE_ROOF['hx'] + .55)


def build_foundry(parent, portal, collection):
    """Brick type foundry: limestone dressings, steel windows, four sawtooth bays, chimney."""
    left, right, door_h, door_plane = portal
    eave = 3.0
    b = Builder('Foundry', {'brick': .9, 'slate': 1.0, 'concrete': 1.2})
    # Facade: wall plane with recessed openings.
    upper_l = (-2.86, -2.02, 2.18, 2.78)
    upper_r = (2.02, 2.86, 2.18, 2.78)
    lower_l = (-2.86, -2.02, .5, 1.72)
    lower_r = (2.02, 2.86, .5, 1.72)
    clerestory = (left + .1, right - .1, 2.5, 2.88)
    openings = [(left, right, 0, door_h, None, door_plane - FRONT, False)]
    for o in (upper_l, upper_r, lower_l, lower_r, clerestory):
        openings.append((*o, 'glass'))
    b.wall_with_openings('brick', -HALF, HALF, 0, eave, FRONT, openings, .12, back_key='brick')
    for x0, x1, z0, z1 in (upper_l, upper_r):
        b.grid_window(x0, x1, z0, z1, FRONT + .12, 4, 2)
    for x0, x1, z0, z1 in (lower_l, lower_r):
        b.grid_window(x0, x1, z0, z1, FRONT + .12, 4, 5)
    cx0, cx1, cz0, cz1 = clerestory
    for k in range(4):
        sx0 = cx0 + (cx1 - cx0) * k / 4
        sx1 = cx0 + (cx1 - cx0) * (k + 1) / 4
        b.grid_window(sx0 + .01, sx1 - .01, cz0, cz1, FRONT + .12, 3, 2)
    # Brick segmental arches over the lower windows and limestone keystones/sills.
    for x0, x1, z0, z1 in (lower_l, lower_r):
        b.box('brick', x0 - .06, x1 + .06, FRONT - .035, FRONT, z1, z1 + .13)
        b.box('limestone', (x0 + x1) / 2 - .06, (x0 + x1) / 2 + .06, FRONT - .05, FRONT, z1 - .02, z1 + .15)
        b.box('limestone', x0 - .05, x1 + .05, FRONT - .07, FRONT + .02, z0 - .07, z0)
    for x0, x1, z0, z1 in (upper_l, upper_r):
        b.box('limestone', x0 - .05, x1 + .05, FRONT - .07, FRONT + .02, z0 - .07, z0)
    # Limestone string course under the upper windows (side bays) and base course.
    for xa, xb in ((-HALF, -1.8), (1.81, HALF)):
        b.box('limestone', xa, xb, FRONT - .04, FRONT, 1.98, 2.06)
    b.box('limestone', -HALF - .03, left, FRONT - .05, BACK + .03, 0, .18, skip=('bottom',))
    b.box('limestone', right, HALF + .03, FRONT - .05, BACK + .03, 0, .18, skip=('bottom',))
    # Pilasters: corners and door piers, brick with limestone quoin bands and caps.
    for xa, xb in ((-HALF - .04, -3.0), (3.0, HALF + .04), (-1.80, left), (right, 1.81)):
        b.box('brick', xa, xb, FRONT - .09, FRONT, .18, eave, skip=('back', 'bottom'))
        for z in (.18, 1.0, 1.98):
            b.box('limestone', xa - .015, xb + .015, FRONT - .105, FRONT, z, z + .12, skip=('back',))
        b.box('limestone', xa - .03, xb + .03, FRONT - .12, FRONT, eave - .02, eave + .1, skip=('back',))
    # Door: steel portal frame and the plum sign band.
    b.box('frame', left - .05, left, FRONT - .03, FRONT + .12, 0, 2.42, skip=('bottom',))
    b.box('frame', right, right + .05, FRONT - .03, FRONT + .12, 0, 2.42, skip=('bottom',))
    b.box('frame', left - .05, right + .05, FRONT - .03, FRONT + .02, door_h, door_h + .05)
    b.box('frame', left - .05, right + .05, FRONT - .03, FRONT + .02, 2.37, 2.42)
    sign_x = (2.90 / 2)
    b.box('plum', -sign_x, sign_x, FRONT - .04, FRONT, 1.98, 2.36)
    # Cornice and eave course.
    b.box('limestone', -HALF - .06, HALF + .06, FRONT - .13, BACK + .06, eave + .08, eave + .16)
    b.box('brick', -HALF, HALF, FRONT, BACK, eave, eave + .08, skip=('bottom', 'front'))
    # Plain closed side and rear walls; the rear leaves the loading bay corridor open.
    b.box('brick', -HALF, -HALF + .2, FRONT, BACK, .18, eave, skip=('front', 'right'))
    b.box('brick', HALF - .2, HALF, FRONT, BACK, .18, eave, skip=('front', 'left'))
    b.quad('brick', [(left, BACK, 0), (-HALF + .2, BACK, 0), (-HALF + .2, BACK, eave), (left, BACK, eave)])
    b.quad('brick', [(HALF - .2, BACK, 0), (right, BACK, 0), (right, BACK, eave), (HALF - .2, BACK, eave)])
    b.quad('brick', [(right, BACK, door_h), (left, BACK, door_h), (left, BACK, eave), (right, BACK, eave)])
    # Sawtooth roof: four bays; long slate slope with a glazed light, steep slate face.
    base = eave + .16
    teeth = 4
    width = 2 * HALF / teeth
    for i in range(teeth):
        x0 = -HALF + i * width
        peak_x, peak_z = x0 + width * .74, base + .72
        x1 = x0 + width
        ya, yb = FRONT - .05, BACK + .05
        # Brick gable infill on the front, coped in limestone.
        b.quad('brick', [(x0, FRONT, base), (x1, FRONT, base), (peak_x, FRONT, peak_z)])
        # Long slope surfaces, split to frame the skylight.
        def on_long(t):
            return x0 + (peak_x - x0) * t, base + (peak_z - base) * t
        lo, hi = .5, .9
        (ax, az), (bx, bz) = on_long(lo), on_long(hi)
        lift = .012
        for (p0, p1) in ((on_long(0), on_long(lo)), (on_long(hi), on_long(1))):
            b.quad('slate', [(p0[0], ya, p0[1]), (p0[0], yb, p0[1]), (p1[0], yb, p1[1]), (p1[0], ya, p1[1])][::-1])
        b.quad('slate', [(ax, ya, az), (ax, ya + .12, az), (bx, ya + .12, bz), (bx, ya, bz)][::-1])
        b.quad('slate', [(ax, yb - .12, az), (ax, yb, az), (bx, yb, bz), (bx, yb - .12, bz)][::-1])
        b.quad('glass', [(ax, ya + .12, az), (ax, yb - .12, az), (bx, yb - .12, bz), (bx, ya + .12, bz)][::-1])
        # Skylight glazing bars running down the slope plus a ridge cap.
        nx, nz = -(bz - az), (bx - ax)
        ln = math.hypot(nx, nz)
        nx, nz = nx / ln * lift, nz / ln * lift
        for k in range(7):
            y = ya + .12 + (yb - ya - .24) * k / 6
            b.quad('frame', [(ax + nx, y - .014, az + nz), (ax + nx, y + .014, az + nz), (bx + nx, y + .014, bz + nz), (bx + nx, y - .014, bz + nz)][::-1])
        for t in (lo, (lo + hi) / 2, hi):
            p = on_long(t)
            b.quad('frame', [(p[0] - .02 + nx, ya + .12, p[1] + nz), (p[0] - .02 + nx, yb - .12, p[1] + nz), (p[0] + .02 + nx, yb - .12, p[1] + nz), (p[0] + .02 + nx, ya + .12, p[1] + nz)][::-1])
        b.quad('slate', [(x1, ya, base), (x1, yb, base), (peak_x, yb, peak_z), (peak_x, ya, peak_z)])
        b.box('limestone', peak_x - .05, peak_x + .05, ya - .02, yb + .02, peak_z - .03, peak_z + .05)
        # Coping along the gable edges.
        for (p0, p1) in (((x0, base), (peak_x, peak_z)), ((peak_x, peak_z), (x1, base))):
            dx, dz = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(dx, dz)
            ox, oz = -dz / ln * .05, dx / ln * .05
            b.quad('limestone', [(p0[0], FRONT - .07, p0[1] + .0), (p1[0], FRONT - .07, p1[1]), (p1[0] + ox, FRONT - .07, p1[1] + oz), (p0[0] + ox, FRONT - .07, p0[1] + oz)])
            b.quad('limestone', [(p0[0] + ox, FRONT - .07, p0[1] + oz), (p1[0] + ox, FRONT - .07, p1[1] + oz), (p1[0] + ox, FRONT + .02, p1[1] + oz), (p0[0] + ox, FRONT + .02, p0[1] + oz)])
        # Rear gable closes the volume for shadows.
        b.quad('brick', [(x1, BACK, base), (x0, BACK, base), (peak_x, BACK, peak_z)])
    # Gable posts with stone caps at each valley, like the pilasters below.
    for i in range(teeth + 1):
        x = -HALF + i * width
        xa, xb = x - .11, x + .11
        b.box('brick', xa, xb, FRONT - .09, FRONT + .14, base, base + .42, skip=('bottom',))
        b.box('limestone', xa - .025, xb + .025, FRONT - .115, FRONT + .165, base + .42, base + .5)
    # Downpipes with hopper heads.
    for x in (-2.955, 2.955):
        b.cylinder('iron', x, FRONT - .07, .02, eave + .02, .03, 10)
        b.box('iron', x - .06, x + .06, FRONT - .14, FRONT - .01, eave - .1, eave + .06)
        for z in (.7, 1.5, 2.3):
            b.box('iron', x - .045, x + .045, FRONT - .05, FRONT, z, z + .035)
    # Chimney (right rear) with iron bands and a raised cap; smoke rises from its throat.
    cx, cy = 2.94, .05
    b.box('brick', cx - .3, cx + .3, cy - .3, cy + .3, base - .2, base + .25)
    b.box('limestone', cx - .33, cx + .33, cy - .33, cy + .33, base + .25, base + .33)
    b.cylinder('brick', cx, cy, base + .33, 4.98, .2, 20, caps=False, r1=.18)
    for z in (3.9, 4.4, 4.86):
        r = .2 - (.02 * (z - base - .33) / (4.98 - base - .33))
        b.cylinder('chimney cap', cx, cy, z, z + .04, r + .012, 20)
    b.cylinder('chimney cap', cx, cy, 4.98, 5.06, .215, 20)
    b.cylinder('chimney cap', cx, cy, 5.06, 5.08, .14, 12)  # throat
    for a in range(4):
        ang = math.pi / 4 + a * math.pi / 2
        px, py = cx + math.cos(ang) * .16, cy + math.sin(ang) * .16
        b.box('chimney cap', px - .012, px + .012, py - .012, py + .012, 5.06, 5.26)
    b.cylinder('chimney cap', cx, cy, 5.26, 5.38, .27, 20, r1=.05)
    return b.build(parent, palette(), collection)


# ---------------------------------------------------------------- warehouse
def _rounded_rect(cx, cy, hx, hy, r, segments=6):
    pts = []
    for qx, qy, start in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ccx, ccy = cx + qx * (hx - r), cy + qy * (hy - r)
        for s in range(segments + 1):
            a = math.radians(start + 90 * s / segments)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def _slab(b, key, outline, z0, z1, top=True, bottom=True):
    n = len(outline)
    if top:
        b.quad(key, [(x, y, z1) for x, y in outline])
    if bottom:
        b.quad(key, [(x, y, z0) for x, y in reversed(outline)])
    for i in range(n):
        (ax, ay), (bx, by) = outline[i], outline[(i + 1) % n]
        b.quad(key, [(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], smooth=True)


def build_warehouse(parent, portal, collection):
    """Ivory corrugated warehouse with plum frame and a smartphone roof."""
    left, right, door_h, door_plane = portal
    eave = 2.96
    b = Builder('Warehouse', {'cladding': .72, 'concrete': 1.2})
    plinth = .45
    win_l = (-2.86, -1.92, 2.44, 2.72)
    win_r = (1.92, 2.86, 2.44, 2.72)
    openings = [(left, right, 0, door_h, None, door_plane - FRONT, False), (*win_l, 'glass'), (*win_r, 'glass')]
    b.wall_with_openings('cladding', -3.1, 3.1, 0, eave, FRONT, openings, .08)
    # Concrete plinth either side of the door.
    b.box('concrete', -3.12, left - .18, FRONT - .04, BACK + .02, 0, plinth, skip=('bottom',))
    b.box('concrete', right + .18, 3.12, FRONT - .04, BACK + .02, 0, plinth, skip=('bottom',))
    # Plum corner posts and door frame.
    for xa, xb in ((-HALF, -3.08), (3.08, HALF)):
        b.box('plum', xa, xb, FRONT - .05, BACK, 0, eave, skip=('bottom',))
    b.box('plum', left - .18, left, FRONT - .07, FRONT + .08, 0, door_h + .18, skip=('bottom',))
    b.box('plum', right, right + .18, FRONT - .07, FRONT + .08, 0, door_h + .18, skip=('bottom',))
    b.box('plum', left - .18, right + .18, FRONT - .07, FRONT + .08, door_h, door_h + .18)
    # Dock bumpers on concrete blocks.
    for x in (left - .36, right + .36):
        b.box('concrete', x - .16, x + .16, FRONT - .14, FRONT, 0, .5, skip=('bottom',))
        b.box('rubber', x - .1, x + .1, FRONT - .2, FRONT - .04, .5, 1.02)
        b.box('galvanized', x - .11, x + .11, FRONT - .07, FRONT, .98, 1.04)
    # Ribbon windows with warm interior lamps behind the glass.
    for x0, x1, z0, z1 in (win_l, win_r):
        b.grid_window(x0, x1, z0, z1, FRONT + .08, 3, 1, frame=.035)
        for k in range(3):
            lx = x0 + (x1 - x0) * (k + .5) / 3
            b.quad('warm light', [(lx - .1, FRONT + .075, (z0 + z1) / 2 - .012), (lx + .1, FRONT + .075, (z0 + z1) / 2 - .012),
                                  (lx + .1, FRONT + .075, (z0 + z1) / 2 + .012), (lx - .1, FRONT + .075, (z0 + z1) / 2 + .012)])
    # Sign band and canopy.
    b.box('plum', -1.62, 1.62, FRONT - .04, FRONT, SIGN_Z - .21, SIGN_Z + .21)
    b.box('galvanized', -1.62, 1.62, FRONT - .05, FRONT - .03, SIGN_Z - .21, SIGN_Z - .19)
    cz = 2.08
    b.prism_y('galvanized', [(-1.78, cz), (1.78, cz), (1.78, cz + .05), (-1.78, cz + .05)], FRONT - .5, FRONT)
    b.box('galvanized', -1.8, 1.8, FRONT - .53, FRONT - .48, cz - .04, cz + .07)
    for x in (-1.72, 1.72):
        b.rod('galvanized', (x, FRONT - .47, cz + .05), (x, FRONT, cz + .42), .014)
    # Downpipes with brackets.
    for x in (-2.98, 2.98):
        b.cylinder('galvanized', x, FRONT - .1, 0, eave + .05, .045, 12)
        for z in (.6, 1.4, 2.2):
            b.box('galvanized', x - .06, x + .06, FRONT - .1, FRONT, z, z + .05)
    # Closed side and rear walls (rear leaves the bay corridor open).
    b.box('cladding', -3.1, -2.9, FRONT, BACK, plinth, eave, skip=('front', 'right'))
    b.box('cladding', 2.9, 3.1, FRONT, BACK, plinth, eave, skip=('front', 'left'))
    b.quad('cladding', [(left, BACK, 0), (-3.08, BACK, 0), (-3.08, BACK, eave), (left, BACK, eave)])
    b.quad('cladding', [(3.08, BACK, 0), (right, BACK, 0), (right, BACK, eave), (3.08, BACK, eave)])
    b.quad('cladding', [(right, BACK, door_h), (left, BACK, door_h), (left, BACK, eave), (right, BACK, eave)])
    # Smartphone roof: a real roof slab with eaves. It overhangs the walls on every
    # side (more at the front and ends) and has a deep titanium band, so it reads as
    # the warehouse roof rather than a panel resting on it.
    r = WAREHOUSE_ROOF
    cx, cy, hx, hy, top = r['cx'], r['cy'], r['hx'], r['hy'], eave + PHONE_BAND
    _slab(b, 'titanium', _rounded_rect(cx, cy, hx, hy, .5, 8), eave, top)
    _slab(b, 'bezel', _rounded_rect(cx, cy, hx - .05, hy - .05, .45, 8), top, top + .02, bottom=False)
    _slab(b, 'screen', _rounded_rect(cx, cy, r['screen_hx'], r['screen_hy'], .34, 8), top + .02, top + .026, bottom=False)
    _slab(b, 'bezel', _rounded_rect(r['pill_x'], cy, .14, .4, .14, 6), top + .026, top + .032, bottom=False)
    return b.build(parent, palette(), collection)
