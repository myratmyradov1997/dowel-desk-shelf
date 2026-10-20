"""Print-oriented copies of the MagSafe v3 STLs (plain python3): mount face down, screw head down, nut flat."""
import json,os,struct
import numpy as np
D=os.path.expanduser('~/fusion-mcp/exports/magsafe-mount-v3')
RX90=np.array([[1,0,0],[0,0,-1],[0,1,0]])   # y -> z: cup front (min y) on the bed
def load(fn):
    d=open(fn,'rb').read();n=struct.unpack('<I',d[80:84])[0]
    return d,np.frombuffer(d[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')])).copy()
rep=[]
for name in ('magsafe_mount_v3','magsafe_v3_screw','magsafe_v3_nut'):
    d,a=load(f'{D}/{name}.stl');v=a['v'].reshape(-1,3).astype(np.float64)
    if name=='magsafe_mount_v3':v=v@RX90.T
    if name=='magsafe_v3_screw':
        lo,hi=v[:,2].min(),v[:,2].max();r=np.hypot(v[:,0]-v[:,0].mean(),v[:,1]-v[:,1].mean())
        if r[v[:,2]>hi-4].max()>r[v[:,2]<lo+4].max():v[:,2]*=-1;v[:,1]*=-1   # head must be at the bottom
    lo,hi=v.min(0),v.max(0)
    v-=np.array([(lo[0]+hi[0])/2-127.5,(lo[1]+hi[1])/2-105,lo[2]])
    a['v']=v.reshape(-1,9).astype(np.float32)
    t=v.reshape(-1,3,3);nr=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nr/=np.maximum(np.linalg.norm(nr,axis=1,keepdims=True),1e-12)
    a['n']=nr.astype(np.float32)
    open(f'{D}/print/{name}.stl','wb').write(d[:84]+a.tobytes())
    rep.append(dict(part=name,print_dims_mm=[round(float(x),1) for x in hi-lo]))
json.dump(rep,open(f'{D}/print/print_orientation.json','w'),indent=2);print(rep)
