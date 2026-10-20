"""Print-oriented copies of the module STLs (all print as modelled, z up)."""
import glob,os,struct,json
import numpy as np
OUT=os.path.expanduser('~/fusion-mcp/exports/deskshelf-modules-v2')
BED=(255.0,210.0)
os.makedirs(OUT+'/print',exist_ok=True)
rep=[]
for fn in sorted(glob.glob(OUT+'/*.stl')):
    name=os.path.basename(fn)[:-4]
    d=open(fn,'rb').read();n=struct.unpack('<I',d[80:84])[0]
    a=np.frombuffer(d[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')])).copy()
    v=a['v'].reshape(-1,3).astype(np.float64)
    lo,hi=v.min(0),v.max(0);dims=hi-lo
    if dims[1]>dims[0]:
        v=v[:,[1,0,2]]*np.array([1,-1,1]);lo,hi=v.min(0),v.max(0);dims=hi-lo
    v-=np.array([(lo[0]+hi[0])/2-BED[0]/2,(lo[1]+hi[1])/2-BED[1]/2,lo[2]])
    a['v']=v.reshape(-1,9).astype(np.float32)
    t=v.reshape(-1,3,3);nr=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nr/=np.maximum(np.linalg.norm(nr,axis=1,keepdims=True),1e-12)
    a['n']=nr.astype(np.float32)
    open(OUT+'/print/'+name+'.stl','wb').write(d[:84]+a.tobytes())
    q=np.round(v,4);u,inv=np.unique(q,axis=0,return_inverse=True);tri=inv.reshape(-1,3)
    e=np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1);_,cnt=np.unique(e,axis=0,return_counts=True)
    rep.append(dict(part=name,print_dims_mm=[round(float(x),1) for x in dims],watertight=bool((cnt==2).all()),
                    fits_with_5mm_brim=bool(dims[0]+10<=BED[0] and dims[1]+10<=BED[1] and dims[2]<=210)))
json.dump(rep,open(OUT+'/print/print_orientation.json','w'),indent=2)
for r in rep:print(r)
