"""MagSafe mount v3 for DeskShelf v2.3: one rod, tool-free angle change, cable laid in from the front.

User feedback on v2 (2026-10-19): the cable could not get out (closed tunnel under the rim, the
USB-C plug cannot be threaded through), and an M3x30 bolt + hex key is inconvenient. The original
Workspace Hero mount uses a printed screw. User's charger: Anker/Ugreen 25 W puck, D58 x 6,
flat face, cable leaves from the EDGE through an 8 mm wide boot.

- Clamp: C-ring D20.3 around the front rod (y = -100), open to the back, as v2 (snaps on to an
  assembled shelf from the front). The two ears behind the rod are squeezed by a PRINTED
  thumb screw M8x1.25 (knurled head D20 on top, beside tile 3) into a PRINTED M8 nut that sits
  in a hex pocket under the lower ear. Loosen by hand -> turn or slide -> tighten.
- Cup D66, pocket D58.4 x 5.5 (puck 0.5 proud), flat floor. An open notch 9.5 mm wide through
  the bottom rim, full pocket depth: the cable boot drops into it from the front.
- Print: mount face down (supports only in the pocket); screw head down; nut flat.
"""
import adsk.core
import adsk.fusion
import math
import os
import json

SRC = "/Users/YOU/fusion-mcp/exports/deskshelf-v2.3-modules-v2/deskshelf_v2_3_modules_v2_colorsD.f3d"
OUT = "/Users/YOU/fusion-mcp/exports/magsafe-mount-v3"
YR, ZR = -100.0, 105.0        # front rod centre
RI, RO = 10.15, 13.0          # clamp bore D20.3, outer
CX0, CX1 = 274.0, 304.0       # clamp width 30 on the bare rod piece x 270..328
PX, PZ = 289.0, 105.0         # puck centre
CUP_D = 66.0
PUCK_D, PUCK_T = 58.0, 6.0
POCKET_D, POCKET_T = 58.4, 5.5
BOOT_W = 8.0                  # cable boot on the puck edge
NOTCH_W = 9.5
BACKPL = 4.0
Y_CUP_BACK = -126.5
Y_FLOOR = Y_CUP_BACK - BACKPL
Y_CUP_FRONT = Y_FLOOR - POCKET_T
EAR_Y1 = -74.0
EAR_TOP_Z0, EAR_TOP_Z1 = 115.4, 120.4
EAR_BOT_Z0, EAR_BOT_Z1 = 84.6, 94.6
BOLT_Y = -83.5
HOLE_D = 8.8                  # clearance for the M8 screw
NUT_AF, NUT_H = 13.0, 7.0
POCKET_AF, POCKET_TOP = 13.3, 91.8
HEAD_D, HEAD_H = 20.0, 8.0
SHAFT_L = 34.0
SCREW_SHRINK = 0.95           # radial scale of the printed screw: M8 -> 7.6 major, 0.2 mm play per side


