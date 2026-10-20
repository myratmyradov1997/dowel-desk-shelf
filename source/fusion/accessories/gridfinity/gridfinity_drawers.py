"""Gridfinity inserts for the two DeskShelf drawers (2026-10-19).

Drawer interior (from deskshelf_v2_4.py / v2.3 drawer(); identical code), drawer-local mm,
origin = body front-left-bottom corner (global = x0 + x, -115 + y, 26 + z;
x0 = -534 left drawer, 344 right drawer):
  walls 2.0, floor 2.0  -> cavity x 2..188 (186), y 2..222 (220), floor top z = 2 (global 28), rim top z = 62 (global 88)
  rim beams on the side walls: 6 wide x 6 tall + 45 deg chamfer below -> occupy x 2..8 / 182..188 for z >= 49.8
  (the opening between the beams is 174 mm, free full width 186 below z 49.8)
  left drawer divider y 139..141 -> front compartment y 2..139 (137), back compartment y 141..222 (81)
  stop tongue on the end-leg side wall (left drawer: left wall, right drawer: right wall), y 150..193, z 8..26;
  nub sticks OUT of the drawer; when it is pressed the tongue moves INTO the drawer by ~2.5..3.3 mm
  finger scoop in the front wall, lowest point z = 38 (wall only)

Gridfinity (Zack Freedman spec): pitch 42, unit height 7.
  plain (open-bottom) baseplate: profile 0.7 / 1.8 / 2.15 (45 deg), top corner R4, height 4.65 nominal;
  here the solid is 4.60 high (ridge flats 0.1 instead of knife edges, profile below unchanged) - bins sit on the drawer floor.
  bin foot: 0.8 / 1.8 / 2.15, 41.5 x 41.5, R3.75, height 4.75; stacking lip 0.7 / 1.8 / 1.9 (tip truncated 0.5).

Layout: grid 4 columns centred in x (x 11..179, i.e. 3 mm inside the rim beams, 9 mm from the walls),
so bins of any height never touch the rim beams or the stop tongue.  Every plate is split in two halves at the
grid centre line (x = 95): a full 185 mm plate cannot pass the 174 mm opening between the rim beams.
The two halves of one plate are identical parts (the second one is turned 180 deg) and fill the drawer wall to wall.
  right drawer: 4 x 5 (168 x 210) -> plate 185 x 219 = 2 x [92.5 x 219, 2 x 5 cells]
  left front  : 4 x 3 (168 x 126) -> plate 185 x 136 = 2 x [92.5 x 136, 2 x 3 cells]
  left back   : 4 x 1 (168 x 42)  -> plate 185 x 80  = 2 x [92.5 x 80, 2 x 1 cells] (81 mm deep compartment)
Bins: 7 units (49) + lip -> 52.9 tall, top at global z 81.0 (rim 88, rods 95).
"""
import adsk.core
import adsk.fusion
import math
import os
import json

SRC = "/Users/YOU/fusion-mcp/exports/deskshelf-v2.3-modules-v2/deskshelf_v2_3_modules_v2_colorsD.f3d"
OUT = "/Users/YOU/fusion-mcp/exports/acc-gridfinity"
DOCNAME = "ACC gridfinity drawers - REVIEW"

PITCH, UNIT = 42.0, 7.0
# baseplate
BP_H = 4.60
# bin
B_CLR = 0.25            # 41.5 = 42 - 2 x 0.25
R_BIN = 3.75
FOOT_H = 4.75
H_UNITS = 7
L0 = H_UNITS * UNIT     # lip profile base (49)
H_TOP = L0 + 4.4 - 0.5  # 52.9: lip tip truncated 0.5 mm
WALL = 1.2
FLOOR_TOP = 7.0
TAB_W = 10.0
GAPZ = 0.05             # CAD air gap above the drawer floor for the interference check

DR = {"drawer_left": -534.0, "drawer_right": 344.0}
DY0, DZ0 = -115.0, 26.0
FLOOR = 2.0
GRID_X0 = 11.0
PLATE_X0, PLATE_X1, JOINT = 2.5, 187.5, 95.0


