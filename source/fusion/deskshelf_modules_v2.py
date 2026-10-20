"""DeskShelf v2.2 add-on modules v2: everything sits on the rods, no tools.
The shelf stands against a wall (nothing may protrude behind y = 122).

- laptop_dock: one slot 19 mm for the MacBook Air M1 (16.1 mm max), against the
  right end leg. The 304 mm laptop is pushed back to the wall and sticks out
  ~62 mm at the front.
- bookend: lower L-bookend for small textbooks; books stand on the rods between
  the bookend and the dock.
- macmini_stand: Mac mini M4 on its side above the left bay. Ports face the
  wall with ~55 mm for plugs, front ports face the user, the underside (air
  intake, power button) faces the open bay.
- Cable notches are in the deck tiles of shelf v2.2 (no parts behind the shelf).

Module feet are slotted ribs: arches drop over the rods from above, teeth
between the rods lock front/back, tops of the teeth are flush with the rod tops.
Imports exports/deskshelf-v2.2/deskshelf_v2_2.f3d into a new document; the
shelf itself is not changed. Reference devices and the wall are translucent
boxes, not exported.
"""
import adsk.core
import adsk.fusion
import math
import os
import json

SHELF = "/Users/YOU/fusion-mcp/exports/deskshelf-v2.2/deskshelf_v2_2.f3d"
OUT = "/Users/YOU/fusion-mcp/exports/deskshelf-modules-v2"
YS = (-100, -50, 0, 50, 100)
RA = 10.2                     # rod arch radius (rod 20.0, socket fit as v2)
ZC = 105.0                    # rod centre height
ZTOP = 115.0                  # rod top = flush level of the teeth
ZBOT = 92.0                   # rib bottom; drawer rim is at 88
T = 3.0                       # rib / wall thickness
TB = 4.0                      # bookend upright (no gussets: they would hit the books)
# Right bay is x 342..536, left bay -536..-342. Monitor panel (700.9 mm) ends at
# x = +-350.5, so modules start at |x| >= 362.
SLOT_A = 19.0                 # MacBook Air M1, 16.1 mm max
DOCK_X0 = 534.0-2*T-SLOT_A    # dock against the end leg (face at 536)
BOOK_X0, BOOK_RIB2 = 362.0, 400.0
MINI, MINI_H = 127.0, 50.0    # Mac mini M4 127 x 127 x 50
MS_X0 = -533.0                # tall wall of the vertical stand, end-leg side
MS_Y0, MS_Y1 = -60.0, 67.0    # mini front / back (ports): 55 mm to the wall line
BACK_GAP_Y = 120.0            # devices end 2 mm before the shelf back (wall)


