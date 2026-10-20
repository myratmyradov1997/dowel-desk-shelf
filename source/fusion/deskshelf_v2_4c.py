"""Five-rod desk shelf v2.4c (2026-10-19): as v2.4b + FIX of the drawer stop tongue. Since v2 the three
"Stop tongue slot" cuts went only 0.5 mm into the 2.0 mm side wall (found by the Gridfinity agent), so the
tongue was not cut free and the stop nub could not spring in: the drawer would not go in past the leg.
Slots now cut through the whole wall; checked by point containment after the build.

Five-rod desk shelf v2.4b (2026-10-19): as v2.4, but the inner-leg socket on the middle rod (y = 0)
is D20.4 instead of D20.2 - only rods 1 and 5 (clamped) and the thin rods 2/4 are close fits, so the
leg does not jam while it is slid 200-330 mm along five bent rods (user agreed).

Five-rod desk shelf v2.4 (2026-10-19): v2.3 with sockets fitted to the real rods.
Real rods: three ~20.0-20.1 (fit the printed D20.2 ring well), two ~19.0. Rods 1/3/5 (y = -100, 0, 100;
clamps on 1 and 5) are the good ones, the thin rods go to positions 2 and 4 (y = -50, 50).
Inner legs (not printed yet): sockets D20.2 at y = -100/0/100, D19.3 at y = -50/50 (no test print, user's
choice). End legs are already printed with D20.4 (unchanged here). rod_clip bore 20.2 -> 19.8 (it slid).
If the 'balka' document is not open, the wooden rod is rebuilt as the identical D20 x 1100 cylinder.

Five-rod desk shelf v2.3 (ABS): channel clearance B from the two-sided coupon test,
stiffer drawers (2.0 mm walls/floor, inner rim beams on the sides; left drawer also has a bonded-in divider).
Based on v2.2: hanging drawers in V-channels cut into the legs.

v2.2 (2026-10-15): the shelf stands against a wall. Deck tiles get cable
notches (8 / 12 / 16 mm) in the back edge so monitor cables drop down behind
the back rod; nothing protrudes behind y = 122. Otherwise as v2.1.

v2.1 (2026-10-15): drawer 10 mm narrower (190 body, 198 with flanges) so it
fits the 210 mm bed with a 5 mm brim; inner legs move 10 mm outward, side bays
194 mm, clear centre 656 mm. Everything else as v2.

Changes from v1 (see exports/deskshelf-v2/README.txt):
- No separate drawer rails. Each leg carries a V-channel on its bay face;
  the drawer hangs by two top-rim flanges (45 deg underside, printable without
  supports). The channel is closed at the back (push-in stop) and has a
  retainer above the flange (anti-tip when the drawer is pulled out).
- Pull-out stop: snap tongue with a nub on the end-leg side of each drawer;
  the nub stops at the front edge of the leg window. Press the nub through
  the window to remove the drawer.
- New parametric drawer 200 x 224 x 62 body (208 with flanges, fits 210 bed).
- Clamp slit 1.2 -> 2.4 mm (grips rods 19.6..20.4), M3 nut pockets, bolt
  raised so the head clears the leg top.
- Rod clips (deck end stop + cable hook), bay spacing gauge, fit coupons.

Concept credit: GoCartDad DadWel System, Printables 1693920 (CC BY-NC-SA 4.0).
v2 contains no mesh geometry from that model. No load rating implied.
"""
import adsk.core
import adsk.fusion
import math
import os
import json

OUT = "/Users/YOU/fusion-mcp/exports/deskshelf-v2.4c"
YS = (-100, -50, 0, 50, 100)
R = 10.2
SOCK_INNER = {-100: 10.1, -50: 9.65, 0: 10.2, 50: 9.65, 100: 10.1}   # v2.4 inner-leg socket radii
CLIP_RI = 9.9                              # v2.4 rod_clip bore D19.8
R_SADDLE = 10.5                            # deck saddles D21: tile rests on the rod crown, any rod 19.8..21 fits

