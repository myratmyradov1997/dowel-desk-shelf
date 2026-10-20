"""Print-oriented copies of the front-rod accessory STLs (plain python3, rotations only).
Cable clips and the left hub cap: x-min face on the bed (+x up: teardrops/throats point up, end wall down).
Right hub cap: x-max face (end wall) on the bed (-x up). Writes print/*.stl, print/plates.json, print/print_orientation.json."""
import json, os, struct
import numpy as np
D = os.path.expanduser('~/fusion-mcp/exports/acc-front-rod')
XUP = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])   # +x -> +z
XDN = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])   # -x -> +z
ROT = {'acc_cable_clip_1': XUP, 'acc_cable_clip_2': XUP, 'acc_cable_clip_3': XUP,
       'acc_hub_cap_left': XUP, 'acc_hub_cap_right': XDN}
os.makedirs(D + '/print', exist_ok=True)
rep = []
for name, M in ROT.items():
    assert round(np.linalg.det(M)) == 1
    d = open(f'{D}/{name}.stl', 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
    a = np.frombuffer(d[84:84+n*50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')])).copy()
    v = a['v'].reshape(-1, 3).astype(np.float64) @ M.T
    lo, hi = v.min(0), v.max(0)
    v -= np.array([(lo[0]+hi[0])/2-127.5, (lo[1]+hi[1])/2-105, lo[2]])
    a['v'] = v.reshape(-1, 9).astype(np.float32)
    t = v.reshape(-1, 3, 3); nr = np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0])
    nr /= np.maximum(np.linalg.norm(nr, axis=1, keepdims=True), 1e-12)
    a['n'] = nr.astype(np.float32)
    open(f'{D}/print/{name}.stl', 'wb').write(d[:84] + a.tobytes())
    # area of the first layer (faces lying on z=0, normal down)
    z0 = np.all(np.abs(t[:, :, 2] - 0) < 1e-3, axis=1) & (nr[:, 2] < -0.99)
    ar = 0.5*np.linalg.norm(np.cross(t[z0, 1]-t[z0, 0], t[z0, 2]-t[z0, 0]), axis=1).sum()
    rep.append(dict(part=name, print_dims_mm=[round(float(x), 1) for x in hi-lo], bed_contact_mm2=round(float(ar), 1)))
P = f'{D}/print/'
plates = {'acc_cable_clip_1': [P+'acc_cable_clip_1.stl'], 'acc_cable_clip_2': [P+'acc_cable_clip_2.stl'],
          'acc_cable_clip_3': [P+'acc_cable_clip_3.stl'],
          'acc_hub_caps_pair': [P+'acc_hub_cap_left.stl', P+'acc_hub_cap_right.stl']}
json.dump(plates, open(P+'plates.json', 'w'), indent=1)
json.dump(rep, open(P+'print_orientation.json', 'w'), indent=2)
print(json.dumps(rep, indent=1))