def run(context):
    app = adsk.core.Application.get()
    for d in list(app.documents):
        if d.name.startswith("DeskShelf v2.3 + MagSafe v3"):
            d.close(False)
    im = app.importManager
    doc = im.importToNewDocument(im.createFusionArchiveImportOptions(SRC))
    doc.name = "DeskShelf v2.3 + MagSafe v3 - REVIEW"
    os.makedirs(OUT, exist_ok=True)
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    ash = des.appearances.itemByName("ABS - ash blue-grey")
    ref_ap = des.appearances.itemByName("Reference - clear")

    def p(x, y, z):
        return adsk.core.Point3D.create(x/10, y/10, z/10)

    def component(name, tx=0.0, ty=0.0, tz=0.0, flip=False):
        m = adsk.core.Matrix3D.create()
        if flip:      # 180 deg about x: print orientation (head down) -> assembly (head up)
            m.setToRotation(math.pi, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Point3D.create(0, 0, 0))
        m.translation = adsk.core.Vector3D.create(tx/10, ty/10, tz/10)
        occ = root.occurrences.addNewComponent(m)
        occ.component.name = name
        return occ, occ.component

    def plane(comp, kind, offset=0):
        base = {"xy": comp.xYConstructionPlane, "yz": comp.yZConstructionPlane, "xz": comp.xZConstructionPlane}[kind]
        if not offset:
            return base
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, adsk.core.ValueInput.createByString("%g mm" % offset))
        result = comp.constructionPlanes.add(inp)
        result.isLightBulbOn = False
        return result

    def poly(comp, pl, coords, name):
        sk = comp.sketches.add(pl)
        sk.name = name
        pts = [sk.modelToSketchSpace(p(*q)) for q in coords]
        for i, q in enumerate(pts):
            sk.sketchCurves.sketchLines.addByTwoPoints(q, pts[(i+1) % len(pts)])
        assert sk.profiles.count == 1, (name, sk.profiles.count)
        return sk

    def ext(comp, sk, length, op, name):
        inp = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
        if op != NEW:
            inp.participantBodies = [comp.bRepBodies.item(0)]
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByString("%g mm" % length))
        f = comp.features.extrudeFeatures.add(inp)
        f.name = name
        sk.isVisible = False
        return f

    AXIS = {"xy": 2, "yz": 0, "xz": 1}

    def prism(comp, kind, pts2, a0, a1, op, name):
        base = {"xy": comp.xYConstructionPlane, "yz": comp.yZConstructionPlane, "xz": comp.xZConstructionPlane}[kind]
        n = base.geometry.normal
        sgn = [n.x, n.y, n.z][AXIS[kind]]
        at = a0 if sgn > 0 else a1
        pl = plane(comp, kind, at*sgn)

        def to3(u, v):
            if kind == "xz":
                return (u, at, v)
            if kind == "yz":
                return (at, u, v)
            return (u, v, at)
        sk = poly(comp, pl, [to3(u, v) for u, v in pts2], name)
        return ext(comp, sk, a1-a0, op, name)

    def box(comp, x0, x1, y0, y1, z0, z1, op=NEW, name="Box"):
        return prism(comp, "xy", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, op, name)

    def circle_pts(cu, cv, r, n=96):
        return [(cu+r*math.cos(2*math.pi*k/n), cv+r*math.sin(2*math.pi*k/n)) for k in range(n)]

    def hex_pts(cu, cv, af):
        r = af/math.sqrt(3)
        return [(cu+r*math.cos(math.radians(60*k)), cv+r*math.sin(math.radians(60*k))) for k in range(6)]

    def disc(comp, r, z0, z1, op, name, cx=0.0, cy=0.0):
        sk = comp.sketches.add(plane(comp, "xy", z0))
        sk.name = name
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(cx, cy, z0)), r/10)
        return ext(comp, sk, z1-z0, op, name)

    def thread(comp, body, internal, r_mm):
        faces = [f for f in body.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType
                 and abs(f.geometry.radius*10 - r_mm) < 0.01]
        assert len(faces) == 1, ("thread face", len(faces))
        tf = comp.features.threadFeatures
        info = tf.createThreadInfo(internal, "ISO Metric profile", "M8x1.25", "6H" if internal else "6g")
        inp = tf.createInput(faces[0], info)
        inp.isModeled = True
        inp.isFullLength = True
        return tf.add(inp)

    # ---------------- the mount ----------------
    occ, c = component("magsafe_mount_v3")
    prism(c, "xz", circle_pts(PX, PZ, CUP_D/2), Y_CUP_FRONT, Y_CUP_BACK, NEW, "Round cup D66")
    box(c, CX0, CX1, Y_CUP_BACK-0.5, YR-11.0, ZR-12.0, ZR+12.0, JOIN, "Neck: cup to clamp")
    a0, a1 = 80.0, 280.0
    angs = [a0+(a1-a0)*k/60.0 for k in range(61)]
    ring = [(YR+RO*math.cos(math.radians(a)), ZR+RO*math.sin(math.radians(a))) for a in angs]
    ring += [(YR+RI*math.cos(math.radians(a)), ZR+RI*math.sin(math.radians(a))) for a in reversed(angs)]
    prism(c, "yz", ring, CX0, CX1, JOIN, "C-clamp on the front rod, open to the back")
    box(c, CX0, CX1, YR-1.0, EAR_Y1, EAR_TOP_Z0, EAR_TOP_Z1, JOIN, "Upper ear")
    box(c, CX0, CX1, YR-1.0, EAR_Y1, EAR_BOT_Z0, EAR_BOT_Z1, JOIN, "Lower ear (carries the nut)")
    bx = (CX0+CX1)/2
    prism(c, "xy", circle_pts(bx, BOLT_Y, HOLE_D/2, 48), EAR_BOT_Z0-1, EAR_TOP_Z1+1, CUT, "M8 clearance hole")
    prism(c, "xy", hex_pts(bx, BOLT_Y, POCKET_AF), EAR_BOT_Z0-1, POCKET_TOP, CUT, "Printed M8 nut pocket, from below")
    prism(c, "xz", circle_pts(PX, PZ, POCKET_D/2), Y_CUP_FRONT-0.5, Y_FLOOR, CUT, "Puck pocket D58.4")
    box(c, PX-NOTCH_W/2, PX+NOTCH_W/2, Y_CUP_FRONT-0.5, Y_FLOOR, PZ-CUP_D/2-1, PZ-POCKET_D/2+1, CUT,
        "Open cable notch in the bottom rim")
    body = c.bRepBodies.item(0)
    assert c.bRepBodies.count == 1 and body.isSolid
    body.name = "magsafe_mount_v3"

    # ---------------- printed thumb screw (modelled in print orientation: head on the bed) ----------------
    head_top = EAR_TOP_Z1 + HEAD_H
    socc, sc = component("magsafe_v3_screw", bx, BOLT_Y, head_top, flip=True)
    prism(sc, "xy", circle_pts(0, 0, HEAD_D/2), 0, HEAD_H, NEW, "Knurled head D20")
    for k in range(12):
        a = 2*math.pi*k/12
        prism(sc, "xy", circle_pts(10.6*math.cos(a), 10.6*math.sin(a), 1.8, 24), -1, HEAD_H+1, CUT, "Grip flute")
    disc(sc, 4.0, HEAD_H, HEAD_H+SHAFT_L, JOIN, "Shaft D8")
    sbody = sc.bRepBodies.item(0)
    thread(sc, sbody, False, 4.0)
    sci = sc.features.scaleFeatures.createInput(adsk.core.ObjectCollection.createWithArray([sbody]),
                                                sc.originConstructionPoint, adsk.core.ValueInput.createByReal(1.0))
    sci.setToNonUniform(adsk.core.ValueInput.createByReal(SCREW_SHRINK), adsk.core.ValueInput.createByReal(SCREW_SHRINK),
                        adsk.core.ValueInput.createByReal(1.0))
    sc.features.scaleFeatures.add(sci)
    sbody = sc.bRepBodies.item(0)
    sbody.name = "magsafe_v3_screw"

    # ---------------- printed nut ----------------
    nocc, nc = component("magsafe_v3_nut", bx, BOLT_Y, POCKET_TOP-0.1-NUT_H)
    prism(nc, "xy", hex_pts(0, 0, NUT_AF), 0, NUT_H, NEW, "Hex nut AF13")
    disc(nc, 4.0, -1, NUT_H+1, CUT, "Hole D8")
    nbody = nc.bRepBodies.item(0)
    thread(nc, nbody, True, 4.0)
    nbody = nc.bRepBodies.item(0)
    nbody.name = "magsafe_v3_nut"

    for comp, b in ((c, body), (sc, sbody), (nc, nbody)):
        if ash:
            b.appearance = ash
        for sk in comp.sketches:
            sk.isVisible = False
        comp.isConstructionFolderLightBulbOn = False

    def ref(name, build):
        o, rc = component("REF - " + name)
        build(rc)
        for b in rc.bRepBodies:
            if ref_ap:
                b.appearance = ref_ap
        for sk in rc.sketches:
            sk.isVisible = False
        rc.isConstructionFolderLightBulbOn = False
        return o
    y_face = Y_CUP_FRONT - (PUCK_T-POCKET_T)

    def puck(rc):
        prism(rc, "xz", circle_pts(PX, PZ, PUCK_D/2), y_face, y_face+PUCK_T, NEW, "puck")
        box(rc, PX-BOOT_W/2, PX+BOOT_W/2, y_face+0.5, y_face+PUCK_T-0.5, PZ-PUCK_D/2-8, PZ-PUCK_D/2+1, JOIN, "cable boot")
    ref("Puck 58x6 with edge cable boot", puck)
    PH_W, PH_H, PH_T = 76.0, 152.0, 11.0
    ref("Phone in case 76x152x11", lambda rc: box(rc, PX-PH_W/2, PX+PH_W/2, y_face-PH_T, y_face, PZ-PH_H/2, PZ+PH_H/2, NEW, "phone"))

    parts = {}
    for comp_name, b in (("magsafe_mount_v3", body), ("magsafe_v3_screw", sbody), ("magsafe_v3_nut", nbody)):
        stl = OUT + "/" + comp_name + ".stl"
        opt = des.exportManager.createSTLExportOptions(b, stl)
        opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        des.exportManager.execute(opt)
        bb = b.boundingBox
        parts[comp_name] = {"dims_mm": [round((getattr(bb.maxPoint, a)-getattr(bb.minPoint, a))*10, 2) for a in "xyz"],
                            "volume_cm3": round(b.volume, 3)}

    tm = adsk.fusion.TemporaryBRepManager.get()
    items = []
    for o in root.allOccurrences:
        if not o.isVisible:
            continue
        for b in o.bRepBodies:
            items.append((o.component.name, tm.copy(b)))

    def overlap(a, b):
        A, B = a.boundingBox, b.boundingBox
        return not any(getattr(A.maxPoint, k) <= getattr(B.minPoint, k)+1e-6 or
                       getattr(B.maxPoint, k) <= getattr(A.minPoint, k)+1e-6 for k in "xyz")

    def inter(a, b):
        if not overlap(a, b):
            return 0.0
        rr = tm.copy(a)
        tm.booleanOperation(rr, b, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return rr.volume*1000 if rr.lumps.count else 0.0

    NEWN = ("magsafe_mount_v3", "magsafe_v3_", "REF - Puck", "REF - Phone")
    new = [(n, b) for n, b in items if n.startswith(NEWN)]
    rest = [(n, b) for n, b in items if not n.startswith(NEWN)]
    hits = [[n, m, round(inter(b, mb), 3)] for n, b in new for m, mb in rest if inter(b, mb) > 1e-3]
    own = [[new[i][0], new[j][0], round(inter(new[i][1], new[j][1]), 3)]
           for i in range(len(new)) for j in range(i+1, len(new)) if inter(new[i][1], new[j][1]) > 1e-3]
    drawer_hits = []
    dr = next(b for n, b in items if n == "drawer_right")
    for travel in range(0, 150, 5):
        t = tm.copy(dr)
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(0, -travel/10, 0)
        tm.transform(t, m)
        for n, b in new:
            v = inter(t, b)
            if v > 1e-3:
                drawer_hits.append([n, travel, round(v, 3)])
    others = [(n, b) for n, b in rest if not n.startswith("REF - wall")]
    tilt = {}
    for deg in range(-40, 41, 5):
        m = adsk.core.Matrix3D.create()
        m.setToRotation(math.radians(deg), adsk.core.Vector3D.create(-1, 0, 0), p(300, YR, ZR))
        hit = []
        for n, b in new:
            t = tm.copy(b)
            tm.transform(t, m)
            for on, ob in others:
                v = inter(t, ob)
                if v > 1e-3:
                    hit.append([n, on, round(v, 2)])
        tilt[str(deg)] = hit
    slide = {}
    for dx in (-4, -2, 0, 4, 8, 12, 16):
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(dx/10, 0, 0)
        hit = []
        for n, b in new:
            t = tm.copy(b)
            tm.transform(t, m)
            for on, ob in others:
                if on.startswith("WOOD"):
                    continue
                v = inter(t, ob)
                if v > 1e-3:
                    hit.append([n, on, round(v, 2)])
        slide[str(dx)] = hit
    report = {"parts": parts, "interferences_new_vs_assembly": hits, "interferences_between_new_parts": own,
              "drawer_right_travel": drawer_hits, "tilt_about_front_rod_deg": tilt, "slide_along_rod_mm": slide,
              "clamp": {"bore_mm": 2*RI, "opening_chord_mm": round(2*RI*math.sin(math.radians(80)), 2),
                        "screw": "printed M8x1.25, radial scale %.2f" % SCREW_SHRINK, "nut": "printed M8, AF13 x 7",
                        "ear_gap_mm": round(EAR_TOP_Z0-EAR_BOT_Z1, 2)},
              "puck": [PUCK_D, PUCK_T], "pocket": [POCKET_D, POCKET_T], "notch_w": NOTCH_W,
              "phone_x": [PX-PH_W/2, PX+PH_W/2], "cup_back_y": Y_CUP_BACK}
    with open(OUT + "/magsafe_v3_check.json", "w") as f:
        json.dump(report, f, indent=2)
    des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT + "/deskshelf_v2_3_magsafe_v3.f3d"))
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
        vp.saveAsImageFile(OUT + "/" + fname, 1600, 1000)
    shot("_warmup.png", (700, -560, 330), (300, -100, 110), 40.0)
    shot("view_v3_front_right.png", (700, -560, 330), (300, -100, 110), 40.0)
    keep = ("WOOD", "magsafe_mount_v3", "magsafe_v3_", "REF - Puck")
    hidden = []
    for o in root.occurrences:
        if o.isLightBulbOn and not o.component.name.startswith(keep):
            o.isLightBulbOn = False
            hidden.append(o)
    shot("view_v3_isolated_front.png", (520, -420, 200), (289, -110, 100), 22.0)
    shot("view_v3_isolated_back.png", (430, 120, 230), (289, -95, 100), 22.0)
    shot("view_v3_isolated_below.png", (420, -330, -60), (289, -110, 95), 22.0)
    for o in hidden:
        o.isLightBulbOn = True
    try:
        os.remove(OUT + "/_warmup.png")
    except OSError:
        pass
    print(json.dumps(report, indent=1))
