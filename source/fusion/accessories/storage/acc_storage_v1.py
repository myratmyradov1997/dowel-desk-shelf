"""DeskShelf accessories 'storage' v1 (2026-10-19): cable tray, tool rail, headphone stand.

Global mm: x along the rods, y front(-) -> back(+), z up from the desk. Rods z=105 at y -100..100.

1. Cable tray under the centre (x -266..266, y 6..117, z 42..87) in 3 segments joined by sleeve
   overlaps + 8 printed pins. It hangs on two HANGERS on the bare rod pieces x +-(281..326) of rods 4/5
   (nothing above the rods in the tile zone). Hanger = module-style comb (arches over rods 4 and 5,
   dropped from above) with a stem down through the 4/5 gap and a claw open to the front. The tray
   slides in from the front: a floor-level flange on each end segment enters the claw, a printed
   lock pin through claw + flange keeps it there.
2. Tool rail in the left bay (x -446..-364, y 36..120) on rods 4/5, top z 150.
3. Headphone stand in the left bay in front of the rail: foot on rods 1/2/3 (modules style) + post
   with a R70 saddle at z 310 (195 above the rods), tenon in the foot hub + printed cross pin.
Imports the colorsD assembly into a new document; the shelf is not changed.
"""
import adsk.core
import adsk.fusion
import math
import os
import json
import traceback

SRC = "/Users/YOU/fusion-mcp/exports/deskshelf-v2.3-modules-v2/deskshelf_v2_3_modules_v2_colorsD.f3d"
OUT = "/Users/YOU/fusion-mcp/exports/acc-storage"
DOC = "ACC storage - REVIEW"
ZC, RA = 105.0, 10.2

# ---- tray ----
T = 2.0
TY0, TY1 = 6.0, 117.0          # end segment outer y
TZ0, TZR = 42.0, 87.0          # tray bottom, rim
XW = 266.0                     # end wall outer face
XJ, OVL = 92.0, 28.0           # end segment inner end, sleeve overlap
XM = XJ + OVL                  # middle half length (120)
MG = 0.3                       # sleeve clearance
FL_X1, FL_Y1 = 311.5, 86.0     # flange tip x, flange back end y
PIN_X, PIN_Z = 106.0, (53.0, 77.0)
LOCK_X, LOCK_Y = 295.0, 75.0
# ---- hanger ----
HX0, HX1 = 281.0, 326.0        # comb x (rod clip ends at 280.5, inner leg at 328)
STX0 = 312.0                   # stem x0
HY0, HY1, HZT = 34.0, 120.0, 121.0
CLAW_Y0, CLAW_Y1 = 64.0, 88.5
# ---- tool rail ----
RX0, RX1, RY0, RY1, RZT = -446.0, -364.0, 36.0, 120.0, 150.0
# ---- headphone stand ----
FX0, FX1 = -455.0, -365.0
HUB = (-425.5, -384.5, -89.8, -60.2, 92.0, 142.0)
PX0, PX1 = -421.0, -389.0
PY = -80.0
SAD_C, SAD_RO, SAD_RI, SAD_A = 240.0, 70.0, 63.0, 40.0


def run(context):
    app = adsk.core.Application.get()
    os.makedirs(OUT, exist_ok=True)
    try:
        main(app)
    except Exception:
        with open(OUT + "/_error.txt", "w") as f:
            f.write(traceback.format_exc())
        raise