# Drawer / channel parameters (mm, global coordinates)
DR_W, DR_D, DR_H = 190.0, 224.0, 62.0      # drawer body
DR_WALL, DR_FLOOR = 2.0, 2.0                # v2.2: 1.6 / 1.6 (too soft, user test)
DR_Z0 = 26.0                               # drawer bottom above desk
DR_Y0 = -115.0                             # drawer front = leg front
GAP = 2.0                                  # drawer wall to leg face
FL = 4.0                                   # flange protrusion
FL_TIP = 1.5                               # flange tip height
TOP = DR_Z0 + DR_H                         # rim top, 88
CH_DEPTH = 2.8                             # channel depth into the leg (coupon B; v2.2 3.5)
CH_RET = 0.5                               # retainer clearance above rim (coupon B; v2.2 0.8)
CH_END = DR_Y0 + DR_D + 0.5                # closed back end of channel
V0 = TOP - FL_TIP - (FL - GAP) - 0.1       # V-line z at leg face (0.1 CAD gap)
WIN_Y = 88.0                               # leg window half-width (stop edge)
NUB_Y = 172.0                              # nub stop face, from drawer front
STOP_TRAVEL = NUB_Y + DR_Y0 + WIN_Y        # 145 mm
BAY = DR_W + 2*GAP                         # side bay clear width, 194
RIM_W, RIM_H = 6.0, 6.0                    # inner rim beam: width, vertical part (+45 deg chamfer below)
DIV_Y, DIV_T = 140.0, 2.0                  # left-drawer divider: front compartment = full pull-out
X_IN_L = -536 + BAY                        # inner-left leg, bay face
X_IN_R = 536 - BAY                         # inner-right leg, bay face


