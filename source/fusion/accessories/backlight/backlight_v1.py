"""DeskShelf backlight v1 (2026-10-19): wall-wash LED rail behind the monitor + ESP32-C3 Super Mini box.

Why the rail sits ON the tiles: the deck tiles reach y = 122 and the wall is at y = 122.5, so a strip
under the tiles can only light the wall below the shelf. The rail therefore lies on the tile tops along
the back edge (y 108.4..121.8, z 118.2..140.4) and the strip on its 45 deg face shines back-up onto the
wall behind the monitor. Nothing passes y = 122.

- 3 rail segments (212 mm, x -318..318 = 634 mm of strip). S2 (middle) drops onto dovetail tabs of S1/S3.
  Arches 7.5 mm high over all 9 cable notches of the tiles: cables slide under the rail from the front.
- 2 end brackets: snap clips D19.8 on the bare back rod (x 298..320 and -316..-296; tiles end at |x| 270,
  rod_clip at 270.5..280.5), a tongue under the rail end. R bracket has a wire notch.
- Optional diffusers (white/natural plastic only), 0.9 mm, clip on the strip lips.
- Controller box for ESP32-C3 Super Mini (22.5 x 18): own snap clip on rod 5 at x 283.5..295.5, box behind
  the rod under it, USB-C pointing down to the desk, lid with 2 snap tabs, vents, wire entry on top.
Self-contained: imports the shelf assembly, builds, checks, exports STL/f3d, renders.
"""
import adsk.core
import adsk.fusion
import math
import os
import json

SRC = "/Users/YOU/fusion-mcp/exports/deskshelf-v2.3-modules-v2/deskshelf_v2_3_modules_v2_colorsD.f3d"
OUT = "/Users/YOU/fusion-mcp/exports/acc-backlight"
DOCNAME = "ACC backlight v1 - REVIEW"

# ---- LED strip parameters ----
LED_W = 10.0          # strip width (WS2812B 60/m: 10 mm; IP65 in silicone: 12)
LED_T = 2.5           # strip thickness incl. LEDs and tape
ANG = 45.0            # strip normal above the horizontal, pointing to the wall
CH = LED_W + 0.6      # channel width between the lips
LIP_T, LIP_H = 1.2, LED_T + 1.5
G, DIF_T, HOOK_T, NB = 0.05, 0.9, 0.9, 0.9
Z0, ARCH_H, Y_MAX = 118.2, 7.5, 121.8
sA, cA = math.sin(math.radians(ANG)), math.cos(math.radians(ANG))
ARCH_TOP = Z0 + ARCH_H
Z0F = ARCH_TOP + 1.3 + LIP_T * cA
Y0 = Y_MAX - ((LIP_T + G + HOOK_T) * sA + (LIP_H + G + DIF_T) * cA)
X_L, X_R = -318.0, 318.0
SEGS = {"S1": (-318.0, -106.1), "S2": (-105.9, 105.9), "S3": (106.1, 318.0)}
NOTCHES = [(-220, 8), (-180, 12), (-140, 16), (-40, 8), (0, 12), (40, 16), (140, 8), (180, 12), (220, 16)]
# ---- rod / clips ----
YR, ZR = 100.0, 105.0
RI, RO = 9.9, 12.4     # snap bore D19.8 (good rod 20.0-20.1), wall 2.5
A0, A1 = -10.0, 190.0  # ring covers the top, opens downwards (pushed down onto the rod)
BR_R = (298.0, 320.0)
BR_L = (-316.0, -296.0)
TONGUE_Y, TONGUE_Z = (111.0, 115.0), (118.15, 121.15)
SLOT_Y, SLOT_Z = (110.8, 115.2), (Z0 - 1.0, 121.4)
WIRE_X = (308.0, 316.0)
# ---- controller box ----
BX0, BX1, BY0, BY1, BZ0, BZ1 = 283.5, 326.0, 110.4, 121.8, 60.4, 97.6
CX0, CX1, CY1, CZ0, CZ1 = 285.1, 324.4, 120.4, 62.0, 96.0
BRING = (283.5, 295.5)


def P(s, n):
    return (Y0 - s * sA + n * cA, Z0F + s * cA + n * sA)


def rail_section():
    v3, v10 = P(-LIP_T, 0), P(CH + LIP_T, 0)
    return [(v10[0], Z0), (v3[0], Z0), v3, P(-LIP_T, 1.0), P(-LIP_T + 0.4, 1.5), P(-LIP_T, 2.0), P(-LIP_T, LIP_H),
            P(0, LIP_H), P(0, 0), P(CH, 0), P(CH, LIP_H), P(CH + LIP_T, LIP_H),
            P(CH + LIP_T, 2.0), P(CH + LIP_T - 0.4, 1.5), P(CH + LIP_T, 1.0), v10]


