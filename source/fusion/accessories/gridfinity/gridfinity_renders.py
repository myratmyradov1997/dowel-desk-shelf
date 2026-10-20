"""Renders of the Gridfinity inserts: drawers pulled out 145 mm on the shelf + isolated set."""
import adsk.core
import adsk.fusion
import os

SRC = "/Users/YOU/fusion-mcp/exports/acc-gridfinity/deskshelf_gridfinity.f3d"
OUT = "/Users/YOU/fusion-mcp/exports/acc-gridfinity"
TRAVEL = 145.0


def run(context):
    app = adsk.core.Application.get()
    for d in list(app.documents):
        if d.name.startswith("ACC gridfinity"):
            d.close(False)
    im = app.importManager
    doc = im.importToNewDocument(im.createFusionArchiveImportOptions(SRC))
    doc.name = "ACC gridfinity renders - REVIEW"
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    vp = app.activeViewport

    def p(x, y, z):
        return adsk.core.Point3D.create(x/10, y/10, z/10)

    for o in root.occurrences:
        n = o.component.name
        if n.startswith("REF - wall") or n.startswith("REF - tongue"):
            o.isLightBulbOn = False
    moved = []
    for o in root.occurrences:
        n = o.component.name
        if not o.isLightBulbOn:
            continue
        if n in ("drawer_left", "drawer_right") or n.startswith("gf_"):
            m = o.transform
            t = m.translation
            t.y -= TRAVEL/10
            m.translation = t
            o.transform = m
            moved.append(n)
    try:
        des.snapshots.add()
    except Exception:
        pass

    def shot(fname, eye, target, ext=None, fit=False):
        cam = vp.camera
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
        cam.target = p(*target)
        cam.eye = p(*eye)
        cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
        cam.isSmoothTransition = False
        cam.isFitView = fit
        if ext and not fit:
            cam.viewExtents = ext
        vp.camera = cam
        if fit:
            vp.fit()
        vp.refresh()
        vp.saveAsImageFile(OUT + "/" + fname, 1600, 1000)

    shot("_warmup.png", (1000, -900, 520), (440, -150, 60), 45.0)
    shot("view_right_drawer_out_145.png", (980, -760, 480), (440, -150, 60), 45.0)
    shot("view_left_drawer_out_145.png", (-980, -760, 480), (-440, -150, 60), 45.0)
    shot("view_shelf_both_out.png", (700, -1500, 700), (0, -60, 80), 120.0)
    hidden = []
    for o in root.occurrences:
        if o.isLightBulbOn and not o.component.name.startswith("gf_"):
            o.isLightBulbOn = False
            hidden.append(o)
    # isolated: right-drawer set (2 plate halves + bins) in place
    left = []
    for o in root.occurrences:
        if o.isLightBulbOn and o.boundingBox.minPoint.x < 0:
            o.isLightBulbOn = False
            left.append(o)
    shot("view_isolated_right_set.png", (750, -650, 320), (439, -150, 40), None, True)
    # isolated: plate halves only (bins hidden)
    bins = [o for o in root.occurrences if o.isLightBulbOn and o.component.name.startswith("gf_bin")]
    for o in bins:
        o.isLightBulbOn = False
    shot("view_isolated_right_plates.png", (700, -620, 520), (439, -150, 30), None, True)
    # isolated: bins only, from behind and below (feet, label tabs on the front walls)
    plates_ = [o for o in root.occurrences if o.isLightBulbOn and o.component.name.startswith("gf_plate")]
    for o in bins:
        o.isLightBulbOn = True
    for o in plates_:
        o.isLightBulbOn = False
    shot("view_isolated_right_bins_below.png", (250, 250, -160), (439, -150, 50), None, True)
    shot("view_isolated_right_bins_back.png", (300, 300, 330), (439, -150, 50), None, True)
    for o in plates_:
        o.isLightBulbOn = True
    for o in left:
        o.isLightBulbOn = True
    for o in hidden:
        o.isLightBulbOn = True
    try:
        os.remove(OUT + "/_warmup.png")
    except OSError:
        pass
    print("moved", moved)