def run(context):
    app = adsk.core.Application.get()
    for d in list(app.documents):
        if d.name.startswith("ACC gridfinity"):
            d.close(False)
    im = app.importManager
    doc = im.importToNewDocument(im.createFusionArchiveImportOptions(SRC))
    doc.name = DOCNAME
    os.makedirs(OUT, exist_ok=True)
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    ash = des.appearances.itemByName("ABS - ash blue-grey")
    blue = des.appearances.itemByName("ABS - blue")
    ref_ap = des.appearances.itemByName("Reference - clear")
    VI = adsk.core.ValueInput

    def p(x, y, z):
        return adsk.core.Point3D.create(x/10, y/10, z/10)

    def mat(tx, ty, tz, rot180=False):
        m = adsk.core.Matrix3D.create()
        if rot180:
            m.setToRotation(math.pi, adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))
        m.translation = adsk.core.Vector3D.create(tx/10, ty/10, tz/10)
        return m

    def plane(comp, z):
        if abs(z) < 1e-9:
            return comp.xYConstructionPlane
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(comp.xYConstructionPlane, VI.createByString("%g mm" % z))
        pl = comp.constructionPlanes.add(inp)
        pl.isLightBulbOn = False
        return pl

    def rr_sketch(comp, z, cx, cy, hx, hy, r, name):
        sk = comp.sketches.add(plane(comp, z))
        sk.name = name
        S = lambda x, y: sk.modelToSketchSpace(p(x, y, z))
        arcs = []
        for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            ccx, ccy = cx + sx*(hx-r), cy + sy*(hy-r)
            a0 = math.atan2(sy, sx)
            pts = [(ccx + r*math.cos(a0 + d), ccy + r*math.sin(a0 + d)) for d in (-math.pi/4, 0, math.pi/4)]
            arcs.append(sk.sketchCurves.sketchArcs.addByThreePoints(S(*pts[0]), S(*pts[1]), S(*pts[2])))
        ends = []
        for a in arcs:
            ends += [a.startSketchPoint, a.endSketchPoint]

        def near(x, y):
            q = S(x, y)
            return min(ends, key=lambda sp: sp.geometry.distanceTo(q))
        segs = [((cx+hx, cy-hy+r), (cx+hx, cy+hy-r)), ((cx+hx-r, cy+hy), (cx-hx+r, cy+hy)),
                ((cx-hx, cy+hy-r), (cx-hx, cy-hy+r)), ((cx-hx+r, cy-hy), (cx+hx-r, cy-hy))]
        for a, b in segs:
            sk.sketchCurves.sketchLines.addByTwoPoints(near(*a), near(*b))
        assert sk.profiles.count == 1, (name, sk.profiles.count)
        sk.isVisible = False
        return sk

    def rr_ext(comp, z, cx, cy, hx, hy, r, height, taper, op, name, body=None):
        sk = rr_sketch(comp, z, cx, cy, hx, hy, r, name)
        inp = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
        if body is not None:
            inp.participantBodies = [body]
        ext = adsk.fusion.DistanceExtentDefinition.create(VI.createByString("%g mm" % height))
        inp.setOneSideExtent(ext, adsk.fusion.ExtentDirections.PositiveExtentDirection,
                             VI.createByString("%g deg" % taper))   # +taper expands upward (tested)
        f = comp.features.extrudeFeatures.add(inp)
        f.name = name
        return f

    def box(comp, x0, x1, y0, y1, z0, z1, op, name, body=None):
        sk = comp.sketches.add(plane(comp, z0))
        sk.name = name
        sk.sketchCurves.sketchLines.addTwoPointRectangle(sk.modelToSketchSpace(p(x0, y0, z0)), sk.modelToSketchSpace(p(x1, y1, z0)))
        sk.isVisible = False
        inp = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
        if body is not None:
            inp.participantBodies = [body]
        inp.setDistanceExtent(False, VI.createByString("%g mm" % (z1-z0)))
        f = comp.features.extrudeFeatures.add(inp)
        f.name = name
        return f

    def yz_prism(comp, pts, x0, x1, op, name, body=None):
        """profile in (y, z) extruded along x from x0 to x1"""
        base = comp.yZConstructionPlane
        sgn = base.geometry.normal.x
        at = x0 if sgn > 0 else x1
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, VI.createByString("%g mm" % (at*sgn)))
        pl = comp.constructionPlanes.add(inp)
        pl.isLightBulbOn = False
        sk = comp.sketches.add(pl)
        sk.name = name
        q = [sk.modelToSketchSpace(p(at, y, z)) for y, z in pts]
        for i in range(len(q)):
            sk.sketchCurves.sketchLines.addByTwoPoints(q[i], q[(i+1) % len(q)])
        sk.isVisible = False
        inp = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
        if body is not None:
            inp.participantBodies = [body]
        inp.setDistanceExtent(False, VI.createByString("%g mm" % (x1-x0)))
        f = comp.features.extrudeFeatures.add(inp)
        f.name = name
        return f

    def pattern(comp, body, nx, ny):
        if nx*ny == 1:
            return [body]
        col = adsk.core.ObjectCollection.create()
        col.add(body)
        rp = comp.features.rectangularPatternFeatures
        if nx > 1:
            inp = rp.createInput(col, comp.xConstructionAxis, VI.createByReal(nx), VI.createByString("42 mm"),
                                 adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
            if ny > 1:
                inp.setDirectionTwo(comp.yConstructionAxis, VI.createByReal(ny), VI.createByString("42 mm"))
        else:
            inp = rp.createInput(col, comp.yConstructionAxis, VI.createByReal(ny), VI.createByString("42 mm"),
                                 adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
        f = rp.add(inp)
        return [b for b in f.bodies] if f.bodies.count else None

    def combine(comp, target, tools, op, name):
        col = adsk.core.ObjectCollection.create()
        for t in tools:
            if t != target:
                col.add(t)
        inp = comp.features.combineFeatures.createInput(target, col)
        inp.operation = op
        inp.isKeepToolBodies = False
        f = comp.features.combineFeatures.add(inp)
        f.name = name

    def dims(b):
        bb = b.boundingBox
        return [round((getattr(bb.maxPoint, a)-getattr(bb.minPoint, a))*10, 3) for a in "xyz"]

    comps = {}

    # ---------------- baseplate halves ----------------
    def plate_half(name, length, border_y, ny):
        occ = root.occurrences.addNewComponent(mat(0, -600, 0))
        c = occ.component
        c.name = name
        W = JOINT - PLATE_X0                     # 92.5
        bx = GRID_X0 - PLATE_X0                  # 8.5 border on the wall side
        box(c, 0, W, 0, length, 0, BP_H, NEW, "Plate slab 4.6")
        plate = c.bRepBodies.item(0)
        cx, cy = bx + 21, border_y + 21
        rr_ext(c, -0.5, cx, cy, 17.65, 17.65, 0.65, 1.2, 45, NEW, "Cell cutter - lower 45 (0.7)")
        cut = c.bRepBodies.item(1)
        rr_ext(c, 0.7, cx, cy, 18.85, 18.85, 1.85, 1.8, 0, JOIN, "Cell cutter - vertical 1.8", cut)
        rr_ext(c, 2.5, cx, cy, 18.85, 18.85, 1.85, 2.5, 45, JOIN, "Cell cutter - upper 45 (2.15), R4 at top", cut)
        cutters = pattern(c, cut, 2, ny)
        cutters = [b for b in c.bRepBodies if b != plate]
        combine(c, plate, cutters, CUT, "Open Gridfinity cells")
        assert c.bRepBodies.count == 1, (name, c.bRepBodies.count)
        b = c.bRepBodies.item(0)
        b.name = name
        if ash:
            b.appearance = ash
        c.isConstructionFolderLightBulbOn = False
        comps[name] = (occ, c, b)
        return occ, c, b

    # ---------------- bins ----------------
    def make_bin(name, nx, ny):
        occ = root.occurrences.addNewComponent(mat(0, -800, 0))
        c = occ.component
        c.name = name
        rr_ext(c, 0, 21, 21, 17.8, 17.8, 0.8, 0.8, 45, NEW, "Foot - lower 45 (0.8)")
        foot = c.bRepBodies.item(0)
        rr_ext(c, 0.8, 21, 21, 18.6, 18.6, 1.6, 1.8, 0, JOIN, "Foot - vertical 1.8", foot)
        rr_ext(c, 2.6, 21, 21, 18.6, 18.6, 1.6, 2.15, 45, JOIN, "Foot - upper 45 (2.15) to 41.5 R3.75", foot)
        pattern(c, foot, nx, ny)
        feet = [b for b in c.bRepBodies]
        W, D = PITCH*nx, PITCH*ny
        hx, hy = W/2 - B_CLR, D/2 - B_CLR
        rr_ext(c, FOOT_H, W/2, D/2, hx, hy, R_BIN, H_TOP - FOOT_H, 0, NEW, "Bin body to lip tip")
        body = [b for b in c.bRepBodies if b not in feet][0]
        combine(c, body, feet, JOIN, "Feet to body")
        body = c.bRepBodies.item(0)
        z1 = L0 - 1.4
        rr_ext(c, FLOOR_TOP, W/2, D/2, hx-WALL, hy-WALL, R_BIN-WALL, z1-FLOOR_TOP, 0, CUT, "Cavity, wall 1.2", body)
        rr_ext(c, z1, W/2, D/2, hx-WALL, hy-WALL, R_BIN-WALL, 1.4, -45, CUT, "Lip support 45", body)
        rr_ext(c, L0, W/2, D/2, hx-2.6, hy-2.6, R_BIN-2.6, 0.7, 45, CUT, "Lip lower 45 (0.7)", body)
        rr_ext(c, L0+0.7, W/2, D/2, hx-1.9, hy-1.9, R_BIN-1.9, 1.8, 0, CUT, "Lip vertical 1.8", body)
        rr_ext(c, L0+2.5, W/2, D/2, hx-1.9, hy-1.9, R_BIN-1.9, 2.4, 45, CUT, "Lip upper 45 (1.9, tip cut)", body)
        yi = B_CLR + WALL
        yz_prism(c, [(yi, z1), (yi+TAB_W, z1), (yi+TAB_W, z1-1.0), (yi, z1-1.0-TAB_W)],
                 B_CLR+WALL, W-B_CLR-WALL, JOIN, "Label tab 10 mm, 45 deg underside (front wall)", body)
        assert c.bRepBodies.count == 1, (name, c.bRepBodies.count)
        b = c.bRepBodies.item(0)
        b.name = name
        if blue:
            b.appearance = blue
        c.isConstructionFolderLightBulbOn = False
        comps[name] = (occ, c, b)
        return occ, c, b

    plate_half("gf_plate_R_half_2x5", 219.0, 4.5, 5)
    plate_half("gf_plate_Lfront_half_2x3", 136.0, 5.0, 3)
    plate_half("gf_plate_Lback_half_2x1", 80.0, 19.0, 1)
    make_bin("gf_bin_1x1_7u", 1, 1)
    make_bin("gf_bin_1x2_7u", 1, 2)
    make_bin("gf_bin_2x2_7u", 2, 2)
    make_bin("gf_bin_1x3_7u_dupont", 1, 3)

    parts = {}
    for n, (o, c, b) in comps.items():
        parts[n] = {"dims_mm": dims(b), "volume_cm3": round(b.volume, 3), "solid": b.isSolid}

    # ---------------- placement ----------------
    placed = []   # (drawer, occurrence)

    def place_plate(name, drawer, y0):
        o, c, b = comps[name]
        x0 = DR[drawer]
        L = {"gf_plate_R_half_2x5": 219.0, "gf_plate_Lfront_half_2x3": 136.0, "gf_plate_Lback_half_2x1": 80.0}[name]
        gz = DZ0 + FLOOR + GAPZ
        o1 = root.occurrences.addExistingComponent(c, mat(x0 + PLATE_X0, DY0 + y0, gz))
        o2 = root.occurrences.addExistingComponent(c, mat(x0 + PLATE_X1, DY0 + y0 + L, gz, rot180=True))
        placed.extend([(drawer, o1), (drawer, o2)])

    def place_bin(name, drawer, gy0, col, row):
        o, c, b = comps[name]
        x0 = DR[drawer]
        oc = root.occurrences.addExistingComponent(c, mat(x0 + GRID_X0 + PITCH*col, DY0 + gy0 + PITCH*row, DZ0 + FLOOR + GAPZ))
        placed.append((drawer, oc))

    place_plate("gf_plate_R_half_2x5", "drawer_right", 2.5)
    place_plate("gf_plate_Lfront_half_2x3", "drawer_left", 2.5)
    place_plate("gf_plate_Lback_half_2x1", "drawer_left", 141.5)
    GR, GLF, GLB = 7.0, 7.5, 160.5
    place_bin("gf_bin_1x3_7u_dupont", "drawer_right", GR, 0, 0)
    place_bin("gf_bin_2x2_7u", "drawer_right", GR, 1, 0)
    place_bin("gf_bin_1x2_7u", "drawer_right", GR, 3, 0)
    place_bin("gf_bin_1x1_7u", "drawer_right", GR, 1, 2)
    place_bin("gf_bin_1x1_7u", "drawer_right", GR, 2, 2)
    place_bin("gf_bin_1x2_7u", "drawer_right", GR, 3, 2)
    place_bin("gf_bin_2x2_7u", "drawer_right", GR, 1, 3)
    place_bin("gf_bin_2x2_7u", "drawer_left", GLF, 0, 0)
    place_bin("gf_bin_1x2_7u", "drawer_left", GLF, 2, 0)
    place_bin("gf_bin_1x1_7u", "drawer_left", GLF, 3, 0)
    place_bin("gf_bin_1x1_7u", "drawer_left", GLB, 0, 0)
    # parking occurrences (the component masters) out of the way: hide them
    for n, (o, c, b) in comps.items():
        o.isLightBulbOn = False

    # tongue keep-out volumes (tongue moves up to ~3.5 mm into the drawer when the nub is pressed)
    keep = []
    for drawer, x0 in DR.items():
        o = root.occurrences.addNewComponent(mat(0, 0, 0))
        kc = o.component
        kc.name = "REF - tongue keep-out " + drawer
        xi = (x0 + 2.0, x0 + 6.0) if drawer == "drawer_left" else (x0 + 184.0, x0 + 188.0)
        box(kc, xi[0], xi[1], DY0 + 150, DY0 + 193, DZ0 + 8, DZ0 + 27, NEW, "keep-out 4 mm")
        if ref_ap:
            kc.bRepBodies.item(0).appearance = ref_ap
        o.isLightBulbOn = False
        keep.append((drawer, kc.bRepBodies.item(0)))

    # ---------------- checks ----------------
    tm = adsk.fusion.TemporaryBRepManager.get()

    def overlap(a, b):
        A, B = a.boundingBox, b.boundingBox
        return not any(getattr(A.maxPoint, k) <= getattr(B.minPoint, k)+1e-6 or
                       getattr(B.maxPoint, k) <= getattr(A.minPoint, k)+1e-6 for k in "xyz")

    def inter(a, b):
        if not overlap(a, b):
            return 0.0
        r = tm.copy(a)
        tm.booleanOperation(r, b, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return r.volume*1000 if r.lumps.count else 0.0

    placed_set = set(o.fullPathName for d, o in placed)
    shelf = []
    for o in root.allOccurrences:
        if not o.isVisible or o.fullPathName in placed_set or o.component.name.startswith("REF - tongue"):
            continue
        for b in o.bRepBodies:
            shelf.append((o.fullPathName, o.component.name, tm.copy(b)))
    ins = {"drawer_left": [], "drawer_right": []}
    for d, o in placed:
        ins[d].append((o.fullPathName, tm.copy(o.bRepBodies.item(0))))
    static_hits, own_hits, keep_hits = [], [], []
    alls = [(d, n, b) for d in ins for n, b in ins[d]]
    for d, n, b in alls:
        for fn, cn, sb in shelf:
            v = inter(b, sb)
            if v > 1e-4:
                static_hits.append([n, fn, round(v, 4)])
        for kd, kb in keep:
            v = inter(b, kb)
            if v > 1e-4:
                keep_hits.append([n, kd, round(v, 4)])
    for i in range(len(alls)):
        for j in range(i+1, len(alls)):
            v = inter(alls[i][2], alls[j][2])
            if v > 1e-4:
                own_hits.append([alls[i][1], alls[j][1], round(v, 4)])
    travel_hits = []
    fixed = [(fn, cn, b) for fn, cn, b in shelf if cn not in ("drawer_left", "drawer_right")]
    for d in ("drawer_left", "drawer_right"):
        dbody = [b for fn, cn, b in shelf if cn == d][0]
        moving = [(d, dbody)] + [(n, b) for n, b in ins[d]]
        for t in range(0, 146, 5):
            m = adsk.core.Matrix3D.create()
            m.translation = adsk.core.Vector3D.create(0, -t/10, 0)
            for n, b in moving:
                tb = tm.copy(b)
                tm.transform(tb, m)
                for fn, cn, fb in fixed:
                    v = inter(tb, fb)
                    if v > 1e-4:
                        travel_hits.append([d, t, n, fn, round(v, 4)])
    tops = {}
    for d in ins:
        tops[d] = round(max(b.boundingBox.maxPoint.z for n, b in ins[d])*10, 3)
    report = {"parts": parts,
              "grid": {"right": "4x5 (168x210)", "left_front": "4x3 (168x126)", "left_back": "4x1 (168x42)"},
              "insert_top_z_mm": tops, "drawer_rim_z": 88.0, "rod_bottom_z": 95.0,
              "interferences_inserts_vs_shelf_closed": static_hits,
              "interferences_between_inserts": own_hits,
              "tongue_keepout_hits": keep_hits,
              "travel_0_145_step5_hits (drawer + inserts vs fixed shelf)": travel_hits,
              "n_inserts": {d: len(ins[d]) for d in ins}}
    with open(OUT + "/gridfinity_check.json", "w") as f:
        json.dump(report, f, indent=2)

    # ---------------- exports ----------------
    os.makedirs(OUT + "/stl_raw", exist_ok=True)
    for n, (o, c, b) in comps.items():
        opt = des.exportManager.createSTLExportOptions(b, OUT + "/stl_raw/" + n + ".stl")
        opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        des.exportManager.execute(opt)
    des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT + "/deskshelf_gridfinity.f3d"))
    print(json.dumps(report, indent=1))