def diffuser_section():
    a, b = -(LIP_T + G), CH + LIP_T + G
    top = LIP_H + G + DIF_T
    return [P(a - HOOK_T, NB), P(a - HOOK_T, top), P(b + HOOK_T, top), P(b + HOOK_T, NB), P(b, NB), P(b, 1.1),
            P(b - 0.35, 1.5), P(b, 1.9), P(b, LIP_H + G), P(a, LIP_H + G), P(a, 1.9), P(a + 0.35, 1.5), P(a, 1.1), P(a, NB)]


def ring_section():
    angs = [A0 + (A1 - A0) * k / 60.0 for k in range(61)]
    pts = [(YR + RO * math.cos(math.radians(a)), ZR + RO * math.sin(math.radians(a))) for a in angs]
    pts += [(YR + (RI - 0.3) * math.cos(math.radians(a)), ZR + (RI - 0.3) * math.sin(math.radians(a))) for a in reversed(angs)]
    return pts


def run(context):
    app = adsk.core.Application.get()
    for d in list(app.documents):
        if d.name.startswith("ACC backlight v1"):
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
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    ash = des.appearances.itemByName("ABS - ash blue-grey")
    ref_ap = des.appearances.itemByName("Reference - clear")
    white = des.appearances.itemByName("ABS - natural white (diffuser)")
    if not white:
        base = lib.appearances.itemByName("Plastic - Matte (White)") or lib.appearances.itemByName("Plastic - Glossy (White)")
        white = des.appearances.addByCopy(base, "ABS - natural white (diffuser)") if base else ref_ap
    led_ap = des.appearances.itemByName("LED strip - ref")
    if not led_ap:
        base = lib.appearances.itemByName("Plastic - Matte (Yellow)") or lib.appearances.itemByName("Plastic - Matte (Gray)")
        led_ap = des.appearances.addByCopy(base, "LED strip - ref") if base else ref_ap
    pcb_ap = des.appearances.itemByName("PCB - ref")
    if not pcb_ap:
        base = lib.appearances.itemByName("Plastic - Matte (Black)") or lib.appearances.itemByName("Plastic - Matte (Gray)")
        pcb_ap = des.appearances.addByCopy(base, "PCB - ref") if base else ref_ap

    def p(x, y, z):
        return adsk.core.Point3D.create(x / 10, y / 10, z / 10)

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

    def poly(comp, pl, coords, name):
        sk = comp.sketches.add(pl)
        sk.name = name
        sk.isComputeDeferred = True
        pts = [sk.modelToSketchSpace(p(*q)) for q in coords]
        for i, q in enumerate(pts):
            sk.sketchCurves.sketchLines.addByTwoPoints(q, pts[(i + 1) % len(pts)])
        sk.isComputeDeferred = False
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
        pl = plane(comp, kind, at * sgn)

        def to3(u, v):
            if kind == "xz":
                return (u, at, v)
            if kind == "yz":
                return (at, u, v)
            return (u, v, at)
        sk = poly(comp, pl, [to3(u, v) for u, v in pts2], name)
        return ext(comp, sk, a1 - a0, op, name)

    def box(comp, x0, x1, y0, y1, z0, z1, op=NEW, name="Box"):
        return prism(comp, "xy", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, op, name)

    def circle_pts(cu, cv, r, n=72):
        return [(cu + r * math.cos(2 * math.pi * k / n), cv + r * math.sin(2 * math.pi * k / n)) for k in range(n)]

    def finish(c, ap):
        for b in c.bRepBodies:
            if ap:
                b.appearance = ap
        for sk in c.sketches:
            sk.isVisible = False
        c.isConstructionFolderLightBulbOn = False

    def bore_cut(comp, xa, xb, name):
        """True cylindrical bore (sketch circle, not a polygon) so the D19.8 snap is exact."""
        sk = comp.sketches.add(plane(comp, "yz", xa - 1))
        sk.name = name
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(xa - 1, YR, ZR)), RI / 10)
        return ext(comp, sk, xb - xa + 2, CUT, name)

    printed = []

    # ---------------- rail segments ----------------
    for key, (xa, xb) in SEGS.items():
        occ, c = component("acc_backlight_rail_" + key)
        prism(c, "yz", rail_section(), xa, xb, NEW, "Rail section: 45 deg LED face, lips with snap grooves")
        for nx, w in NOTCHES:
            if xa < nx < xb:
                aw = w + 4.0
                box(c, nx - aw / 2, nx + aw / 2, 100, 126, Z0 - 1, ARCH_TOP, CUT, "Cable arch over tile notch %g" % w)
        if key in ("S1", "S3"):
            sg = 1 if key == "S3" else -1
            root_x, tip_x = sg * 106.6, sg * 98.1
            prism(c, "xy", [(root_x, 112.0), (tip_x, 111.0), (tip_x, 117.0), (root_x, 116.0)], Z0, Z0 + 3.0, JOIN,
                  "Dovetail tab into S2")
            if key == "S3":
                box(c, BR_R[0] - 0.2, X_R + 1, SLOT_Y[0], SLOT_Y[1], SLOT_Z[0], SLOT_Z[1], CUT, "Slot for bracket tongue")
                box(c, WIRE_X[0], WIRE_X[1], 112.5, 126, Z0 - 1, 150, CUT, "Wire drop, open to the back")
            else:
                box(c, X_L - 1, BR_L[1] + 0.2, SLOT_Y[0], SLOT_Y[1], SLOT_Z[0], SLOT_Z[1], CUT, "Slot for bracket tongue")
        else:
            for sg in (1, -1):
                prism(c, "xy", [(sg * 106.5, 111.9), (sg * 97.95, 110.85), (sg * 97.95, 117.15), (sg * 106.5, 116.1)],
                      Z0 - 0.7, Z0 + 3.2, CUT, "Dovetail pocket, open from below")
        body = c.bRepBodies.item(0)
        assert c.bRepBodies.count == 1 and body.isSolid, key
        body.name = "acc_backlight_rail_" + key
        finish(c, ash)
        printed.append((c.name, body))

    # ---------------- end brackets ----------------
    for key, (xa, xb) in (("R", BR_R), ("L", BR_L)):
        occ, c = component("acc_backlight_bracket_" + key)
        prism(c, "yz", ring_section(), xa, xb, NEW, "Snap ring D19.8 on the back rod, opens downwards")
        box(c, xa, xb, 98.0, Y0 + LIP_T * sA - 0.05, 112.5, TONGUE_Z[0], JOIN, "Top plate under the rail end")
        box(c, xa, xb, TONGUE_Y[0], TONGUE_Y[1], TONGUE_Z[0] - 0.5, TONGUE_Z[1], JOIN, "Tongue into the rail slot")
        bore_cut(c, xa, xb, "Bore D19.8")
        if key == "R":
            box(c, WIRE_X[0], WIRE_X[1], 112.5, 126, 108, 125, CUT, "Wire notch, open to the back")
        body = c.bRepBodies.item(0)
        assert c.bRepBodies.count == 1 and body.isSolid, key
        body.name = "acc_backlight_bracket_" + key
        finish(c, ash)
        printed.append((c.name, body))

    # ---------------- diffusers (optional, white) ----------------
    for key, (xa, xb) in SEGS.items():
        occ, c = component("acc_backlight_diffuser_" + key)
        prism(c, "yz", diffuser_section(), xa, xb, NEW, "Diffuser 0.9 mm, clips on the lips")
        body = c.bRepBodies.item(0)
        body.name = "acc_backlight_diffuser_" + key
        finish(c, white)
        printed.append((c.name, body))

    # ---------------- controller box ----------------
    occ, c = component("acc_backlight_box")
    box(c, BX0, BX1, BY0, BY1, BZ0, BZ1, NEW, "Box shell")
    box(c, CX0, CX1, BY0 - 0.5, CY1, CZ0, CZ1, CUT, "Cavity, open at the front (lid)")
    box(c, BRING[0], BRING[1], BY0, 113.6, BZ1 - 0.6, 104.0, JOIN, "Web ring -> box")
    prism(c, "yz", ring_section(), BRING[0], BRING[1], JOIN, "Snap ring D19.8 on the back rod")
    bore_cut(c, BRING[0], BRING[1], "Bore D19.8")
    box(c, 289.25, 302.75, 113.05, 120.55, BZ0 - 0.5, CZ0 + 0.5, CUT, "USB-C plug opening 13.5 x 7.5")
    box(c, 308.5, 316.5, 113.0, 119.0, CZ1 - 0.5, BZ1 + 0.5, CUT, "Wire entry from the strip (3 wires)")
    box(c, 298.0, 305.0, 113.9, 116.0, CZ1 - 0.5, BZ1 + 0.5, CUT, "Window for the lid snap (top)")
    box(c, 310.0, 318.0, 113.9, 116.0, BZ0 - 0.5, CZ0 + 0.5, CUT, "Window for the lid snap (bottom)")
    box(c, CX0 - 0.1, 286.85, 116.0, CY1 + 0.1, CZ0 - 0.1, 66.0, JOIN, "Board stop left")
    box(c, 305.15, 306.6, 116.0, CY1 + 0.1, CZ0 - 0.1, 66.0, JOIN, "Board stop right")
    bbody = c.bRepBodies.item(0)
    assert c.bRepBodies.count == 1 and bbody.isSolid, ("box", c.bRepBodies.count)
    bbody.name = "acc_backlight_box"
    finish(c, ash)
    printed.append((c.name, bbody))

    occ, c = component("acc_backlight_box_lid")
    box(c, CX0 + 0.15, CX1 - 0.15, BY0, BY0 + 1.2, CZ0 + 0.15, CZ1 - 0.15, NEW, "Lid plate")
    box(c, 298.5, 304.5, BY0 + 1.0, 116.0, CZ1 - 1.25, CZ1 - 0.25, JOIN, "Snap tab top")
    prism(c, "yz", [(114.2, CZ1 - 0.3), (114.2, CZ1 + 0.55), (114.6, CZ1 + 0.55), (115.8, CZ1 - 0.3)], 298.5, 304.5, JOIN, "Bump top")
    box(c, 310.5, 317.5, BY0 + 1.0, 116.0, CZ0 + 0.25, CZ0 + 1.25, JOIN, "Snap tab bottom")
    prism(c, "yz", [(114.2, CZ0 + 0.3), (115.8, CZ0 + 0.3), (114.6, CZ0 - 0.55), (114.2, CZ0 - 0.55)], 310.5, 317.5, JOIN, "Bump bottom")
    for k in range(6):
        xc = 289.0 + 6.0 * k
        box(c, xc - 0.9, xc + 0.9, BY0 - 0.5, BY0 + 1.7, 70.0, 88.0, CUT, "Vent slot")
    lbody = c.bRepBodies.item(0)
    assert c.bRepBodies.count == 1 and lbody.isSolid, ("lid", c.bRepBodies.count)
    lbody.name = "acc_backlight_box_lid"
    finish(c, ash)
    printed.append((c.name, lbody))

    # ---------------- references (not printed) ----------------
    def ref(name, build, ap):
        o, rc = component("REF - backlight " + name)
        build(rc)
        finish(rc, ap)
        return o
    s0, s1 = 0.3, 0.3 + LED_W
    strip = [P(s0, 0.03), P(s1, 0.03), P(s1, LED_T), P(s0, LED_T)]
    ref("LED strip WS2812B %gx%g" % (LED_W, LED_T), lambda rc: prism(rc, "yz", strip, X_L, 316.0, NEW, "strip"), led_ap)

    def board(rc):
        box(rc, 287.0, 305.0, 118.4, 119.4, CZ0 + 0.02, CZ0 + 22.52, NEW, "PCB 22.5 x 18")
        box(rc, 291.53, 300.47, 115.2, 118.5, 61.2, 68.5, JOIN, "USB-C receptacle")
        box(rc, 292.0, 297.0, 117.5, 118.5, 72.0, 77.0, JOIN, "ESP32-C3 QFN")
    ref("ESP32-C3 Super Mini", board, pcb_ap)

    def cap(rc):
        prism(rc, "xy", circle_pts(316.5, 116.1, 4.0, 48), 64.5, 77.5, NEW, "1000uF D8x13")
    ref("capacitor 1000uF D8", cap, ref_ap)

    # ---------------- STL + dims ----------------
    parts = {}
    for name, b in printed:
        stl = OUT + "/" + name + ".stl"
        opt = des.exportManager.createSTLExportOptions(b, stl)
        opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        des.exportManager.execute(opt)
        bb = b.boundingBox
        parts[name] = {"bbox_mm": [round(getattr(bb.minPoint, a) * 10, 2) for a in "xyz"] + [round(getattr(bb.maxPoint, a) * 10, 2) for a in "xyz"],
                       "volume_cm3": round(b.volume, 3)}

    # ---------------- checks ----------------
    for o in root.occurrences:
        if o.component.name == "REF - wall behind the shelf":
            o.isLightBulbOn = True
    tm = adsk.fusion.TemporaryBRepManager.get()
    items = []
    for o in root.allOccurrences:
        if not o.isVisible:
            continue
        for b in o.bRepBodies:
            items.append((o.component.name, tm.copy(b)))

    def overlap(a, b):
        A, B = a.boundingBox, b.boundingBox
        return not any(getattr(A.maxPoint, k) <= getattr(B.minPoint, k) + 1e-6 or
                       getattr(B.maxPoint, k) <= getattr(A.minPoint, k) + 1e-6 for k in "xyz")

    def inter(a, b):
        if not overlap(a, b):
            return 0.0
        rr = tm.copy(a)
        tm.booleanOperation(rr, b, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return rr.volume * 1000 if rr.lumps.count else 0.0

    NEWN = ("acc_backlight", "REF - backlight")
    new = [(n, b) for n, b in items if n.startswith(NEWN)]
    rest = [(n, b) for n, b in items if not n.startswith(NEWN)]
    hits, press = [], []
    for n, b in new:
        for m, mb in rest:
            v = inter(b, mb)
            if v > 1e-3:
                (press if m.startswith("WOOD") else hits).append([n, m, round(v, 3)])
    own = [[new[i][0], new[j][0], round(inter(new[i][1], new[j][1]), 3)]
           for i in range(len(new)) for j in range(i + 1, len(new)) if inter(new[i][1], new[j][1]) > 1e-3]
    # same check with a D19.8 rod: the only overlap above must be the designed 0.1 mm snap preload
    rod_small = []
    cyl = tm.createCylinderOrCone(p(-560, YR, ZR), RI / 10, p(560, YR, ZR), RI / 10)
    for n, b in new:
        v = inter(b, cyl)
        if v > 1e-3:
            rod_small.append([n, round(v, 3)])
    drawer_hits = []
    for dn in ("drawer_left", "drawer_right"):
        dr = next(b for n, b in items if n == dn)
        for travel in range(0, 150, 5):
            t = tm.copy(dr)
            m = adsk.core.Matrix3D.create()
            m.translation = adsk.core.Vector3D.create(0, -travel / 10, 0)
            tm.transform(t, m)
            for n, b in new:
                v = inter(t, b)
                if v > 1e-3:
                    drawer_hits.append([dn, n, travel, round(v, 3)])
    max_y = max(b.boundingBox.maxPoint.y * 10 for n, b in new)
    report = {
        "parts": parts,
        "interferences_new_vs_shelf_modules_wall": hits,
        "contact_with_wooden_rod_CAD_D20_(designed_snap_preload_0.1mm)": press,
        "overlap_with_D19.8_rod_(should_be_empty)": rod_small,
        "interferences_between_new_parts": own,
        "drawer_travel_0_145mm": drawer_hits,
        "max_y_of_new_parts_mm": round(max_y, 3),
        "rail": {"x": [X_L, X_R], "strip_length_mm": 316.0 - X_L, "front_y": round(rail_section()[0][0], 2),
                 "top_z_rail": round(max(q[1] for q in rail_section()), 2),
                 "top_z_diffuser": round(max(q[1] for q in diffuser_section()), 2),
                 "led_face_low_point": [round(Y0, 2), round(Z0F, 2)], "angle_deg": ANG,
                 "LED_W": LED_W, "LED_T": LED_T, "arch_h": ARCH_H},
        "snap_bore_mm": 2 * RI, "snap_opening_chord_mm": round(2 * RI * math.sin(math.radians((A1 - A0) / 2)), 2),
    }
    with open(OUT + "/backlight_v1_check.json", "w") as f:
        json.dump(report, f, indent=2)
    des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT + "/deskshelf_backlight_v1.f3d"))

    # ---------------- renders ----------------
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
    shot("_warmup.png", (500, 1150, 520), (0, 100, 110), 70.0)
    shot("view_wall_side_overview.png", (500, 1150, 520), (0, 100, 110), 70.0)
    shot("view_wall_side_right_end.png", (470, 330, 230), (295, 108, 100), 16.0)
    keep = ("acc_backlight", "REF - backlight", "WOOD", "deck_tile")
    hidden = []
    for o in root.occurrences:
        if o.isLightBulbOn and not o.component.name.startswith(keep):
            o.isLightBulbOn = False
            hidden.append(o)
    shot("view_isolated_wall_side.png", (420, 700, 330), (60, 110, 115), 45.0)
    for o in root.occurrences:
        if o.component.name in ("acc_backlight_diffuser_S3", "acc_backlight_box_lid") or o.component.name.startswith("deck_tile"):
            if o.isLightBulbOn:
                o.isLightBulbOn = False
                hidden.append(o)
    shot("view_isolated_right_end_open.png", (420, 330, 175), (300, 110, 100), 13.0)
    shot("view_isolated_section_from_right.png", (700, 110, 112), (300, 110, 112), 9.0)
    shot("view_isolated_box_front.png", (330, -60, 60), (303, 112, 85), 11.0)
    for o in hidden:
        o.isLightBulbOn = True
    try:
        os.remove(OUT + "/_warmup.png")
    except OSError:
        pass
    print(json.dumps(report, indent=1))
