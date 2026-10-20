"""DeskShelf front-rod accessories v1 (2026-10-19): cable (plug) holders + USB-hub hanger.

Global mm: x along the rods, y front(-) -> back(+), z up from the desk. Front rod (1) y=-100, rod 2 y=-50, axis z=105.
Deck tiles x -270..270 lie ON the rods (skin z 115.1..118.1, front edge y=-122): nothing may wrap over the rod
crown there, so every clip here is an OPEN-TOP C-ring that snaps on FROM BELOW (tips ~31..43 deg above the
equator, all material <= z 114.8). Tile saddles (x = +-75..81, +-99..105, +-255..261) are avoided in x.

1. acc_cable_clip_N (N = 1, 2, 3 cables): snap ring D19.8 on the front rod (as the tested v2.4 rod_clip, wrap ~242 deg)
   + a 5 mm ledge in front of the tile edge (top z 101) with N teardrop holes D4.8 and 3.0 mm throats at 45 deg
   (cable 3..4.5 mm presses in from the front, the plug boot rests on the ledge). Anti-rotation: a fin behind the rod
   stops 0.3 mm under the tile skin, so the plug weight (front-down torque) is taken by the tile after ~1.5 deg.
   Print: lying on its x-min side (teardrops and throats point up), no supports.
2. acc_hub_cap_left / acc_hub_cap_right: two mirrored end caps that hold the hub by its ends (pocket 10 mm,
   end wall with an open cable slot to the back, 4 mm front lips at the hub ends -> ports stay free).
   Each cap snaps on rod 1 (D19.8) AND rod 2 (thin 19.0 rod: stadium bore 19.4 with +-1 mm play in y), so it cannot
   rotate when plugs are pushed in or pulled out. Hub under the front rod, ports flush with y=-124.6 (facing the user).
   Print: end wall on the bed, no supports.
"""
import adsk.core
import adsk.fusion
import math
import os
import json

# ---------------- user parameters ----------------
HUB_L, HUB_W, HUB_H = 95.0, 30.0, 11.0      # USB hub: length (x), depth (y, ports on the front face), height (z)
HUB_XC = -266.0                             # hub centre x (left of the keyboard, next to the left inner leg)
CABLE_DY, CABLE_DZ = 0.0, 0.0               # hub cable offset from the centre of the hub end face
CABLE_SLOT = 5.5                            # slot in the cap end wall for the hub cable
CLIPS = (("acc_cable_clip_3", 3, -203.0), ("acc_cable_clip_2", 2, 120.0), ("acc_cable_clip_1", 1, 200.0))  # name, n, x0

SRC = "/Users/YOU/fusion-mcp/exports/deskshelf-v2.3-modules-v2/deskshelf_v2_3_modules_v2_colorsD.f3d"
OUT = "/Users/YOU/fusion-mcp/exports/acc-front-rod"
DOC = "ACC front-rod v1 - REVIEW"
Y1, Y2, ZR = -100.0, -50.0, 105.0
RI1, RO1, CH1 = 9.9, 12.4, 17.0             # rod 1 snap: bore D19.8, wall 2.5, opening chord 17.0
RI2, RO2, E2, CH2 = 9.7, 12.2, 1.0, 16.2    # rod 2 (D19.0): stadium bore D19.4, +-1.0 mm in y, chord 16.2
TILE_Z0 = 115.1
# cable clip
ARM_Z0, ARM_Z1 = 96.0, 101.0
LEDGE_Y = -146.0
HOLE_Y, HOLE_R, THROAT = -139.0, 2.4, 3.0
PITCH = 14.0
RING_W = 16.0                               # snap ring width (x) of every cable clip
FIN_Y0, FIN_Y1, FIN_Z0, FIN_Z1 = -89.5, -85.5, 106.0, 114.8
# hub caps
CLR = 0.3
END_T, POCKET, LIP_X, LIP_T, WALL = 2.0, 10.0, 4.0, 1.6, 2.5
Y_CF = -124.6                               # cavity front (back face of the front lips)
Y_CB = Y_CF + HUB_W + 2*CLR
ZC_T = 90.4                                 # cavity top; top bar to z 93.0 (rod 1 bottom z 95)
ZC_B = ZC_T - HUB_H - 2*CLR
HX0, HX1 = HUB_XC - HUB_L/2, HUB_XC + HUB_L/2
SADDLES = [(-261, -255), (-105, -99), (-81, -75), (75, 81), (99, 105), (255, 261)]