def main(app):
    for d in list(app.documents):
        if d.name.startswith("ACC storage"):
            d.close(False)
    im = app.importManager
    doc = im.importToNewDocument(im.createFusionArchiveImportOptions(SRC))
    doc.name = DOC
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    ash = des.appearances.itemByName("ABS - ash blue-grey")
    blue = des.appearances.itemByName("ABS - blue")
    ref_ap = des.appearances.itemByName("Reference - clear")
    for o in root.occurrences:      # the wall takes part in the checks
        if o.component.name == "REF - wall behind the shelf":
            o.isLightBulbOn = True
    log = []

    def p(x, y, z):
        return adsk.core.Point3D.create(x/10, y/10, z/10)

    def component(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ, occ.component

    def plane(comp, kind, offset=0):
        base = {"xy": comp.xYConstructionPlane, "yz": comp.yZConstructionPlane, "xz": comp.xZConstructionPlane}[kind]
        if not offset:
            return base
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, adsk.core.ValueInput.createByString("%g mm" % offset))
        r = comp.constructionPlanes.add(inp)
        r.isLightBulbOn = False
        return r

    AXIS = {"xy": 2, "yz": 0, "xz": 1}

    def at_plane(comp, kind, a0, a1):
        base = {"xy": comp.xYConstructionPlane, "yz": comp.yZConstructionPlane, "xz": comp.xZConstructionPlane}[kind]
        n = base.geometry.normal
        sgn = [n.x, n.y, n.z][AXIS[kind]]
        at = a0 if sgn > 0 else a1
        return plane(comp, kind, at*sgn), at

    def to3(kind, u, v, at):
        if kind == "xz":
            return (u, at, v)
        if kind == "yz":
            return (at, u, v)
        return (u, v, at)

    def ext(comp, sk, length, op, name, prof=None):
        inp = comp.features.extrudeFeatures.createInput(prof or sk.profiles.item(0), op)
        if op != NEW:
            inp.participantBodies = [comp.bRepBodies.item(0)]
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByString("%g mm" % length))
        f = comp.features.extrudeFeatures.add(inp)
        f.name = name
        sk.isVisible = False
        return f

    def prism(comp, kind, pts2, a0, a1, op, name):
        a0, a1 = min(a0, a1), max(a0, a1)
        pl, at = at_plane(comp, kind, a0, a1)
        sk = comp.sketches.add(pl)
        sk.name = name
        q = [sk.modelToSketchSpace(p(*to3(kind, u, v, at))) for u, v in pts2]
        for i in range(len(q)):
            sk.sketchCurves.sketchLines.addByTwoPoints(q[i], q[(i+1) % len(q)])
        assert sk.profiles.count == 1, (name, sk.profiles.count)
        return ext(comp, sk, a1-a0, op, name)

    def cyl(comp, kind, cu, cv, r, a0, a1, op, name):
        a0, a1 = min(a0, a1), max(a0, a1)
        pl, at = at_plane(comp, kind, a0, a1)
        sk = comp.sketches.add(pl)
        sk.name = name
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(*to3(kind, cu, cv, at))), r/10)
        return ext(comp, sk, a1-a0, op, name)

    def box(comp, x0, x1, y0, y1, z0, z1, op=NEW, name="box"):
        x0, x1 = min(x0, x1), max(x0, x1)
        return prism(comp, "xy", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, op, name)

    def stadium(cx, cy, lx, ly, n=10):
        pts = []
        if lx >= ly:
            r, d = ly/2, lx/2-ly/2
            for k in range(n+1):
                a = -math.pi/2+math.pi*k/n
                pts.append((cx+d+r*math.cos(a), cy+r*math.sin(a)))
            for k in range(n+1):
                a = math.pi/2+math.pi*k/n
                pts.append((cx-d+r*math.cos(a), cy+r*math.sin(a)))
        else:
            r, d = lx/2, ly/2-lx/2
            for k in range(n+1):
                a = math.pi*k/n
                pts.append((cx+r*math.cos(a), cy+d+r*math.sin(a)))
            for k in range(n+1):
                a = math.pi+math.pi*k/n
                pts.append((cx+r*math.cos(a), cy-d+r*math.sin(a)))
        return pts

    def arch_pts(yc, zb):
        """Module arch: open bottom, semicircle R10.2 on the rod top."""
        pts = [(yc+RA, zb-1), (yc+RA, ZC)]
        pts += [(yc+RA*math.cos(math.radians(a)), ZC+RA*math.sin(math.radians(a))) for a in range(4, 180, 4)]
        return pts + [(yc-RA, ZC), (yc-RA, zb-1)]

    def pointed_arch_pts(yc, zb, ztop=117.0):
        """Arch for long tunnels: R10.2 up to 45 deg, then 45 deg flanks, flat top (no supports)."""
        pts = [(yc+RA, zb-1), (yc+RA, ZC)]
        pts += [(yc+RA*math.cos(math.radians(a)), ZC+RA*math.sin(math.radians(a))) for a in range(5, 46, 5)]
        c45 = RA*math.cos(math.radians(45))
        h = ztop-(ZC+c45)
        pts += [(yc+c45-h, ztop), (yc-c45+h, ztop)]
        pts += [(yc+RA*math.cos(math.radians(a)), ZC+RA*math.sin(math.radians(a))) for a in range(135, 176, 5)]
        return pts + [(yc-RA, ZC), (yc-RA, zb-1)]

    def finish(comp, name, ap):
        assert comp.bRepBodies.count == 1, (comp.name, comp.bRepBodies.count)
        b = comp.bRepBodies.item(0)
        assert b.isSolid, name
        b.name = name
        if ap:
            b.appearance = ap
        for sk in comp.sketches:
            sk.isVisible = False
        comp.isConstructionFolderLightBulbOn = False
        return b

    parts = {}

    # =============================== 1. CABLE TRAY ===============================
    def tray_end(s):
        name = "tray_end_" + ("R" if s > 0 else "L")
        occ, c = component(name)
        X = lambda v: s*v
        box(c, X(XJ), X(XW), TY0, TY1, TZ0, TZR, NEW, "Shell outer")
        box(c, X(XJ-1), X(XW-T), TY0+T, TY1-T, TZ0+T, TZR+1, CUT, "Shell cavity (open towards the middle)")
        box(c, X(XW-2), X(FL_X1), TY0, FL_Y1, TZ0, TZ0+4, JOIN, "Hanging flange at floor level (rides in the hanger claw)")
        prism(c, "xz", [(X(XW-1), 45.0), (X(XW+9), 45.0), (X(XW-1), 55.0)], TY0, FL_Y1, JOIN, "Flange gusset 45 deg")
        box(c, X(XW-T-1), X(XW+1), 86, 110, 68, TZR+1, CUT, "Cable pass in the end wall (towards the rod-clip hook)")
        box(c, X(170), X(200), TY0-1, TY0+T+1, 65, TZR+1, CUT, "Front cable notch")
        prism(c, "xy", stadium(X(222), 103, 36, 14), TZ0-1, TZ0+T+1, CUT, "Floor cable exit to the desk")
        for xc in (145, 185, 225):
            for yc in (22, 40, 58, 76):
                prism(c, "xy", stadium(X(xc), yc, 30, 8, 6), TZ0-1, TZ0+T+1, CUT, "Vent slot")
        for zp in PIN_Z:
            cyl(c, "xz", X(PIN_X), zp, 2.6, TY0-1, TY0+T+1, CUT, "Pin hole D5.2 front")
            cyl(c, "xz", X(PIN_X), zp, 2.6, TY1-T-1, TY1+1, CUT, "Pin hole D5.2 back")
        cyl(c, "xy", X(LOCK_X), LOCK_Y, 2.65, TZ0-1, TZ0+5, CUT, "Lock pin hole D5.3")
        return finish(c, name, ash)

    def tray_mid():
        occ, c = component("tray_mid")
        y0, y1, z0 = TY0+T+MG, TY1-T-MG, TZ0+T+0.1
        box(c, -XM, XM, y0, y1, z0, TZR, NEW, "Shell outer (slides into the end segments)")
        box(c, -XM-1, XM+1, y0+T, y1-T, z0+T, TZR+1, CUT, "Shell cavity (open ends)")
        box(c, -15, 15, y0-1, y0+T+1, 65, TZR+1, CUT, "Front cable notch")
        prism(c, "xy", stadium(0, 103, 36, 14), z0-1, z0+T+1, CUT, "Floor cable exit to the desk")
        for xc in (-70, -35, 35, 70):
            for yc in (22, 40, 58, 76):
                prism(c, "xy", stadium(xc, yc, 30, 8, 6), z0-1, z0+T+1, CUT, "Vent slot")
        for sx in (-1, 1):
            for zp in PIN_Z:
                cyl(c, "xz", sx*PIN_X, zp, 2.6, y0-1, y0+T+1, CUT, "Pin hole D5.2 front")
                cyl(c, "xz", sx*PIN_X, zp, 2.6, y1-T-1, y1+1, CUT, "Pin hole D5.2 back")
        return finish(c, "tray_mid", ash)

    def pin_y(name, x, z, front):
        occ, c = component(name)
        if front:
            cyl(c, "xz", x, z, 4.5, TY0-1.55, TY0-0.05, NEW, "Head D9")
            cyl(c, "xz", x, z, 2.5, TY0-0.5, TY0+T+MG+T+0.55, JOIN, "Shank D5.0")
        else:
            cyl(c, "xz", x, z, 4.5, TY1+0.05, TY1+1.55, NEW, "Head D9")
            cyl(c, "xz", x, z, 2.5, TY1-T-MG-T-0.55, TY1+0.5, JOIN, "Shank D5.0")
        return finish(c, name, blue)

    def hanger(s):
        name = "tray_hanger_" + ("R" if s > 0 else "L")
        occ, c = component(name)
        X = lambda v: s*v
        prism(c, "yz", [(HY0, 92), (HY1, 92), (HY1, HZT), (HY0, HZT)], X(HX0), X(HX1), NEW, "Comb over rods 4 and 5")
        stem = [(60.2, 96), (CLAW_Y0, 92.2), (CLAW_Y0, 37), (CLAW_Y1, 37), (CLAW_Y1, 89.5), (86.0, 92.2), (89.8, 96)]
        prism(c, "yz", stem, X(STX0), X(HX1), JOIN, "Stem down through the 4/5 gap")
        box(c, X(HX0), X(HX1), CLAW_Y0, CLAW_Y1, 37.0, 41.9, JOIN, "Claw lower jaw (carries the flange)")
        box(c, X(HX0), X(STX0+2), CLAW_Y0, CLAW_Y1, 46.1, 50.0, JOIN, "Claw upper jaw (anti-tip)")
        box(c, X(HX0), X(STX0+1), FL_Y1+0.2, CLAW_Y1, 41.8, 46.2, JOIN, "Claw back stop")
        for yc in (50, 100):
            prism(c, "yz", arch_pts(yc, 92), X(HX0-1), X(HX1+1), CUT, "Rod arch")
        win = [(66, 99), (84, 99), (84, 108), (80, 112), (70, 112), (66, 108)]
        prism(c, "yz", win, X(HX0-1), X(STX0-6), CUT, "Lightening window")
        cyl(c, "xy", X(LOCK_X), LOCK_Y, 2.65, 36, 51, CUT, "Lock pin hole D5.3")
        return finish(c, name, ash)

    def lock_pin(s):
        name = "tray_lock_pin_" + ("R" if s > 0 else "L")
        occ, c = component(name)
        cyl(c, "xy", s*LOCK_X, LOCK_Y, 4.5, 50.05, 51.55, NEW, "Head D9")
        cyl(c, "xy", s*LOCK_X, LOCK_Y, 2.5, 37.5, 50.5, JOIN, "Shank D5.0")
        return finish(c, name, blue)

    parts["tray_end_R"] = tray_end(1)
    parts["tray_end_L"] = tray_end(-1)
    parts["tray_mid"] = tray_mid()
    k = 0
    for sx in (-1, 1):
        for zp in PIN_Z:
            for front in (True, False):
                k += 1
                parts["tray_pin_%d" % k] = pin_y("tray_pin_%d" % k, sx*PIN_X, zp, front)
    parts["tray_hanger_R"] = hanger(1)
    parts["tray_hanger_L"] = hanger(-1)
    parts["tray_lock_pin_R"] = lock_pin(1)
    parts["tray_lock_pin_L"] = lock_pin(-1)

    # =============================== 2. TOOL RAIL ===============================
    occ, c = component("tool_rail")
    box(c, RX0, RX1, RY0, RY1, 92, RZT, NEW, "Rail block on rods 4 and 5")
    for yc in (50, 100):
        prism(c, "yz", pointed_arch_pts(yc, 92), RX0-1, RX1+1, CUT, "Rod tunnel (pointed, prints without supports)")
    holes = [  # kind, x, y, a, b, floor z, label
        ("c", -438, 52, 6.5, 0, 121, "precision screwdriver D6.5"),
        ("c", -421, 52, 6.5, 0, 121, "precision screwdriver D6.5"),
        ("c", -400, 52, 19, 0, 121, "marker D19"),
        ("c", -378, 52, 16, 0, 121, "marker D16"),
        ("s", -429, 75, 30, 22, 94, "wire stripper 30x22"),
        ("s", -406, 75, 5.5, 17.5, 94, "caliper beam 5.5x17.5"),
        ("c", -382, 75, 9, 0, 94, "screwdriver D9"),
        ("c", -437, 102, 9, 0, 121, "screwdriver D9"),
        ("c", -419, 101, 11.5, 0, 121, "multimeter probe D11.5"),
        ("c", -404, 101, 11.5, 0, 121, "multimeter probe D11.5"),
        ("c", -386, 101, 13, 0, 121, "marker D13"),
        ("s", -432, 115.1, 14, 5.5, 94, "tweezers 14x5.5"),
        ("s", -413, 115.1, 14, 5.5, 94, "tweezers 14x5.5"),
        ("s", -394, 115.1, 14, 5.5, 94, "tweezers 14x5.5"),
    ]
    for kind, x, y, a, b, zf, label in holes:
        if kind == "c":
            cyl(c, "xy", x, y, a/2, zf, RZT+1, CUT, label)
        else:
            prism(c, "xy", stadium(x, y, a, b), zf, RZT+1, CUT, label)
    rail = finish(c, "tool_rail", ash)
    for f in rail.faces:
        bb = f.boundingBox
        if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType and bb.minPoint.z*10 > RZT-0.05:
            f.appearance = blue
    parts["tool_rail"] = rail

    # =============================== 3. HEADPHONE STAND ===============================
    occ, c = component("hp_foot")
    prism(c, "yz", [(-118, 92), (16, 92), (16, 122), (-118, 122)], FX0, FX0+4, NEW, "Rib 1")
    for y0, y1 in ((-117, -112), (-83, -77), (-28, -22), (11, 15)):
        box(c, FX0, FX1, y0, y1, 92, 115, JOIN, "Tie bar between rods (stands on the bed)")
    prism(c, "yz", [(-118, 92), (16, 92), (16, 122), (-118, 122)], FX1-4, FX1, JOIN, "Rib 2")
    x0, x1, y0, y1, z0, z1 = HUB
    box(c, x0, x1, y0, y1, z0, z1, JOIN, "Hub in the 1/2 gap")
    box(c, PX0-0.2, PX1+0.2, -86.2, -73.8, 102, z1+1, CUT, "Mortise for the post tenon")
    cyl(c, "xz", (PX0+PX1)/2, 130, 3.15, -95, -55, CUT, "Cross pin hole D6.3")
    for yc in (-100, -50, 0):
        prism(c, "yz", arch_pts(yc, 92), FX0-1, FX1+1, CUT, "Rod arch")
    parts["hp_foot"] = finish(c, "hp_foot", ash)

    occ, c = component("hp_post")
    body = [(-89.5, 142.05), (-66.5, 142.05), (-72, 262), (-72, 304), (-88, 304), (-88, 262)]
    prism(c, "yz", body, PX0, PX1, NEW, "Post, tapered")
    box(c, PX0, PX1, -86, -74, 102.2, 142.5, JOIN, "Tenon 32x12 (key into the foot hub)")
    gus = [(-88, 256), (-72, 256)]
    gus += [(PY+(SAD_RI+1.5)*math.sin(math.radians(a)), SAD_C+(SAD_RI+1.5)*math.cos(math.radians(a)))
            for a in range(int(SAD_A)-6, -int(SAD_A)+5, -4)]
    prism(c, "yz", gus, PX0, PX1, JOIN, "Gussets under the saddle")
    pl, at = at_plane(c, "yz", PX0, PX1)
    sk = c.sketches.add(pl)
    sk.name = "Saddle R70"
    arcs, lines = sk.sketchCurves.sketchArcs, sk.sketchCurves.sketchLines

    def sp(y, z):
        return sk.modelToSketchSpace(p(at, y, z))

    def arcpt(r, a):
        return (PY+r*math.sin(math.radians(a)), SAD_C+r*math.cos(math.radians(a)))
    ao = arcs.addByThreePoints(sp(*arcpt(SAD_RO, -SAD_A)), sp(*arcpt(SAD_RO, 0)), sp(*arcpt(SAD_RO, SAD_A)))
    ai = arcs.addByThreePoints(sp(*arcpt(SAD_RI, -SAD_A)), sp(*arcpt(SAD_RI, 0)), sp(*arcpt(SAD_RI, SAD_A)))

    def near(arc, q):
        a, b = arc.startSketchPoint, arc.endSketchPoint
        return a if a.geometry.distanceTo(q) < b.geometry.distanceTo(q) else b
    for a in (-SAD_A, SAD_A):
        lines.addByTwoPoints(near(ao, sp(*arcpt(SAD_RO, a))), near(ai, sp(*arcpt(SAD_RI, a))))
    assert sk.profiles.count == 1, sk.profiles.count
    ext(c, sk, PX1-PX0, JOIN, "Saddle R70 x 32 (headband rest)")
    cyl(c, "xz", (PX0+PX1)/2, 130, 3.15, -87, -73, CUT, "Cross pin hole D6.3")
    post = c.bRepBodies.item(0)
    fillet_ok = False
    try:
        face = next(f for f in post.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType
                    and abs(f.geometry.radius*10-SAD_RO) < 0.05)
        edges = adsk.core.ObjectCollection.create()
        for e in face.edges:
            edges.add(e)
        fi = c.features.filletFeatures.createInput()
        try:
            fi.edgeSetInputs.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByString("3 mm"), True)
        except Exception:
            fi.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByString("3 mm"), True)
        c.features.filletFeatures.add(fi).name = "Saddle edge rounds R3"
        fillet_ok = True
    except Exception as e:
        log.append("saddle fillet failed: %s" % e)
    post = finish(c, "hp_post", ash)
    for f in post.faces:
        if f.boundingBox.minPoint.z*10 > 285:
            f.appearance = blue
    parts["hp_post"] = post

    occ, c = component("hp_pin")
    cyl(c, "xz", (PX0+PX1)/2, 130, 5.0, -91.85, -89.85, NEW, "Head D10")
    cyl(c, "xz", (PX0+PX1)/2, 130, 3.0, -90.3, -61.0, JOIN, "Shank D6.0")
    parts["hp_pin"] = finish(c, "hp_pin", blue)

    # =============================== references (not exported) ===============================
    refs = []

    def ref_box(name, x0, x1, y0, y1, z0, z1):
        o, rc = component("REF - " + name)
        box(rc, x0, x1, y0, y1, z0, z1, NEW, name)
        finish(rc, name, ref_ap)
        refs.append(name)
        return o
    ref_box("power strip 320x50x40", -160, 160, 60, 110, 46.3, 86.3)
    ref_box("PSU brick 100x60x30 R", 150, 250, 20, 80, 44.2, 74.2)
    ref_box("PSU brick 100x60x30 L", -250, -150, 20, 80, 44.2, 74.2)
    ref_box("headphones cup front", FX0+10, FX1, -190, -152, 125, 225)
    ref_box("headphones cup back", FX0+10, FX1, -8, 30, 125, 225)
    o, rc = component("REF - headphones band")
    band = [(PY+r*math.cos(math.radians(a)), 225+r*math.sin(math.radians(a))) for r, rng in ((85.2, range(0, 181, 6)),) for a in rng]
    band += [(PY+91*math.cos(math.radians(a)), 225+91*math.sin(math.radians(a))) for a in range(180, -1, -6)]
    prism(rc, "yz", band, PX0-2, PX1+2, NEW, "band")
    finish(rc, "headphones band", ref_ap)
    refs.append("headphones band")

    # =============================== exports ===============================
    os.makedirs(OUT + "/stl", exist_ok=True)
    stl_names = ["tray_end_L", "tray_end_R", "tray_mid", "tray_pin_1", "tray_lock_pin_R", "tray_hanger_L",
                 "tray_hanger_R", "tool_rail", "hp_foot", "hp_post", "hp_pin"]
    audit = {}
    for n, b in parts.items():
        bb = b.boundingBox
        audit[n] = {"volume_cm3": round(b.volume, 2),
                    "min_mm": [round(getattr(bb.minPoint, a)*10, 2) for a in "xyz"],
                    "max_mm": [round(getattr(bb.maxPoint, a)*10, 2) for a in "xyz"]}
        if n in stl_names:
            opt = des.exportManager.createSTLExportOptions(b, OUT + "/stl/" + n + ".stl")
            opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            des.exportManager.execute(opt)

    # =============================== checks ===============================
    tm = adsk.fusion.TemporaryBRepManager.get()
    mine_names = set(parts)
    items = []
    for o in root.allOccurrences:
        if not o.isVisible:
            continue
        for b in o.bRepBodies:
            items.append((o.component.name, tm.copy(b)))
    mine = [(n, b) for n, b in items if n in mine_names]
    myref = [(n, b) for n, b in items if n.startswith("REF - ") and n[6:] in refs]
    rest = [(n, b) for n, b in items if n not in mine_names and not (n.startswith("REF - ") and n[6:] in refs)]

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

    def moved(b, dx=0.0, dy=0.0, dz=0.0):
        t = tm.copy(b)
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(dx/10, dy/10, dz/10)
        tm.transform(t, m)
        return t

    hits = [[n, m, round(v, 3)] for n, b in mine for m, mb in rest for v in [inter(b, mb)] if v > 1e-3]
    own = [[mine[i][0], mine[j][0], round(v, 3)] for i in range(len(mine)) for j in range(i+1, len(mine))
           for v in [inter(mine[i][1], mine[j][1])] if v > 1e-3]
    ref_hits = [[n, m, round(v, 3)] for n, b in myref for m, mb in mine + rest
                if not (m.startswith("REF - ") and m[6:] in refs) for v in [inter(b, mb)] if v > 1e-3]
    drawer = []
    for dn, db in [(n, b) for n, b in rest if n.startswith("drawer_")]:
        for travel in range(0, 150, 5):
            t = moved(db, dy=-travel)
            for n, b in mine:
                v = inter(t, b)
                if v > 1e-3:
                    drawer.append([dn, travel, n, round(v, 3)])
    # tray slides in from the front (hangers already on the rods)
    tray_grp = [(n, b) for n, b in mine if n.startswith(("tray_end", "tray_mid", "tray_pin"))]
    others = [(n, b) for n, b in rest + mine if not n.startswith(("tray_end", "tray_mid", "tray_pin", "tray_lock"))]
    slide = {}
    for dy in (-15, -40, -80, -130, -180):
        slide[str(dy)] = [[n, m, round(v, 3)] for n, b in tray_grp for t in [moved(b, dy=dy)]
                          for m, mb in others for v in [inter(t, mb)] if v > 1e-3]
    # hangers, rail and foot are dropped from above (like the modules)
    drop = {}
    droppers = [(n, b) for n, b in mine if n.startswith(("tray_hanger", "tool_rail", "hp_foot"))]
    for dz in (8, 20, 45, 90):
        drop[str(dz)] = [[n, m, round(v, 3)] for n, b in droppers for t in [moved(b, dz=dz)]
                         for m, mb in rest for v in [inter(t, mb)] if v > 1e-3]
    rod_bottom = 95.0
    metrics = {
        "tray_bottom_z": audit["tray_end_R"]["min_mm"][2],
        "lowest_point_z (hanger jaw)": min(audit[n]["min_mm"][2] for n in ("tray_hanger_R", "tray_hanger_L")),
        "tray_rim_below_rod_bottom_mm": round(rod_bottom-TZR, 2),
        "tray_front_y": TY0, "max_y_all_parts": max(a["max_mm"][1] for a in audit.values()),
        "nothing_above_rods_in_tile_zone": all(not (a["max_mm"][2] > 95 and a["min_mm"][0] < 270 and a["max_mm"][0] > -270)
                                               for n, a in audit.items()),
        "left_bay_parts_max_x": max(audit[n]["max_mm"][0] for n in ("tool_rail", "hp_foot", "hp_post")),
        "rail_top_above_rods_mm": RZT-115.0,
        "saddle_top_z": audit["hp_post"]["max_mm"][2], "saddle_top_above_rods_mm": round(audit["hp_post"]["max_mm"][2]-115.0, 2),
        "left_bay_parts_min_z": min(audit[n]["min_mm"][2] for n in ("tool_rail", "hp_foot")),
        "saddle_fillet": fillet_ok,
    }
    report = {"interferences_new_vs_assembly": hits, "interferences_between_new_parts": own,
              "drawer_travel_0_145_vs_new": drawer, "tray_slide_in_path_dy": slide,
              "drop_from_above_path_dz (hangers, rail, foot)": drop,
              "reference_objects_vs_parts (soft)": ref_hits, "metrics": metrics, "parts": audit, "log": log,
              "note": "Rigid CAD check. Assembly = colorsD (shelf v2.3 + modules v2) incl. the wall box at y>=122.5. "
                      "CAD rods are D20; real rods 2/4 are D19 (more play in arches)."}
    with open(OUT + "/acc_storage_check.json", "w") as f:
        json.dump(report, f, indent=2)
    des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT + "/deskshelf_acc_storage_v1.f3d"))

    # =============================== views ===============================
    for o in root.occurrences:
        if o.component.name == "REF - wall behind the shelf":
            o.isLightBulbOn = False
    vp = app.activeViewport

    def shot(fname, eye, target, ext=None):
        cam = vp.camera
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
        cam.target = p(*target)
        cam.eye = p(*eye)
        cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
        cam.isFitView = False
        cam.isSmoothTransition = False
        if ext:
            cam.viewExtents = ext
        vp.camera = cam
        vp.refresh()
        adsk.doEvents()
        vp.saveAsImageFile(OUT + "/" + fname, 1600, 1000)

    shot("_warmup.png", (-700, -1300, 750), (-120, 0, 120), 90.0)
    shot("view_all_on_shelf.png", (-700, -1300, 750), (-120, 0, 120), 90.0)
    shot("view_left_bay.png", (-150, -620, 470), (-420, 0, 175), 45.0)
    shot("view_tray_under_deck.png", (380, -760, 30), (40, 60, 75), 70.0)
    groups = {"tray": ("tray_", "REF - power strip", "REF - PSU"),
              "tool_rail": ("tool_rail",),
              "headphone_stand": ("hp_", "REF - headphones")}
    cams = {"tray": [("view_iso_tray_front.png", (520, -620, 330), (0, 60, 70), 75.0),
                     ("view_iso_tray_hanger_R.png", (470, -260, 190), (295, 75, 75), 26.0)],
            "tool_rail": [("view_iso_tool_rail.png", (-250, -230, 330), (-405, 78, 120), 25.0)],
            "headphone_stand": [("view_iso_headphone_stand.png", (-120, -560, 330), (-405, -60, 200), 42.0),
                                ("view_iso_headphone_stand_parts.png", (-180, -260, 160), (-405, -75, 135), 24.0)]}
    for g, keep in groups.items():
        hidden = []
        for o in root.occurrences:
            n = o.component.name
            if o.isLightBulbOn and not (n.startswith(keep) or n.startswith("WOOD")):
                o.isLightBulbOn = False
                hidden.append(o)
        for fname, eye, target, ex in cams[g]:
            shot(fname, eye, target, ex)
        for o in hidden:
            o.isLightBulbOn = True
    try:
        os.remove(OUT + "/_warmup.png")
    except OSError:
        pass
    print(json.dumps({k: report[k] for k in report if k != "parts"}, indent=1))
