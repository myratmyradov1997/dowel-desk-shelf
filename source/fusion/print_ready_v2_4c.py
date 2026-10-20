"""Write print-oriented copies of the v2.4 STLs to exports/deskshelf-v2.4/print
(run with plain python3). Rotations only (no mirroring); each part is dropped
to z=0 and centred on the 255 x 210 bed. Also checks the footprint with a 5 mm
brim on every side."""
import glob,json,os,struct
import numpy as np
OUT=os.path.expanduser('~/fusion-mcp/exports/deskshelf-v2.4c')
BED=(255.0,210.0,210.0);BRIM=5.0
# CAD x -> print up for faces at max x, -x up for faces at min x.
XUP=np.array([[0,0,-1],[0,1,0],[1,0,0]]);XDN=np.array([[0,0,1],[0,1,0],[-1,0,0]])
FLIP=np.array([[1,0,0],[0,-1,0],[0,0,-1]]);SIDE=np.array([[0,1,0],[0,0,1],[1,0,0]])
ROT={'leg_end_left':XUP,          # bay face (x=16) up
     'leg_inner_right':XUP,       # bay face (x=14) up
     'leg_end_right':XDN,         # bay face (x=0) up
     'leg_inner_left':XDN,
     'fit_coupon_slide_leg':XDN,  # channel face up
     'deck_tile_1':FLIP,'deck_tile_2':FLIP,'deck_tile_3':FLIP,   # skin on the bed
     'rod_clip':SIDE}             # flat side down
os.makedirs(OUT+'/print',exist_ok=True)
rep=[]
for fn in sorted(glob.glob(OUT+'/*.stl')):
    name=os.path.basename(fn)[:-4]
    d=open(fn,'rb').read();n=struct.unpack('<I',d[80:84])[0]
    a=np.frombuffer(d[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')])).copy()
    M=ROT.get(name,np.eye(3));assert round(np.linalg.det(M))==1
    v=a['v'].reshape(-1,3).astype(np.float64)@M.T
    lo,hi=v.min(0),v.max(0);dims=hi-lo
    if dims[1]>dims[0]:   # long side along the 255 mm axis
        v=v[:,[1,0,2]]*np.array([1,-1,1]);lo,hi=v.min(0),v.max(0);dims=hi-lo
    v-=np.array([(lo[0]+hi[0])/2-BED[0]/2,(lo[1]+hi[1])/2-BED[1]/2,lo[2]])
    a['v']=v.reshape(-1,9).astype(np.float32)
    nr=np.cross(v.reshape(-1,3,3)[:,1]-v.reshape(-1,3,3)[:,0],v.reshape(-1,3,3)[:,2]-v.reshape(-1,3,3)[:,0])
    nr/=np.maximum(np.linalg.norm(nr,axis=1,keepdims=True),1e-12);a['n']=nr.astype(np.float32)
    open(OUT+'/print/'+name+'.stl','wb').write(d[:84]+a.tobytes())
    ok=dims[0]<=BED[0] and dims[1]<=BED[1] and dims[2]<=BED[2]
    ok_brim=dims[0]+2*BRIM<=BED[0] and dims[1]+2*BRIM<=BED[1]
    rep.append(dict(part=name,print_dims_mm=[round(float(x),1) for x in dims],fits_bed=bool(ok),fits_with_5mm_brim=bool(ok_brim)))
json.dump(rep,open(OUT+'/print/print_orientation.json','w'),indent=2)
for r in rep:print(r)