def run(context):
    app = adsk.core.Application.get()
    im = app.importManager
    for d in list(app.documents):
        if d.name.startswith("DeskShelf v2.2 + modules v2"):
            d.close(False)
    doc = im.importToNewDocument(im.createFusionArchiveImportOptions(SHELF))
    doc.name = "DeskShelf v2.2 + modules v2 - REVIEW"
    os.makedirs(OUT, exist_ok=True)
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    teal = des.appearances.addByCopy(lib.appearances.itemByName("Plastic - Matte (Gray)"), "Module - light")
    for prop in teal.appearanceProperties:
        color = adsk.core.ColorProperty.cast(prop)
        if color and prop.id in ("opaque_albedo", "generic_diffuse"):
            color.value = adsk.core.Color.create(120, 170, 165, 255)
    glass = next(a for a in lib.appearances if a.name.lower().startswith("glass"))
    ghost = des.appearances.addByCopy(glass, "Reference device")
    exports = []

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

    def arches(comp, x0, x1, name="Rod arches"):
        """Cut open-bottom arches for all five rods across x0..x1."""
        for y in YS:
            pts = [(y+RA, ZBOT-1), (y+RA, ZC)]
            pts += [(y+RA*math.cos(math.radians(a)), ZC+RA*math.sin(math.radians(a))) for a in range(4, 180, 4)]
            pts += [(y-RA, ZC), (y-RA, ZBOT-1)]
            prism(comp, "yz", pts, x0-0.5, x1+0.5, CUT, name)

    def finish(comp, name, appearance=teal, export=True):
        assert comp.bRepBodies.count == 1, (comp.name, comp.bRepBodies.count)
        body = comp.bRepBodies.item(0)
        assert body.isSolid
        body.name = name
        body.appearance = appearance
        if export:
            exports.append((body, name))
        return body

    def ref_box(name, x0, x1, y0, y1, z0, z1):
        occ, c = component("REF - " + name)
        box(c, x0, x1, y0, y1, z0, z1, NEW, name)
        finish(c, name, ghost, export=False)
        return occ

    # ---------------- laptop dock (right bay): MacBook Air only ----------------
    occ, c = component("laptop_dock")
    walls = [DOCK_X0, DOCK_X0+T+SLOT_A]
    x_end = walls[-1]+T
    wall = [(-100, ZBOT), (100, ZBOT), (100, 165), (96, 169), (64, 169), (60, 165), (60, 121),
            (-60, 121), (-60, 165), (-64, 169), (-96, 169), (-100, 165)]
    prism(c, "yz", wall, walls[0], walls[0]+T, NEW, "Dock wall 1")
    for y, w in ((-75, 3), (75, 3), (-25, 2), (25, 2)):
        box(c, walls[0], x_end, y-w, y+w, ZBOT, ZTOP, JOIN, "Tie bar between rods (stands on the bed)")
    prism(c, "yz", wall, walls[1], walls[1]+T, JOIN, "Dock wall 2")
    arches(c, walls[0], x_end)
    for xw, side in [(walls[0]+T, -1), (walls[1], 1)]:  # side = into material
        for ya, yb in ((-100, -60), (60, 100)):
            tri = [(xw-0.01*side, 169.1), (xw-0.01*side, 166), (xw+3*side, 169.1)]
            prism(c, "xz", tri, ya-1, yb+1, CUT, "Slot lead-in")
    finish(c, "laptop_dock")

    # ---------------- bookend (right bay, inner side), lower for small textbooks ----------------
    occ, c = component("bookend")
    up = [(-100, ZBOT), (100, ZBOT), (100, 121), (55, 121), (55, 205), (45, 215), (-45, 215), (-55, 205),
          (-55, 121), (-100, 121)]
    prism(c, "yz", up, BOOK_X0, BOOK_X0+TB, NEW, "Upright with rod rib")
    for y, w in ((-75, 3), (75, 3), (-25, 2), (25, 2)):
        box(c, BOOK_X0, BOOK_RIB2+T, y-w, y+w, ZBOT, ZTOP, JOIN, "Tie bar between rods (stands on the bed)")
    prism(c, "yz", [(-100, ZBOT), (100, ZBOT), (100, ZTOP), (-100, ZTOP)], BOOK_RIB2, BOOK_RIB2+T, JOIN, "Rib under books")
    arches(c, BOOK_X0, BOOK_RIB2+T)
    win = [(-32, 135), (32, 135), (32, 180), (24, 188), (-24, 188), (-32, 180)]
    prism(c, "yz", win, BOOK_X0-1, BOOK_X0+TB+1, CUT, "Lightening window")
    finish(c, "bookend")

    # ---------------- Mac mini M4 vertical stand (left bay) ----------------
    # Mini on its side: top face against the tall wall (end-leg side), underside with
    # the air intake and power button facing the open bay, ports toward the wall
    # with ~55 mm for plugs and cable bends behind them.
    occ, c = component("macmini_stand")
    xw0 = MS_X0
    xs0, xs1 = xw0+T, xw0+T+MINI_H+2
    tall = [(-100, ZBOT), (100, ZBOT), (100, 121), (MS_Y1+6, 121), (MS_Y1+6, 175), (MS_Y1-4, 185),
            (MS_Y0+4, 185), (MS_Y0-6, 175), (MS_Y0-6, 121), (-100, 121)]
    prism(c, "yz", tall, xw0, xw0+T, NEW, "Tall wall (mini top face side)")
    for y0, y1 in ((MS_Y0-5, MS_Y0-1), (-27, -23), (23, 27), (MS_Y1+1, MS_Y1+5)):
        box(c, xw0, xs1+T, y0, y1, ZBOT, ZTOP, JOIN, "Tie bar between rods (stands on the bed)")
    prism(c, "yz", [(-100, ZBOT), (100, ZBOT), (100, 125), (-100, 125)], xs1, xs1+T, JOIN, "Low rail (underside stays open)")
    box(c, xw0, xs0+8, MS_Y0-5, MS_Y0-1, ZBOT, 135, JOIN, "Front stop post")
    box(c, xs1-6, xs1+T, MS_Y0-5, MS_Y0-1, ZBOT, 121, JOIN, "Front stop, low")
    box(c, xw0, xs0+8, MS_Y1+1, MS_Y1+5, ZBOT, 135, JOIN, "Back stop post (ports stay clear)")
    arches(c, xw0, xs1+T)
    win = [(-35, 135), (40, 135), (40, 165), (32, 173), (-27, 173), (-35, 165)]
    prism(c, "yz", win, xw0-1, xw0+T+1, CUT, "Lightening window")
    finish(c, "macmini_stand")

    # ---------------- reference devices and the wall (not exported) ----------------
    refs = [ref_box("MacBook Air M1 304.1x212.4x16.1", walls[0]+T+1.4, walls[0]+T+1.4+16.1, BACK_GAP_Y-304.1, BACK_GAP_Y, ZTOP+0.1, ZTOP+0.1+212.4),
            ref_box("textbooks 170x220", BOOK_X0+TB+1, DOCK_X0-1, BACK_GAP_Y-170, BACK_GAP_Y, ZTOP+0.1, ZTOP+0.1+220),
            ref_box("Mac mini M4 on its side", xs0+1, xs0+1+MINI_H, MS_Y0, MS_Y1, ZTOP+0.1, ZTOP+0.1+MINI),
            ref_box("wall behind the shelf", -620, 620, 122.5, 140, 0, 450)]
    for occ in root.occurrences:
        c = occ.component
        if c.name in ("laptop_dock", "bookend", "macmini_stand") or c.name.startswith("REF - "):
            c.isConstructionFolderLightBulbOn = False
            for sk in c.sketches:
                sk.isVisible = False

    # ---------------- exports ----------------
    audit = []
    for body, name in exports:
        bb = body.boundingBox
        dims = [(getattr(bb.maxPoint, a)-getattr(bb.minPoint, a))*10 for a in "xyz"]
        opt = des.exportManager.createSTLExportOptions(body, OUT+"/"+name+".stl")
        opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        des.exportManager.execute(opt)
        audit.append({"part": name, "volume_cm3": round(body.volume, 2), "dimensions_mm": [round(v, 1) for v in dims]})

    # ---------------- checks on temporary copies ----------------
    tm = adsk.fusion.TemporaryBRepManager.get()
    items = []
    for occ in root.allOccurrences:
        if not occ.isVisible:
            continue
        for b in occ.bRepBodies:
            items.append((occ.component.name, tm.copy(b)))

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

    print("CTX", [(n, round(b.boundingBox.minPoint.x*10, 1), round(b.boundingBox.minPoint.z*10, 1)) for n, b in items if n.startswith(("drawer_", "leg_end_right"))])
    hits = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            v = inter(items[i][1], items[j][1])
            if v > 1e-3:
                hits.append([items[i][0], items[j][0], round(v, 3)])
    # Drawers pulled out to the stop must clear the modules.
    mods = [(n, b) for n, b in items if n in ("laptop_dock", "bookend", "macmini_stand")]
    drawer_hits = []
    for n, b in items:
        if not n.startswith("drawer_"):
            continue
        for travel in range(0, 150, 5):
            t = tm.copy(b)
            m = adsk.core.Matrix3D.create()
            m.translation = adsk.core.Vector3D.create(0, -travel/10, 0)
            tm.transform(t, m)
            for mn, mb in mods:
                v = inter(t, mb)
                if v > 1e-3:
                    drawer_hits.append([n, travel, mn, round(v, 3)])
    # Rod clearance under each module rib: lowest module point vs drawer rim.
    clear = {}
    for mn, mb in mods:
        clear[mn] = round(mb.boundingBox.minPoint.z*10-88.0, 2)
    report = {"interferences_all_visible_bodies": hits, "drawer_travel_vs_modules": drawer_hits,
              "module_bottom_above_drawer_rim_mm": clear, "parts": audit,
              "note": "Rigid CAD check. Reference boxes approximate devices; the wall is a box at y >= 122.5 (shelf back at 122). LG panel not modeled - modules keep |x| >= 362 vs panel edge 350.5."}
    with open(OUT+"/modules_check.json", "w") as f:
        json.dump(report, f, indent=2)
    des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT+"/deskshelf_v2_2_modules_v2.f3d"))

    for occ in root.occurrences:      # the wall is only for the check; it hides the views
        if occ.component.name == "REF - wall behind the shelf":
            occ.isLightBulbOn = False
    vp = app.activeViewport
    for fname, eye, target in [("preview_modules.png", (900, -1150, 800), (0, 0, 150)),
                               ("preview_right_side.png", (900, -700, 520), (450, 0, 160)),
                               ("preview_left_side.png", (-150, -750, 450), (-470, 0, 160)),
                               ("preview_top.png", (0, -1, 1500), (0, 0, 115))]:
        cam = vp.camera
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
        cam.target = p(*target)
        cam.eye = p(*eye)
        cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
        cam.isFitView = fname in ("preview_modules.png", "preview_top.png")
        cam.isSmoothTransition = False
        vp.camera = cam
        vp.refresh()
        vp.saveAsImageFile(OUT+"/"+fname, 1600, 1000)
    print(json.dumps(report, indent=1))