def log(msg):
    os.makedirs(OUT, exist_ok=True)
    with open(OUT + "/_progress.txt", "a") as f:
        f.write(str(msg) + "\n")


def run(context):
    import traceback
    try:
        _run(context)
        log("DONE")
    except Exception:
        log("ERROR " + traceback.format_exc())


def _run(context):
    app = adsk.core.Application.get()
    for d in list(app.documents):
        if d.name.startswith("ACC front-rod v1"):
            d.close(False)
    assert ZC_B - WALL >= 60.0, "hub too tall: panel would be lower than 60 mm above the desk"
    im = app.importManager
    doc = im.importToNewDocument(im.createFusionArchiveImportOptions(SRC))
    doc.name = DOC
    os.makedirs(OUT, exist_ok=True)
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    blue = des.appearances.itemByName("ABS - blue")
    ref_ap = des.appearances.itemByName("Reference - clear")

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
            inp.participantBodies = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
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

    def stadium(yc, zc, r, e, n=48):
        """Closed stadium (bore), elongated by +-e along y."""
        pts = []
        for k in range(n+1):          # back arc  -90..90
            a = math.radians(-90+180*k/n)
            pts.append((yc+e+r*math.cos(a), zc+r*math.sin(a)))
        for k in range(n+1):          # front arc 90..270
            a = math.radians(90+180*k/n)
            pts.append((yc-e+r*math.cos(a), zc+r*math.sin(a)))
        if e < 1e-6:
            pts = pts[:n] + pts[n+1:2*n+1]
        return pts

    def snap_ring(yc, zc, ri, ro, e, chord, n=40):
        """Open-top C-ring in the yz plane: opening chord measured at the inner surface; radial tip faces."""
        beta = math.asin((chord/2-e)/ri)           # half opening angle from vertical (inner tip)

        def side(r):
            front = [math.radians(90+math.degrees(beta)+(180-math.degrees(beta))*k/n) for k in range(n+1)]   # front tip -> bottom
            back = [math.radians(270+(180-math.degrees(beta))*k/n) for k in range(n+1)]                     # bottom -> back tip
            pts = [(yc-e+r*math.cos(a), zc+r*math.sin(a)) for a in front]
            pts += [(yc+e+r*math.cos(a), zc+r*math.sin(a)) for a in (back if e > 1e-6 else back[1:])]
            return pts
        outer, inner = side(ro), side(ri)
        return outer + list(reversed(inner)), math.degrees(beta)

    def finish(comp, body, name, ap):
        body.name = name
        if ap:
            body.appearance = ap
        for sk in comp.sketches:
            sk.isVisible = False
        comp.isConstructionFolderLightBulbOn = False

    ring1, beta1 = snap_ring(Y1, ZR, RI1, RO1, 0.0, CH1)
    ring2, beta2 = snap_ring(Y2, ZR, RI2, RO2, E2, CH2)

    def free_of_saddles(x0, x1, what):
        for a, b in SADDLES:
            assert x1 <= a - 0.5 or x0 >= b + 0.5, (what, "hits tile saddle", a, b)

    log('# ---------------- cable clips')
    # ---------------- cable clips ----------------
    clip_info = {}
    clip_bodies = []
    for name, n, x0 in CLIPS:
        w = PITCH*n + 1.0
        x1 = x0 + w
        free_of_saddles(x0, x1, name)
        occ, c = component(name)
        rw = min(w, RING_W)          # ring only at the x-min end (= bed side): same snap force for 1/2/3 cables
        prism(c, "yz", ring1, x0, x0+rw, NEW, "Snap ring D19.8, open top (snaps on from below)")
        box(c, x0, x1, LEDGE_Y, -108.0, ARM_Z0, ARM_Z1, JOIN, "Arm + plug ledge (top z 101)")
        box(c, x0, x0+rw, FIN_Y0, FIN_Y1, FIN_Z0, FIN_Z1, JOIN, "Anti-rotation fin, 0.3 under the tile skin")
        prism(c, "yz", circle_pts(Y1, ZR, RI1), x0-1, x1+1, CUT, "Bore D19.8")
        box(c, x0-1, x1+1, Y1-CH1/2, Y1+CH1/2, ZR, ZR+15, CUT, "Keep the snap opening clear")
        holes = []
        for i in range(n):
            xc = x0 + 4.0 + PITCH*i
            tear = [(xc+HOLE_R*math.cos(math.radians(a)), HOLE_Y+HOLE_R*math.sin(math.radians(a)))
                    for a in [45+270*k/48 for k in range(49)]] + [(xc+HOLE_R*math.sqrt(2), HOLE_Y)]
            prism(c, "xy", tear, ARM_Z0-0.5, ARM_Z1+0.5, CUT, "Cable hole D%.1f (teardrop, prints up)" % (2*HOLE_R))
            h = THROAT/2/math.sqrt(2)
            thr = [(xc+h, HOLE_Y+h), (xc+12+h, HOLE_Y-12+h), (xc+12-h, HOLE_Y-12-h), (xc-h, HOLE_Y-h)]
            prism(c, "xy", thr, ARM_Z0-0.5, ARM_Z1+0.5, CUT, "Throat %.1f at 45 deg to the front edge" % THROAT)
            holes.append(xc)
        body = c.bRepBodies.item(0)
        assert c.bRepBodies.count == 1 and body.isSolid, name
        finish(c, body, name, blue)
        clip_bodies.append((name, body))
        clip_info[name] = {"cables": n, "x": [x0, x1], "ring_x": [x0, x0+rw], "hole_x": holes}

    log('# ---------------- hub caps')
    # ---------------- hub caps ----------------
    yc_cab = Y_CF + CLR + HUB_W/2 + CABLE_DY
    zc_cab = (ZC_T + ZC_B)/2 + CABLE_DZ
    cap_bodies = []
    cap_info = {}
    for name, s in (("acc_hub_cap_left", 1), ("acc_hub_cap_right", -1)):
        if s > 0:
            xa = HX0 - CLR - END_T
            xb = xa + END_T + POCKET
            ew = (xa, xa + END_T)
            pk = (xa + END_T, xb)
            lip_from = (pk[0] + LIP_X, xb + 0.5)
        else:
            xb = HX1 + CLR + END_T
            xa = xb - END_T - POCKET
            ew = (xb - END_T, xb)
            pk = (xa, xb - END_T)
            lip_from = (xa - 0.5, pk[1] - LIP_X)
        free_of_saddles(xa, xb, name)
        occ, c = component(name)
        box(c, xa, xb, Y_CF-LIP_T, Y_CB+WALL, ZC_B-WALL, ZC_T+2.6, NEW, "Hub frame block")
        prism(c, "yz", ring1, xa, xb, JOIN, "Snap ring rod 1 D19.8")
        box(c, xa, xb, -106.0, -94.0, ZC_T, 95.0, JOIN, "Ring 1 root block")
        box(c, xa, xb, Y_CB, -42.0, 89.0, 93.6, JOIN, "Web: frame to rod 2")
        box(c, xa, xb, -56.0, -44.0, 89.0, 95.3, JOIN, "Ring 2 root block")
        prism(c, "yz", ring2, xa, xb, JOIN, "Snap ring rod 2 (D19.0 rod): stadium D19.4 +-1")
        a, b = (pk[0], pk[1]+0.5) if s > 0 else (pk[0]-0.5, pk[1])
        box(c, a, b, Y_CF, Y_CB, ZC_B, ZC_T, CUT, "Hub pocket %gx%g +%.1f" % (HUB_W, HUB_H, 2*CLR))
        box(c, lip_from[0], lip_from[1], Y_CF-LIP_T-0.5, Y_CF+0.01, ZC_B, ZC_T, CUT, "Front open beyond the 4 mm end lips (ports free)")
        e0, e1 = (ew[0]-0.5, ew[1]) if s > 0 else (ew[0], ew[1]+0.5)
        box(c, e0, e1, yc_cab-CABLE_SLOT/2, Y_CB+WALL+0.5, zc_cab-CABLE_SLOT/2, zc_cab+CABLE_SLOT/2, CUT,
            "Cable slot in the end wall, open to the back")
        prism(c, "yz", circle_pts(Y1, ZR, RI1), xa-1, xb+1, CUT, "Bore rod 1 D19.8")
        prism(c, "yz", stadium(Y2, ZR, RI2, E2), xa-1, xb+1, CUT, "Bore rod 2 stadium")
        box(c, xa-1, xb+1, Y1-CH1/2, Y1+CH1/2, ZR, ZR+15, CUT, "Keep opening 1 clear")
        box(c, xa-1, xb+1, Y2-CH2/2, Y2+CH2/2, ZR, ZR+15, CUT, "Keep opening 2 clear")
        body = c.bRepBodies.item(0)
        assert c.bRepBodies.count == 1 and body.isSolid, name
        finish(c, body, name, blue)
        cap_bodies.append((name, body))
        cap_info[name] = {"x": [round(xa, 2), round(xb, 2)], "end_wall_x": [round(v, 2) for v in ew]}

    log('# ---------------- references')
    # ---------------- references ----------------
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

    hz0 = ZC_B + CLR
    hy0 = Y_CF + CLR

    def hub(rc):
        box(rc, HX0, HX1, hy0, hy0+HUB_W, hz0, hz0+HUB_H, NEW, "hub")
        for k in range(4):
            px = HUB_XC + (k-1.5)*20.0
            box(rc, px-6.25, px+6.25, hy0-0.5, hy0+9, hz0+HUB_H/2-2.5, hz0+HUB_H/2+2.5, CUT, "USB-A port")
        prism(rc, "yz", circle_pts(yc_cab, zc_cab, 2.0, 24), HX0-8.0, HX0+0.5, JOIN, "cable out of the end")
        box(rc, HX0-8.0, HX0-4.0, yc_cab-2, 30.0, zc_cab-2, zc_cab+2, JOIN, "cable to the back")
    ref("USB hub %gx%gx%g" % (HUB_L, HUB_W, HUB_H), hub)

    def plugs(rc):
        for nm, info in clip_info.items():
            for xc in info["hole_x"]:
                box(rc, xc-6, xc+6, HOLE_Y-3.25, HOLE_Y+3.25, ARM_Z1+0.05, ARM_Z1+22, NEW, "plug boot 12x6.5")
                box(rc, xc-4.2, xc+4.2, HOLE_Y-1.3, HOLE_Y+1.3, ARM_Z1+22, ARM_Z1+28.5, JOIN, "USB-C tip")
                prism(rc, "xy", circle_pts(xc, HOLE_Y, 2.0, 24), 70.0, ARM_Z1+0.1, JOIN, "cable D4")
    ref("Plugs USB-C on the clips", plugs)
    ref("Keyboard 440x140x38 (pushed under)", lambda rc: box(rc, -220, 220, -160, -20, 0, 38, NEW, "keyboard"))

    log('# ---------------- STL')
    # ---------------- STL ----------------
    parts = {}
    for nm, b in clip_bodies + cap_bodies:
        opt = des.exportManager.createSTLExportOptions(b, OUT + "/" + nm + ".stl")
        opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        des.exportManager.execute(opt)
        bb = b.boundingBox
        parts[nm] = {"bbox_mm": [round(getattr(bb.minPoint, a)*10, 2) for a in "xyz"] + [round(getattr(bb.maxPoint, a)*10, 2) for a in "xyz"],
                     "volume_cm3": round(b.volume, 3)}

    log('# ---------------- checks')
    # ---------------- checks ----------------
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

    new = [(n, b) for n, b in items if n.startswith("acc_")]
    refs = [(n, b) for n, b in items if n.startswith("REF - ") and n.split(" - ")[1].startswith(("USB hub", "Plugs", "Keyboard"))]
    ref_names = set(n for n, _ in refs)
    shelf = [(n, b) for n, b in items if not n.startswith("acc_") and n not in ref_names]
    wood = [(n, b) for n, b in shelf if n.startswith("WOOD")]
    rest = [(n, b) for n, b in shelf if not n.startswith("WOOD")]
    hits = [[n, m, round(inter(b, mb), 3)] for n, b in new for m, mb in rest if inter(b, mb) > 1e-3]
    # real rods: 1/3/5 good D20.0 (snap bore 19.8 = intended grip), 2/4 thin D19.0
    real_rods = []
    for y, d in ((-100, 19.79), (-50, 18.99), (0, 20.0), (50, 18.99), (100, 20.0)):
        real_rods.append(("real rod y=%d D%.2f" % (y, d), tm.createCylinderOrCone(p(-550, y, ZR), d/20, p(550, y, ZR), d/20)))
    rod_hits = [[n, m, round(inter(b, mb), 3)] for n, b in new for m, mb in real_rods if inter(b, mb) > 1e-3]
    cad_rod_grip = [[n, m, round(inter(b, mb), 2)] for n, b in new for m, mb in wood if inter(b, mb) > 1e-3]
    ref_hits = [[n, m, round(inter(b, mb), 3)] for n, b in refs for m, mb in rest + wood + new if inter(b, mb) > 1e-3]
    own = [[new[i][0], new[j][0], round(inter(new[i][1], new[j][1]), 3)]
           for i in range(len(new)) for j in range(i+1, len(new)) if inter(new[i][1], new[j][1]) > 1e-3]
    drawer_hits = []
    for dn in ("drawer_left", "drawer_right"):
        dr = next(b for n, b in items if n == dn)
        for travel in range(0, 150, 5):
            t = tm.copy(dr)
            m = adsk.core.Matrix3D.create()
            m.translation = adsk.core.Vector3D.create(0, -travel/10, 0)
            tm.transform(t, m)
            for n, b in new + refs:
                v = inter(t, b)
                if v > 1e-3:
                    drawer_hits.append([dn, n, travel, round(v, 3)])
    # anti-rotation of the cable clips: rotate front-down about the rod axis until the fin meets a deck tile
    tiles = [(n, b) for n, b in rest if n.startswith("deck_tile")]
    tilt = {}
    for nm, b in clip_bodies:
        first = None
        for k in range(1, 21):
            deg = 0.25*k
            m = adsk.core.Matrix3D.create()
            m.setToRotation(math.radians(deg), adsk.core.Vector3D.create(1, 0, 0), p(0, Y1, ZR))
            t = tm.copy(b)
            tm.transform(t, m)
            if any(inter(t, tb) > 1e-4 for _, tb in tiles):
                first = deg
                break
        tilt[nm] = first
    zmin = min(b.boundingBox.minPoint.z*10 for _, b in new)
    zmax = max(b.boundingBox.maxPoint.z*10 for _, b in new)
    ymax = max(b.boundingBox.maxPoint.y*10 for _, b in new + refs)
    report = {"parts": parts, "clips": clip_info, "hub_caps": cap_info,
              "hub": {"L_W_H": [HUB_L, HUB_W, HUB_H], "x": [HX0, HX1], "front_face_y": round(hy0, 2),
                      "z": [round(hz0, 2), round(hz0+HUB_H, 2)], "cable_slot": CABLE_SLOT},
              "interferences_new_vs_shelf_non_wood": hits,
              "interferences_new_vs_real_size_rods": rod_hits,
              "intended_snap_grip_vs_CAD_D20_rods_mm3": cad_rod_grip,
              "interferences_refs(hub, plugs, keyboard)_vs_all": ref_hits,
              "interferences_between_new_parts": own,
              "drawer_travel_0_145_hits": drawer_hits,
              "clip_front_down_rotation_until_fin_meets_tile_deg": tilt,
              "lowest_part_z_mm": round(zmin, 2), "highest_part_z_mm": round(zmax, 2), "tile_skin_z": TILE_Z0,
              "max_y_mm": round(ymax, 2),
              "snap": {"rod1_bore": 2*RI1, "rod1_opening_chord": CH1, "rod1_tip_above_equator_deg": round(90-beta1, 1),
                       "rod2_bore_stadium": [2*RI2, "+-%.1f y" % E2], "rod2_opening_chord": CH2,
                       "rod2_tip_above_equator_deg": round(90-beta2, 1)}}
    log('with open(OUT + "/front_rod_check.json"')
    with open(OUT + "/front_rod_check.json", "w") as f:
        json.dump(report, f, indent=2)
    des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT + "/deskshelf_v2_3_front_rod_acc_v1.f3d"))

    log('# ---------------- renders')
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
    shot("_warmup.png", (-500, -1100, 450), (-60, -100, 100), 70.0)
    shot("view_on_shelf_front.png", (-420, -1150, 420), (-60, -100, 100), 70.0)
    shot("view_on_shelf_hub_and_clip3.png", (-120, -520, 170), (-240, -110, 95), 30.0)
    shot("view_on_shelf_hub_below.png", (-150, -480, 10), (-260, -100, 90), 28.0)
    shot("view_on_shelf_clips_right.png", (330, -480, 230), (165, -115, 105), 26.0)
    keep = ("acc_", "REF - USB hub", "REF - Plugs")
    hidden = []
    for o in root.occurrences:
        if o.isLightBulbOn and not o.component.name.startswith(keep):
            o.isLightBulbOn = False
            hidden.append(o)
    shot("view_isolated_hub_caps.png", (-120, -330, 190), (-266, -85, 95), 30.0)
    shot("view_isolated_hub_caps_back.png", (-420, 150, 200), (-266, -80, 95), 30.0)
    shot("view_isolated_clip3_side.png", (-90, -260, 170), (-182, -110, 103), 16.0)
    for o in hidden:
        o.isLightBulbOn = True
    try:
        os.remove(OUT + "/_warmup.png")
    except OSError:
        pass
    print(json.dumps(report, indent=1))