def run(context):
    app = adsk.core.Application.get()
    source = None
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name.lower().startswith("balka"):
            sd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
            source = sd.rootComponent.bRepBodies.item(0)
            break
    os.makedirs(OUT, exist_ok=True)
    for d in [d for d in app.documents if d.name.startswith("DeskShelf v2.4c")]:
        d.close(False)                      # earlier run of this generator
    tm = adsk.fusion.TemporaryBRepManager.get()
    if source:
        wood_template = tm.copy(source)
        rotate = adsk.core.Matrix3D.create()
        rotate.setToRotation(math.pi/2, adsk.core.Vector3D.create(0,1,0), adsk.core.Point3D.create(0,0,0))
        tm.transform(wood_template, rotate)
    else:
        wood_template = tm.createCylinderOrCone(adsk.core.Point3D.create(0,0,0), 1.0, adsk.core.Point3D.create(110,0,0), 1.0)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    doc.name = "DeskShelf v2.4c - drawer stop fixed - REVIEW"
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    dark = des.appearances.addByCopy(lib.appearances.itemByName("Plastic - Matte (Black)"), "Frame - graphite")
    gray = des.appearances.addByCopy(lib.appearances.itemByName("Plastic - Matte (Gray)"), "Deck - gray")
    warm = des.appearances.addByCopy(lib.appearances.itemByName("Plastic - Matte (Yellow)"), "Wood - warm placeholder")
    for prop in warm.appearanceProperties:
        color = adsk.core.ColorProperty.cast(prop)
        if color and prop.id in ("opaque_albedo", "generic_diffuse"):
            color.value = adsk.core.Color.create(181, 133, 78, 255)
    exports = []
    components = []

    def p(x,y,z):
        return adsk.core.Point3D.create(x/10,y/10,z/10)

    def move(x=0,y=0,z=0):
        m=adsk.core.Matrix3D.create()
        m.translation=adsk.core.Vector3D.create(x/10,y/10,z/10)
        return m

    def component(name,x=0,y=0,z=0):
        occ=root.occurrences.addNewComponent(move(x,y,z))
        comp=occ.component
        comp.name=name
        components.append((occ,comp))
        return occ,comp

    def plane(comp,kind,offset=0):
        base={"xy":comp.xYConstructionPlane,"yz":comp.yZConstructionPlane,"xz":comp.xZConstructionPlane}[kind]
        if not offset:return base
        inp=comp.constructionPlanes.createInput()
        inp.setByOffset(base,adsk.core.ValueInput.createByString("%g mm"%offset))
        result=comp.constructionPlanes.add(inp)
        result.isLightBulbOn=False
        return result

    def poly(comp,pl,coords,name):
        sk=comp.sketches.add(pl)
        sk.name=name
        pts=[sk.modelToSketchSpace(p(*q)) for q in coords]
        for i,q in enumerate(pts):sk.sketchCurves.sketchLines.addByTwoPoints(q,pts[(i+1)%len(pts)])
        assert sk.profiles.count==1,(name,sk.profiles.count)
        return sk

    def ext(comp,sk,length,op,name):
        inp=comp.features.extrudeFeatures.createInput(sk.profiles.item(0),op)
        if op!=NEW:
            inp.participantBodies=[comp.bRepBodies.item(0)]
        inp.setDistanceExtent(False,adsk.core.ValueInput.createByString("%g mm"%length))
        f=comp.features.extrudeFeatures.add(inp)
        f.name=name
        sk.isVisible=False
        return f

    def box(comp,x0,x1,y0,y1,z0,z1,op=NEW,name="Box"):
        sk=poly(comp,plane(comp,"xy",z0),[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],name)
        return ext(comp,sk,z1-z0,op,name)

    AXIS={"xy":2,"yz":0,"xz":1}

    def prism(comp,kind,pts2,a0,a1,op,name):
        """Extrude a 2D profile along the plane normal axis from a0 to a1 (mm).
        Works regardless of the construction-plane normal sign."""
        base={"xy":comp.xYConstructionPlane,"yz":comp.yZConstructionPlane,"xz":comp.xZConstructionPlane}[kind]
        n=base.geometry.normal
        sgn=[n.x,n.y,n.z][AXIS[kind]]
        assert abs(abs(sgn)-1)<1e-9,(kind,sgn)
        at=a0 if sgn>0 else a1
        pl=plane(comp,kind,at*sgn)
        def to3(u,v):
            if kind=="xz":return (u,at,v)
            if kind=="yz":return (at,u,v)
            return (u,v,at)
        sk=poly(comp,pl,[to3(u,v) for u,v in pts2],name)
        return ext(comp,sk,a1-a0,op,name)

    def hole_x(comp,x,y,z,r,length,name):
        sk=comp.sketches.add(plane(comp,"yz",x))
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(x,y,z)),r/10)
        return ext(comp,sk,length,CUT,name)

    def finish(comp,filename,appearance=dark,export=True):
        assert comp.bRepBodies.count==1,(comp.name,comp.bRepBodies.count)
        body=comp.bRepBodies.item(0)
        assert body.isSolid
        body.name=filename
        body.appearance=appearance
        if export:exports.append((body,filename))
        return body

    # Original balka geometry, copied without changing the source document.
    bar_occ,bar=component("WOOD - balka D20 L1100",-550,YS[0],105)
    bf=bar.features.baseFeatures.add()
    bf.startEdit()
    b=bar.bRepBodies.add(wood_template,bf)
    bf.finishEdit()
    b=bar.bRepBodies.item(0)
    b.name="balka - original geometry"
    b.appearance=warm
    for face in b.faces:face.appearance=warm
    for y in YS[1:]:root.occurrences.addExistingComponent(bar,move(-550,y,105))

    # Four legs. face = local x of the bay (drawer) face; sgn points into the leg.
    leg_specs=[("leg_end_left",-552,16,"left",16,-1),("leg_inner_left",X_IN_L,14,"inner-left",0,1),
               ("leg_inner_right",X_IN_R-14,14,"inner-right",14,-1),("leg_end_right",536,16,"right",0,1)]
    for name,x,thick,kind,face,sgn in leg_specs:
        occ,c=component(name,x)
        outline=[(0,-122,0),(0,122,0),(0,122,8),(0,115,8),
                 (0,115,110),(0,105,120),(0,-105,120),(0,-115,110),
                 (0,-115,8),(0,-122,8)]
        sk=poly(c,c.yZConstructionPlane,outline,"Faceted frame profile - 244 x 120")
        ext(c,sk,thick,NEW,"Frame thickness")
        # Window top lowered from 88 to 74 so a solid band carries the drawer channel.
        # Its front vertical edge (y=-88) is the drawer pull-out stop.
        W=WIN_Y
        window=[(-1,-W,10),(-1,W,10),(-1,W,64),(-1,W-10,74),(-1,-(W-10),74),(-1,-W,64)]
        sk=poly(c,plane(c,"yz",-1),window,"Window - front edge is drawer stop")
        ext(c,sk,thick+2,CUT,"Open frame")
        for y in YS:
            start,length=(2,thick-1) if kind=="left" else (-1,thick-1) if kind=="right" else (-1,thick+2)
            r_s=SOCK_INNER[y] if kind.startswith("inner") else R
            hole_x(c,start,y,105,r_s,length,"Rod socket D%.1f"%(2*r_s))
        # Pinch clamps on the front and back rods.
        for y in (-100,100):
            box(c,0,thick,y-9,y+9,115,128,JOIN,"Pinch clamp ears")
            box(c,-0.1,thick+0.1,y-1.2,y+1.2,114,128.2,CUT,"Pinch clamp split 2.4 mm")
        sk=c.sketches.add(c.xZConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(thick/2,0,123)),.17)
        inp=c.features.extrudeFeatures.createInput(sk.profiles.item(0),CUT)
        inp.participantBodies=[c.bRepBodies.item(0)]
        inp.setSymmetricExtent(adsk.core.ValueInput.createByString("260 mm"),True)
        f=c.features.extrudeFeatures.add(inp);f.name="M3 clamp through holes";sk.isVisible=False
        hexr=5.8/math.sqrt(3)
        hexpts=[(thick/2+hexr*math.cos(math.radians(a)),123+hexr*math.sin(math.radians(a))) for a in range(0,360,60)]
        prism(c,"xz",hexpts,106.4,109.5,CUT,"M3 nut pocket - back ear")
        prism(c,"xz",hexpts,-109.5,-106.4,CUT,"M3 nut pocket - front ear")
        # Drawer V-channel on the bay face: 45 deg support, retainer above, closed at back.
        X=lambda s:face+sgn*s
        ch=[(X(-0.5),V0-0.5),(X(CH_DEPTH),V0+CH_DEPTH),(X(CH_DEPTH),TOP+CH_RET),(X(-0.5),TOP+CH_RET)]
        prism(c,"xz",ch,-116,CH_END,CUT,"Drawer V-channel")
        lead=[(X(-0.5),TOP+CH_RET-0.1),(X(CH_DEPTH),TOP+CH_RET-0.1),(X(CH_DEPTH),TOP+CH_RET+1.5),(X(-0.5),TOP+CH_RET+1.5)]
        prism(c,"xz",lead,-116,-109,CUT,"Channel entry lead-in")
        finish(c,name)

    # Three deck tiles, each 180 x 244 mm (unchanged from v1).
    for j,cx in enumerate((-180,0,180),1):
        occ,c=component("deck_tile_%d"%j,cx,0,0)
        box(c,-90,90,-122,122,115.1,118.1,name="Flat deck skin 3 mm")
        for sx in (-78,78):
            for y in YS:
                box(c,sx-3,sx+3,y-13,y+13,105,115.3,JOIN,"Short saddle")
        for y in YS:hole_x(c,-91,y,105,R_SADDLE,182,"Half-round saddle D21 (tolerant to rod size)")
        for cy in (-75,75):
            if j<3:
                coords=[(89.5,cy-10,115.1),(96,cy-14,115.1),(96,cy+14,115.1),(89.5,cy+10,115.1)]
                sk=poly(c,plane(c,"xy",115.1),coords,"Dovetail tile key")
                ext(c,sk,3,JOIN,"Integral tile key")
            if j>1:
                coords=[(-90.2,cy-10.4,114.9),(-83.7,cy-14.4,114.9),(-83.7,cy+14.4,114.9),(-90.2,cy+10.4,114.9)]
                sk=poly(c,plane(c,"xy",114.9),coords,"Dovetail socket - clearance")
                ext(c,sk,3.4,CUT,"Tile key socket")
        for y in (-118,118):
            box(c,-82,82,y-0.55,y+0.55,117.65,118.2,CUT,"Edge graphic - shallow groove")
        # Cable notches in the back edge (wall side), clear of the saddles (y <= 113).
        for nx,w in ((-40,8.0),(0,12.0),(40,16.0)):
            box(c,nx-w/2,nx+w/2,114.0,122.2,114.9,118.3,CUT,"Cable notch %g mm"%w)
        finish(c,"deck_tile_%d"%j,gray)

    # Parametric hanging drawers. Local origin: body front-left-bottom corner.
    def drawer(name,x0,stop_side,divider=False):
        occ,c=component(name,x0,DR_Y0,DR_Z0)
        box(c,0,DR_W,0,DR_D,0,DR_H,NEW,"Drawer body")
        box(c,DR_WALL,DR_W-DR_WALL,DR_WALL,DR_D-DR_WALL,DR_FLOOR,DR_H+1,CUT,"Drawer cavity")
        zc=DR_H-FL_TIP-FL
        prism(c,"xz",[(0.8,zc),(0.8,DR_H),(-FL,DR_H),(-FL,DR_H-FL_TIP),(0,zc)],0,DR_D,JOIN,"Hanging flange left - 45 deg underside")
        prism(c,"xz",[(DR_W-0.8,zc),(DR_W-0.8,DR_H),(DR_W+FL,DR_H),(DR_W+FL,DR_H-FL_TIP),(DR_W,zc)],0,DR_D,JOIN,"Hanging flange right - 45 deg underside")
        # Inner rim beam (v2.3): the 45 deg channel pushes each flange inward with about the
        # hanging load; a stiff horizontal rim carries it to the front/back walls instead of
        # bending the thin side wall. 45 deg underside -> prints without supports.
        w,o=DR_WALL,0.2
        lo=DR_H-RIM_H
        side=lambda a,s:[(a(w-o),DR_H),(a(w+RIM_W),DR_H),(a(w+RIM_W),lo),(a(w-o),lo-RIM_W-o)]
        prism(c,"xz",side(lambda v:v,1),w-o,DR_D-w+o,JOIN,"Rim beam left")
        prism(c,"xz",side(lambda v:DR_W-v,-1),w-o,DR_D-w+o,JOIN,"Rim beam right")
        # No front/back rims: those walls take the rim reactions in their own plane.
        if divider:
            box(c,w-o,DR_W-w+o,DIV_Y-DIV_T/2,DIV_Y+DIV_T/2,DR_FLOOR-o,DR_H,JOIN,"Divider - ties the side walls, front compartment = full pull-out")
        # Finger scoop in the front wall: room for fingers under the front rod.
        a0=math.degrees(math.asin((DR_H+1-73)/35.0))
        arc=[(DR_W/2+35*math.cos(math.radians(t)),73+35*math.sin(math.radians(t)))
             for t in [180-a0+(360+2*a0-180)*k/24.0 for k in range(25)]]
        prism(c,"xz",arc,-0.5,DR_WALL+0.5,CUT,"Finger scoop")
        # Snap stop: tongue cut free in the side wall, nub stops at the leg window edge.
        X=(lambda s:-s) if stop_side<0 else (lambda s:DR_W+s)
        xa,xb=sorted((X(-(DR_WALL+0.5)),X(0.5)))
        box(c,xa,xb,150,193,26,27,CUT,"Stop tongue slot - top")
        box(c,xa,xb,150,193,7,8,CUT,"Stop tongue slot - bottom")
        box(c,xa,xb,192,193,7,27,CUT,"Stop tongue slot - free end")
        prism(c,"xz",[(X(-0.6),10),(X(0),10),(X(4.5),14.5),(X(4.5),24),(X(-0.6),24)],NUB_Y,186,JOIN,"Stop nub - chamfered underside")
        prism(c,"xy",[(X(0.3),186.5),(X(4.8),174),(X(4.8),186.5)],9,25,CUT,"Stop nub insertion ramp")
        body=finish(c,name,dark)
        wx=X(-DR_WALL/2)
        for yy,zz in ((171.0,26.5),(171.0,7.5),(192.5,17.0)):
            pc=body.pointContainment(p(wx,yy,zz))
            assert pc==adsk.fusion.PointContainment.PointOutsidePointContainment,("tongue slot not through",name,yy,zz,pc)
        assert body.pointContainment(p(wx,171.0,17.0))==adsk.fusion.PointContainment.PointInsidePointContainment,("tongue missing",name)
        return occ
    drawer("drawer_left",-536+GAP,-1,divider=True)
    drawer("drawer_right",X_IN_R+GAP,1)

    # Rod clip: deck end stop on the back rod plus a cable hook. Print on its side.
    occ,c=component("rod_clip",270.5)
    yc,zc,ri,ro,half=100.0,105.0,CLIP_RI,CLIP_RI+2.5,60.0
    angs=[half+(360-2*half)*k/30.0 for k in range(31)]
    ring=[(yc+ro*math.cos(math.radians(a)),zc+ro*math.sin(math.radians(a))) for a in angs]
    ring+=[(yc+ri*math.cos(math.radians(a)),zc+ri*math.sin(math.radians(a))) for a in reversed(angs)]
    prism(c,"yz",ring,0,10,NEW,"Snap ring D%.1f, opens to the back"%(2*CLIP_RI))
    prism(c,"yz",[(yc-1.5,zc-ri-1),(yc+1.5,zc-ri-1),(yc+1.5,zc-34),(yc-1.5,zc-34)],0,10,JOIN,"Hook stem")
    prism(c,"yz",[(yc-1.5,zc-34),(yc+12,zc-34),(yc+12,zc-31),(yc-1.5,zc-31)],0,10,JOIN,"Hook base")
    prism(c,"yz",[(yc+9,zc-31.5),(yc+12,zc-31.5),(yc+12,zc-25),(yc+9,zc-25)],0,10,JOIN,"Hook lip")
    finish(c,"rod_clip",gray)
    root.occurrences.addExistingComponent(c,move(-280.5,0,0))

    # Print-only helpers, hidden in the assembly view.
    hidden=[]
    occ,c=component("bay_gauge",-536,-300,0);hidden.append(occ)
    box(c,0,BAY,0,12,0,8,NEW,"Bay spacing gauge %.1f mm"%BAY)
    finish(c,"bay_gauge",gray)
    occ,c=component("fit_coupon_sockets",-150,-320,0);hidden.append(occ)
    box(c,0,84,0,30,0,14,NEW,"Socket test plate")
    for k,d in enumerate((20.2,20.4,20.6)):
        cx=15+27*k
        sk=c.sketches.add(c.xYConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(p(cx,15,0)),d/20)
        ext(c,sk,14,CUT,"Test socket D%.1f"%d)
        for m in range(k+1):
            box(c,cx-3+3*m-0.5,cx-3+3*m+0.5,28.5,30.1,12.5,14.1,CUT,"Size mark")
    finish(c,"fit_coupon_sockets",gray)
    occ,c=component("fit_coupon_slide_leg",0,-320,0);hidden.append(occ)
    box(c,0,12,0,40,72,96,NEW,"Leg channel sample")
    ch=[(-0.5,V0-0.5),(CH_DEPTH,V0+CH_DEPTH),(CH_DEPTH,TOP+CH_RET),(-0.5,TOP+CH_RET)]
    prism(c,"xz",ch,-1,41,CUT,"Drawer V-channel sample")
    finish(c,"fit_coupon_slide_leg",gray)
    occ,c=component("fit_coupon_slide_drawer",0,-320,0);hidden.append(occ)
    w0,w1=-GAP-DR_WALL,-GAP
    box(c,w0-10,w1,0,40,TOP-24,TOP-24+DR_FLOOR,NEW,"Floor strip")
    box(c,w0,w1,0,40,TOP-24,TOP,JOIN,"Wall strip")
    zc2=TOP-FL_TIP-FL
    prism(c,"xz",[(w1-0.8,zc2),(w1-0.8,TOP),(w1+FL,TOP),(w1+FL,TOP-FL_TIP),(w1,zc2)],0,40,JOIN,"Flange sample")
    finish(c,"fit_coupon_slide_drawer",gray)
    for occ in hidden:occ.isLightBulbOn=False

    for occ,c in components:
        c.isConstructionFolderLightBulbOn=False
        for sk in c.sketches:sk.isVisible=False
    assert bar.bRepBodies.count==1,"Cuts must never alter the wooden rod component"
    wb=bar.bRepBodies.item(0)
    assert abs(wb.volume-345.5751918948624)<0.001,"Original wooden rod volume changed"
    audit=[]
    for body,name in exports:
        bb=body.boundingBox
        dims=[(getattr(bb.maxPoint,a)-getattr(bb.minPoint,a))*10 for a in "xyz"]
        assert body.isSolid and body.volume>0
        opt=des.exportManager.createSTLExportOptions(body,OUT+"/"+name+".stl")
        opt.meshRefinement=adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        des.exportManager.execute(opt)
        audit.append({"part":name,"volume_cm3":body.volume,"dimensions_mm":dims})
    with open(OUT+"/cad_audit.json","w") as stream:json.dump(audit,stream,indent=2)
    # Interference of the visible assembly only.
    col=adsk.core.ObjectCollection.create()
    for occ in root.occurrences:
        if occ.isLightBulbOn:col.add(occ)
    inp=des.createInterferenceInput(col)
    inp.areCoincidentFacesIncluded=False
    res=des.analyzeInterference(inp)
    hits=[[r.entityOne.name,r.entityTwo.name,r.interferenceBody.volume] for r in res] if res else []
    with open(OUT+"/assembly_check.json","w") as f:
        json.dump({"components_checked":col.count,"interferences":hits,
                   "wood_volume_cm3":wb.volume},f,indent=2)
    des.exportManager.execute(des.exportManager.createFusionArchiveExportOptions(OUT+"/deskshelf_v2_4c.f3d"))
    des.exportManager.execute(des.exportManager.createSTEPExportOptions(OUT+"/deskshelf_v2_4c_solids.step"))
    cam=app.activeViewport.camera
    cam.cameraType=adsk.core.CameraTypes.OrthographicCameraType
    cam.target=p(0,0,60)
    cam.eye=p(850,-1100,760)
    cam.upVector=adsk.core.Vector3D.create(0,0,1)
    cam.isFitView=True
    cam.isSmoothTransition=False
    app.activeViewport.camera=cam
    app.activeViewport.refresh()
    app.activeViewport.saveAsImageFile(OUT+"/preview_closed.png",1600,1000)
    print("COMPONENTS",root.occurrences.count,"EXPORTED",len(exports))
    print("INTERFERENCES",hits)
    print("STOP_TRAVEL_MM",STOP_TRAVEL,"V0",V0,"BAY",BAY,"CENTER",X_IN_R-14-(X_IN_L+14))
    for a in audit:print(a["part"],[round(v,1) for v in a["dimensions_mm"]],round(a["volume_cm3"],1))
